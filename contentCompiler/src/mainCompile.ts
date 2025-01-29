import path from "path";
import * as fs from "fs";
import { exec } from "child_process";
import { simpleGit } from "simple-git";
import { Probot, Context } from "probot";
import { getDefaultConfig, clearTempStorage, deleteFolderRecursiveSync, getInstallationToken, configureGit } from "./helpers.js";


export const mainCompile = async (app: Probot, context: Context<'push'>) => {
    const __dirname = process.cwd();
    const { gitAppName, gitAppEmail, repoOwner, repoName, repoUrl, clonedRepoFolder, reportFiles, cloneTargetDirectory, cloneBuildDirectory, sourceBuildDirectory, tempDestinationBuildDir, tempStorageDirectory } = getDefaultConfig(context);
    
    context.log.info(`Push event received for ${repoOwner}/${repoName}`);

    // Get the installation token
    const token = await getInstallationToken(app, context);

    // Configure git with token
    const remoteUrl = `https://x-access-token:${token}@github.com/${repoOwner}/${repoName}.git`;
    let git = simpleGit();
    await configureGit(git, gitAppName, gitAppEmail);

    // Step 2: Remove the temp folders
    clearTempStorage(cloneTargetDirectory, tempStorageDirectory, app, context);

    // Step 3: Clone the repository
    try {
        context.log.info(`Cloning repository ${repoName} from ${repoUrl}...`);

        await git.clone(repoUrl, cloneTargetDirectory);

        await git.cwd(cloneTargetDirectory);
        await git.remote(['set-url', 'origin', remoteUrl]);

        context.log.info(`Repository ${repoName} cloned successfully to ${cloneTargetDirectory}`);
    }
    catch (error: any) {
        context.log.error(`Failed to clone repository: ${error.message}`);
        throw error;
    }

    // Step 4: Checkout to the 'content' branch
    try {
        context.log.info(`Checking out to the 'content' branch...`);
        await git.cwd(cloneTargetDirectory).checkout("content");

        context.log.info(`Checked out to 'content' branch successfully`);
    }
    catch (error: any) {
        context.log.error(`Failed to checkout content branch: ${error.message}`);
        throw error;
    }

    // Step 5: Compile the content
    await new Promise<void>((resolve, reject) => {
        context.log.info(`Compiling content...`);
        const pythonProcess = exec('python src/scripts/compile_content.py');
        
        let stdoutData = '';
        let stderrData = '';

        // Collect stdout data
        pythonProcess.stdout?.on('data', (data) => {
            stdoutData += data;
        });

        // Collect stderr data
        pythonProcess.stderr?.on('data', (data) => {
            stderrData += data;
        });

        // Handle process completion
        pythonProcess.on('close', (code) => {
            if (code === 0) {
                context.log.info(`Python script output: ${stdoutData}`);
                resolve();
            } else {
                context.log.error(`Python script failed with code ${code}`);
                context.log.error(`Error output: ${stderrData}`);
                reject(new Error(`Python script failed with code ${code}`));
            }
        });
    });

    // Step 6: Copy the reports to the storage folder
    try {
        context.log.info(`Copying reports to the storage folder...`);
        
        reportFiles.forEach((file) => {
            const sourcePath = path.join(__dirname, clonedRepoFolder, file);
            const destinationPath = path.join(tempStorageDirectory, file);
            fs.copyFileSync(sourcePath, destinationPath);
        });
    } catch (error: any) {
        context.log.error(`Failed to copy reports to the storage folder: ${error.message}`);
        throw error;
    }

    // Step 7: Move build to temp_storage
    try {
        context.log.info(`Copying build to the storage folder...`);

        // Copy build directory to temp destination
        fs.readdirSync(sourceBuildDirectory).forEach((file) => {
            const sourcePath = path.join(sourceBuildDirectory, file);
            const destinationPath = path.join(tempDestinationBuildDir, file);

            if (fs.lstatSync(sourcePath).isDirectory()) {
                fs.cpSync(sourcePath, destinationPath, { recursive: true });
            } else {
                fs.copyFileSync(sourcePath, destinationPath);
            }
        });

        // Delete source build directory
        deleteFolderRecursiveSync(app, sourceBuildDirectory);
    } catch (error: any) {
        context.log.error(`Failed to copy build to the storage folder: ${error.message}`);
        throw error;
    }

    // Step 8: Commit and push reports to the 'content' branch
    try {
        context.log.info(`Committing and pushing reports to the 'content' branch...`);
        await configureGit(git, gitAppName, gitAppEmail); // Configure git before committing
  
        await git.add(reportFiles);
        const status = await git.status();
        
        if (!status.isClean()) {
            const commitMessage = "Update reports [bot-commit]";
            await git.commit(commitMessage, undefined, {
                '--author': `${gitAppName} <${gitAppEmail}>`,
                '--no-verify': null
            });
            await git.push('origin', 'content');
        } else {
              context.log.info('No changes to commit');
        }
    } catch (error: any) {
        context.log.error(`Failed to commit and push reports: ${error.message}`);
        throw error;
    }

    // Step 9: Remove everything from cloned_repo
    try {
        context.log.info(`Removing cloned repository ${repoName}...`);
        deleteFolderRecursiveSync(app, cloneTargetDirectory);
    } catch (error: any) {
        context.log.error(`Failed to remove cloned repo: ${error.message}`);
        throw error;
    }

    git = simpleGit({ baseDir: process.cwd() });

    // Step 10: Clone the repository
    try {
        context.log.info(`Cloning repository ${repoName} from ${repoUrl}...`);

        await git.clone(repoUrl, cloneTargetDirectory);
        await git.remote(['set-url', 'origin', remoteUrl]);

        context.log.info(`Repository ${repoName} cloned successfully to ${cloneTargetDirectory}`);
    }
    catch (error: any) {
        context.log.error(`Failed to clone repository: ${error.message}`);
        throw error;
    }

    git = simpleGit({ baseDir: cloneTargetDirectory });
    
    // Step 11: Check out to the 'staging' branch
    try {
        context.log.info(`Checking out to the 'staging' branch...`);
        await git.cwd(cloneTargetDirectory).checkout("staging");
    } catch (error: any) {
        context.log.error(`Failed to checkout to the 'staging' branch: ${error.message}`);
        throw error;
    }

    // Step 12: Pull the latest changes from the 'staging' branch
    try {
        context.log.info(`Pulling the latest changes from the 'staging' branch...`);
        await git.pull('origin', 'staging');
    } catch (error: any) {
        context.log.error(`Failed to pull the latest changes from the 'staging' branch: ${error.message}`);
        throw error;
    }

    // Step 13: Remove the build directory from the 'staging' branch
    try {
        context.log.info('Removing the build directory from the staging branch...');

        if (fs.existsSync(cloneBuildDirectory)) {
            await git.rm(['-r', 'build/']);
            deleteFolderRecursiveSync(app, cloneBuildDirectory);
        }
    } catch (error: any) {
        context.log.error(`Failed to remove the build directory from the staging branch: ${error.message}`);
        throw error;
    }

    // Step 14: Remove the reports from the 'staging' branch
    try {
        context.log.info('Removing the reports from the staging branch...');
        
        reportFiles.forEach((file) => {
            const filePath = path.join(cloneTargetDirectory, file);
            if (fs.existsSync(filePath)) {
                context.log.info(`Removing ${filePath}...`);
                fs.rmSync(filePath, { force: true });
            } else {
                context.log.info(`File ${file} does not exist, skipping...`);
            }
        });
    } catch (error: any) {
        context.log.error(`Failed to remove the reports from the staging branch: ${error.message}`);
        throw error;
    }

    // Step 15: Sync the compiled files and reports to the 'staging' branch
    try {
        // Copy the build directory to the repo root
        context.log.info('Copying build to the repository root...');
        fs.readdirSync(tempDestinationBuildDir).forEach((file) => {
            const sourcePath = path.join(tempDestinationBuildDir, file);
            const destinationPath = path.join(sourceBuildDirectory, file);

            if (fs.lstatSync(sourcePath).isDirectory()) {
                fs.cpSync(sourcePath, destinationPath, { recursive: true });
            } else {
                fs.copyFileSync(sourcePath, destinationPath);
            }
        });
    } catch (error: any) {
        context.log.error(`Failed to copy build to the repository root: ${error.message}`);
        throw error;
    }

    // Step 16: Copy the reports to the staging branch
    try {
        context.log.info(`Copying reports to the repository root...`);
        
        reportFiles.forEach((file) => {
            const sourcePath = path.join(tempStorageDirectory, file);
            const destinationPath = path.join(clonedRepoFolder, file);
            fs.copyFileSync(sourcePath, destinationPath);
        });
    } catch (error: any) {
        context.log.error(`Failed to copy reports to the storage folder: ${error.message}`);
        throw error;
    }

    // Step 17: Commit and push the compiled files and reports to the 'staging' branch
    try {
        context.log.info('Committing and pushing compiled files and reports to the staging branch...');
        await configureGit(git, gitAppName, gitAppEmail);
        await git.remote(['set-url', 'origin', remoteUrl]);

        await git.add('build/');
        await git.add('taxco_report.md');
        await git.add('content_report.md');

        const statusBeforeCommit = await git.status();
        if (!statusBeforeCommit.isClean()) {
            await git.commit('Sync compiled files and reports to staging', undefined, {
                '--author': `${gitAppName} <${gitAppEmail}>`,
                '--no-verify': null
            });
            await git.push('origin', 'staging');
        } else {
            context.log.info('No changes to commit');
        }
    } catch (error: any) {
        context.log.error(`Failed to sync to staging branch: ${error.message}`);
        throw error;
    }

    // Step 18: Remove the cloned repo directory
    try {
        context.log.info('Removing the cloned repo directory...');
        deleteFolderRecursiveSync(app, cloneTargetDirectory);
    } catch (error: any) {
        context.log.error(`Failed to remove the cloned repo directory: ${error.message}`);
        throw error;
    }

    // Step 19: Remove the temp storage folder
    try {
        context.log.info('Removing the temp storage folder...');
        deleteFolderRecursiveSync(app, tempStorageDirectory);
    } catch (error: any) {
        context.log.error(`Failed to remove the temp storage folder: ${error.message}`);
        throw error;
    }

    context.log.info('Sync to staging branch completed successfully');
}
