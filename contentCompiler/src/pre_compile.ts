import * as fs from "fs";
import path from "path";
import { exec } from "child_process";
import { simpleGit } from "simple-git";
import { Probot, Context } from "probot";
import { getInstallationToken, configureGit, deleteFolderRecursiveSync } from "./helpers.js";


export const preCompile = async (app: Probot, context: Context<'pull_request'>) => {
    const gitAppName = process.env.GITHUB_APP_NAME || '';
    const gitAppEmail = process.env.GITHUB_APP_EMAIL || '';

    const payload = context.payload;
    const prNumber = payload.number;
    const repoOwner = payload.repository.owner.login;
    const repoName = payload.repository.name;
    const repoUrl = payload.repository.clone_url;  

    const clonedRepoFolder = process.env.CLONE_REPO_FOLDER || 'src/cloned_repo';
    const tempStorageFolder = process.env.TEMP_STORAGE_FOLDER || 'src/temp_storage';

    const __dirname = process.cwd();
    const cloneTargetDirectory = path.join(__dirname, clonedRepoFolder);
    const tempStorageDirectory = path.join(__dirname, tempStorageFolder);

    context.log.info(`Pull request ${prNumber} opened for ${repoOwner}/${repoName}`);
    context.log.info('Base branch: ', payload.pull_request.base.ref);
    context.log.info('Head branch: ', payload.pull_request.head.ref);

    // Get the installation token
    const token = await getInstallationToken(app, context);

    // Configure git with token
    const remoteUrl = `https://x-access-token:${token}@github.com/${repoOwner}/${repoName}.git`;
    let git = simpleGit();
    await configureGit(git, gitAppName, gitAppEmail);

    const baseBranch = payload.pull_request.base.ref;
    const headBranch = payload.pull_request.head.ref;

    let changedFiles: any[] = [];
    let illegalChangedFiles: any[] = [];

    // Step 1: Remove the temp folders
    try {
        // Remove the cloned_repo folder if it exists
        if (fs.existsSync(cloneTargetDirectory)) {
            deleteFolderRecursiveSync(app, cloneTargetDirectory);
        }
        fs.mkdirSync(cloneTargetDirectory);
        // Remove the temp_storage folder if it exists
        if (fs.existsSync(tempStorageDirectory)) {
            deleteFolderRecursiveSync(app, tempStorageDirectory);
        }
        fs.mkdirSync(tempStorageDirectory);
    } catch (error: any) {
        context.log.error(`Failed to remove temp folders: ${error.message}`);
        return;
    }
    
    // Step 2: Clone the repository
    try {
        context.log.info(`Cloning repository ${remoteUrl} into ${cloneTargetDirectory}`);
        await git.clone(repoUrl, clonedRepoFolder);
    } catch (error) {
        context.log.error(`Error cloning repository: ${error}`);
        throw error;
    }
    
    // Step 3: Checkout the source branch
    try {
        context.log.info(`Checking out source branch ${headBranch}`);
        await git.cwd(cloneTargetDirectory).checkout(headBranch);
    } catch (error) {
        context.log.error(`Error checking out source branch: ${error}`);
        throw error;
    }

    // Step 4: Get files changed in the PR
    try {        
        // Fetch both branches to ensure we have the latest
        await git.cwd(cloneTargetDirectory).fetch(['origin', baseBranch]);
        await git.cwd(cloneTargetDirectory).fetch(['origin', headBranch]);
        
        // Get the diff between base and head
        const diff = await git.cwd(cloneTargetDirectory)
            .diff([`origin/${baseBranch}...origin/${headBranch}`, '--name-status']);
        
        // Parse the diff output into a more useful format
        changedFiles = diff.split('\n')
            .filter(line => line.trim().length > 0)
            .map(line => {
                const parts = line.split('\t');
                const status = parts[0];
                
                // Handle renamed files (they have old and new names)
                if (status === 'R' || status.startsWith('R')) {
                    return {
                        filename: parts[2],  // new name
                        oldFilename: parts[1],  // old name
                        status: 'renamed'
                    };
                }

                // Handle added, modified, deleted, copied, unmerged, type_changed
                return {
                    filename: parts[1],
                    status: status === 'A' ? 'added' :           // Added
                           status === 'M' ? 'modified' :         // Modified
                           status === 'D' ? 'deleted' :          // Deleted
                           status === 'C' ? 'copied' :           // Copied
                           status === 'U' ? 'unmerged' :         // Unmerged (conflict)
                           status === 'T' ? 'type_changed' :     // File type changed
                           status
                };
            });
        
        context.log.info('Files changed in PR:');
        console.log(changedFiles);
        
    } catch (error) {
        context.log.error(`Error getting PR changed files: ${error}`);
        throw error;
    }

    // Step 5: Check for illegal changed files
    illegalChangedFiles = changedFiles
        .map((file: any) => file.filename + ' (' + file.status + ')')
        .filter((filename: any) => !filename.startsWith('content/'));

    if (illegalChangedFiles.length > 0) {
        context.log.error(`Illegal changed files: `);
        console.log(illegalChangedFiles);

        // Format the files for the comment
        const formattedFiles = illegalChangedFiles.join('\n');
        const commentBody = `# **Aanpassingen buiten content gevonden, niet toegestaan!** \n ## Gevonden bestanden: \n \`\`\` \n ${formattedFiles} \n \`\`\` \n\n Gelieve alleen aanpassingen te maken in de content map.`;

        // Create a review requesting changes
        await context.octokit.pulls.createReview({
            owner: repoOwner,
            repo: repoName,
            pull_number: prNumber,
            event: 'REQUEST_CHANGES',
            body: commentBody
        });

        // return; // TODO: Remove the comment, this is so the rest of the code is executed. In prod this should be enabled.
    }

    // Step 6: Check if there are unmerged files
    if (changedFiles.some(file => file.status === 'unmerged')) {
        context.log.error('Unmerged files found: ');
        console.log(changedFiles);

        // Format the files for the comment
        const formattedFiles = changedFiles.map(file => file.filename).join('\n');
        const commentBody = `# **Bestanden met conflicten gevonden!** \n ## Gevonden bestanden: \n \`\`\` \n ${formattedFiles} \n \`\`\` \n\n Gelieve de conflicten op te lossen.`;

        // Create a review requesting changes
        await context.octokit.pulls.createReview({
            owner: repoOwner,
            repo: repoName,
            pull_number: prNumber,
            event: 'REQUEST_CHANGES',
            body: commentBody
        });

        // return; // TODO: Remove the comment, this is so the rest of the code is executed. In prod this should be enabled.
    }

    // Step 7: Copy the changed files to temp
    try {
        context.log.info(`Copying changed files to temp storage folder ${tempStorageDirectory}`);

        // Copy the changed files to the temp storage folder
        for (const file of changedFiles) {
            if (file.status === 'added' || file.status === 'modified' || file.status === 'renamed' || file.status === 'copied' || file.status === 'type_changed') {
                console.log(file);
                const sourcePath = path.join(cloneTargetDirectory, file.filename);
                console.log(sourcePath);
                const destinationPath = path.join(tempStorageDirectory, file.filename);
                console.log(destinationPath);

                // Create the directory structure if it doesn't exist
                const destinationDir = path.dirname(destinationPath);
                if (!fs.existsSync(destinationDir)) {
                    fs.mkdirSync(destinationDir, { recursive: true });
                }

                fs.copyFileSync(sourcePath, destinationPath);
            }
        }
        
    } catch (error) {
        context.log.error(`Error copying changed files to temp storage folder: ${error}`);
        throw error;
    }
    
    // Step 8: Remove the cloned repo folder
    try {
        context.log.info('Removing the cloned repo directory...');
        deleteFolderRecursiveSync(app, cloneTargetDirectory);
    } catch (error) {
        context.log.error(`Error deleting cloned repository: ${error}`);
        throw error;
    }

    // Step 9: Move the temp storage folder to the cloned repo folder
    try {
        context.log.info('Moving the temp storage folder to the cloned repo folder...');
        fs.renameSync(tempStorageDirectory, cloneTargetDirectory);
    } catch (error) {
        context.log.error(`Error moving temp storage folder: ${error}`);
        throw error;
    }

    // Step 10: Compile the content
    await new Promise<void>((resolve, reject) => {
        context.log.info(`Compiling content...`);
        exec('python src/scripts/compile_content.py --skip-link-check', (error: any, stdout: any) => {
            if (error) {
                context.log.error(`Execution error: ${error.message}`);
                reject(error);
                return;
            }
            context.log.info(`Output: ${stdout}`);
            resolve();
        });
    });

    // Step 11: Create a review with the compiled content
    try {
        // Read the content report file
        const reportPath = path.join(cloneTargetDirectory, 'content_report.md');
        const reportContent = fs.readFileSync(reportPath, 'utf8');

        await context.octokit.pulls.createReview({
            owner: repoOwner,
            repo: repoName,
            pull_number: prNumber,
            event: 'APPROVE',
            body: reportContent
        });
        context.log.info('Successfully posted content report as PR review');
    } catch (error) {
        context.log.error(`Error posting content report: ${error}`);
        throw error;
    }

    // Step 12: Delete the cloned repository
    try {
        deleteFolderRecursiveSync(app, clonedRepoFolder);
    } catch (error) {
        context.log.error(`Error deleting cloned repository: ${error}`);
        throw error;
    }

    context.log.info('Pre-compile completed successfully');
}

