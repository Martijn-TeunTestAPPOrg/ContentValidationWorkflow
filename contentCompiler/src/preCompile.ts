import path from "path";
import * as fs from "fs";
import { exec } from "child_process";
import { simpleGit } from "simple-git";
import { Probot, Context } from "probot";
import { getDefaultConfig, getInstallationToken, configureGit, clearTempStorage, deleteFolderRecursiveSync } from "./helpers.js";

// This variable is used to keep track of the steps that have been executed
var stepSixReviewId: number | null = null;

export const preCompile = async (app: Probot, context: Context<'pull_request'>) => {
    const { gitAppName, gitAppEmail, repoOwner, repoName, repoUrl, clonedRepoFolder, cloneTargetDirectory, tempStorageDirectory, datasetRepoUrl, datasetFolder } = getDefaultConfig(context);
    
    const payload = context.payload;
    const prNumber = payload.number;

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
    clearTempStorage(cloneTargetDirectory, tempStorageDirectory, app, context);

    // Step 2: Clone the dataset
    try {
        context.log.info(`Cloning dataset...`);

        // Remove the dataset folder if it exists
        if (fs.existsSync(datasetFolder)) {
            deleteFolderRecursiveSync(app, datasetFolder);
        }

        await git.clone(datasetRepoUrl, datasetFolder);
        context.log.info(`Dataset cloned successfully to ${cloneTargetDirectory}`);
    }
    catch (error: any) {
        context.log.error(`Failed to clone dataset: ${error.message}`);
        throw error;
    }
    
    // Step 3: Clone the repository
    try {
        context.log.info(`Cloning repository ${remoteUrl} into ${cloneTargetDirectory}`);
        await git.clone(repoUrl, clonedRepoFolder);
    } catch (error) {
        context.log.error(`Error cloning repository: ${error}`);
        throw error;
    }
    
    // Step 4: Checkout the source branch
    try {
        context.log.info(`Checking out source branch ${headBranch}`);
        await git.cwd(cloneTargetDirectory).checkout(headBranch);
    } catch (error) {
        context.log.error(`Error checking out source branch: ${error}`);
        throw error;
    }

    // Step 5: Get files changed in the PR
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
    } catch (error) {
        context.log.error(`Error getting PR changed files: ${error}`);
        throw error;
    }

    // Step 6: Check for illegal changed files
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
        const review = await context.octokit.pulls.createReview({
            owner: repoOwner,
            repo: repoName,
            pull_number: prNumber,
            event: 'REQUEST_CHANGES',
            body: commentBody
        });

        // Log the review ID
        context.log.info(`Successfully posted comment with ID ${review.data.id}`);

        // Set the flag so we don't post another comment in step 7
        stepSixReviewId = review.data.id;
    }

    // Step 7 Copy the changed files to temp
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
        exec('python src/scripts/compileContent.py --skip-link-check', (error: any, stdout: any) => {
            if (error) {
                context.log.error(`Execution error: ${error.message}`);
                reject(error);
                return;
            }
            context.log.info(`Output: ${stdout}`);
            resolve();
        });
    });

    // Step 11: Hide previous bot comments before posting a new one
    try {
        context.log.info('Fetching all reviews on the PR...');
        const reviews = await context.octokit.pulls.listReviews({
            owner: repoOwner,
            repo: repoName,
            pull_number: prNumber,
            sort: 'created',  // Ensure reviews are sorted by creation time
            direction: 'desc' // Most recent first
        });

        // Filter out bot comments
        const botReviews = reviews.data.filter(review =>
            review.user?.login === process.env.GITHUB_BOT_NAME && review.user?.type === "Bot"
        );

        context.log.info(`Found ${botReviews.length} previous bot comments.`);

        // Hide all bot comments except the most recent one if it was posted in this run
        for (const review of botReviews) {
            // Skip hiding the most recent comment if it was posted in this run
            if (stepSixReviewId !== null && review.id === stepSixReviewId) {
                context.log.info(`Skipping hiding most recent comment with ID ${review.id} since it was posted in this run`);
                continue;
            }

            // Use GraphQL to minimize the review
            const query = `
                mutation MinimizeComment($id: ID!) {
                    minimizeComment(input: { subjectId: $id, classifier: OUTDATED }) {
                        clientMutationId
                    }
                }
            `;

            await context.octokit.graphql(query, {
                id: review.node_id,
            });

            context.log.info(`Minimized review with ID ${review.id}`);
        }
    } catch (error) {
        context.log.error(`Error hiding previous bot comments: ${error}`);
        // Log the specific error details
        if (error instanceof Error) {
            context.log.error(`Error message: ${error.message}`);
            context.log.error(`Error stack: ${error.stack}`);
        }
    }

    // Step 12: Create a review with the compiled content
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

    // Step 13: Delete the cloned repository
    try {
        context.log.info('Removing the cloned repository...');
        deleteFolderRecursiveSync(app, clonedRepoFolder);
    } catch (error) {
        context.log.error(`Error deleting cloned repository: ${error}`);
        throw error;
    }

    // Step 14: Delete the dataset folder
    try {
        context.log.info('Removing the dataset folder...');
        deleteFolderRecursiveSync(app, datasetFolder);
    } catch (error) {
        context.log.error(`Error deleting dataset folder: ${error}`);
        throw error;
    }

    context.log.info('Pre-compile completed successfully');
    stepSixReviewId = null;
}

