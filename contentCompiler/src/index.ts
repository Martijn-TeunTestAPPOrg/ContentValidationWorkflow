import { Probot, Context } from "probot";
import { exec } from 'child_process';
import path from "path";
import { simpleGit } from "simple-git";
import * as fs from "fs";

const gitAppName = "ContentCompiler";
const gitAppEmail = "1112193+github[bot]@users.noreply.github.com";

export default (app: Probot) => {
	app.on("push", async (context) => {
		// Skip if this is a commit from our app
		if (isAppCommit(context)) {
			return;
		}

		const payload = context.payload;
		const branch = payload.ref.replace('refs/heads/', '');
		const repoOwner = payload.repository.owner.login;
		const repoName = payload.repository.name;
		const repoUrl = payload.repository.clone_url;  

		if (branch === "content") {
			context.log.info(`Push event received for ${repoOwner}/${repoName}`);

			const clonedRepoFolder = 'src/cloned_repo'
			const tempStorageFolder = 'src/temp_storage';
			const reportFiles = ['taxco_report.md', 'content_report.md'];

			const __dirname = process.cwd();
			const cloneTargetDirectory = path.join(__dirname, "src/cloned_repo");
			const cloneBuildDirectory = path.join(cloneTargetDirectory, 'build');

			const sourceBuildDirectory = path.join(__dirname, clonedRepoFolder, 'build');
			const tempDestinationBuildDir = path.join(__dirname, tempStorageFolder, 'build');

			// Get the installation token
			const octokit = await app.auth();
			const installationId = context.payload.installation?.id;
			if (!installationId) {
				throw new Error('No installation ID found');
			}
			const { token } = await octokit.auth({
				type: 'installation',
				installationId
			}) as { token: string };

			// Configure git with token
			const remoteUrl = `https://x-access-token:${token}@github.com/${repoOwner}/${repoName}.git`;
			
			let git = simpleGit();

			// Setup git
			const configureGit = async () => {
				await git.addConfig("user.name", gitAppName, false, 'local');
				await git.addConfig("user.email", gitAppEmail, false, 'local');
				// Set committer info explicitly
				await git.addConfig("committer.name", gitAppName, false, 'local');
				await git.addConfig("committer.email", gitAppEmail, false, 'local');
			};

		// Step 2: Remove the temp folders
			try {
				// Remove the cloned_repo folder if it exists
				if (fs.existsSync(cloneTargetDirectory)) {
					deleteFolderRecursiveSync(cloneTargetDirectory);
				}
				fs.mkdirSync(cloneTargetDirectory);
				// Remove the cloned_repo folder if it exists
				if (fs.existsSync(tempStorageFolder)) {
					deleteFolderRecursiveSync(tempStorageFolder);
				}
				fs.mkdirSync(tempStorageFolder);
			} catch (error: any) {
				context.log.error(`Failed to remove temp folders: ${error.message}`);
				return;
			}

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
				return
			}

		// Step 4: Checkout to the 'content' branch
			try {
				context.log.info(`Checking out to the 'content' branch...`);
				await git.cwd(cloneTargetDirectory).checkout("content");

				context.log.info(`Checked out to 'content' branch successfully`);
			}
			catch (error: any) {
				context.log.error(`Failed to checkout content branch: ${error.message}`);
				return;
			}

		// Step 5: Compile the content
			await new Promise<void>((resolve, reject) => {
				context.log.info(`Compiling content...`);
				exec('python src/scripts/compile_content.py', (error: any, stdout: any) => {
					if (error) {
						context.log.error(`Execution error: ${error.message}`);
						reject(error);
						return;
					}
					context.log.info(`Output: ${stdout}`);
					resolve();
				});
			});

		// Step 6: Copy the reports to the storage folder
			try {
				context.log.info(`Copying reports to the storage folder...`);
				
				reportFiles.forEach((file) => {
					const sourcePath = path.join(__dirname, clonedRepoFolder, file);
					const destinationPath = path.join(__dirname, tempStorageFolder, file);
					fs.copyFileSync(sourcePath, destinationPath);
				});
			} catch (error: any) {
				context.log.error(`Failed to copy reports to the storage folder: ${error.message}`);
				return;
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
				deleteFolderRecursiveSync(sourceBuildDirectory);
			} catch (error: any) {
				context.log.error(`Failed to copy build to the storage folder: ${error.message}`);
				return;
			}

		// Step 8: Commit and push reports to the 'content' branch
			try {
				context.log.info(`Committing and pushing reports to the 'content' branch...`);
				await configureGit(); // Configure git before committing
		  
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
				return;
			}

		// Step 9: Remove everything from cloned_repo
			try {
				context.log.info(`Removing cloned repository ${repoName}...`);
				deleteFolderRecursiveSync(cloneTargetDirectory);
			} catch (error: any) {
				context.log.error(`Failed to remove cloned repo: ${error.message}`);
				return;
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
				return
			}

			git = simpleGit({ baseDir: cloneTargetDirectory });
			
		// Step 11: Check out to the 'staging' branch
			try {
				context.log.info(`Checking out to the 'staging' branch...`);
				await git.cwd(cloneTargetDirectory).checkout("staging");
			} catch (error: any) {
				context.log.error(`Failed to checkout to the 'staging' branch: ${error.message}`);
				return;
			}

		// Step 12: Pull the latest changes from the 'staging' branch
			try {
				context.log.info(`Pulling the latest changes from the 'staging' branch...`);
				await git.pull('origin', 'staging');
			} catch (error: any) {
				context.log.error(`Failed to pull the latest changes from the 'staging' branch: ${error.message}`);
				return;
			}

		// Step 13: Remove the build directory from the 'staging' branch
			try {
				context.log.info('Removing the build directory from the staging branch...');

				if (fs.existsSync(cloneBuildDirectory)) {
					await git.rm(['-r', 'build/']);
					deleteFolderRecursiveSync(cloneBuildDirectory);
				}
			} catch (error: any) {
				context.log.error(`Failed to remove the build directory from the staging branch: ${error.message}`);
				return;
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
				return;
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
				return;
			}

		// Step 16: Copy the reports to the staging branch
			try {
				context.log.info(`Copying reports to the storage folder...`);
				
				reportFiles.forEach((file) => {
					const sourcePath = path.join(__dirname, tempStorageFolder, file);
					const destinationPath = path.join(__dirname, clonedRepoFolder, file);
					fs.copyFileSync(sourcePath, destinationPath);
				});
			} catch (error: any) {
				context.log.error(`Failed to copy reports to the storage folder: ${error.message}`);
				return;
			}

		// Step 17: Commit and push the compiled files and reports to the 'staging' branch
			try {
				context.log.info('Committing and pushing compiled files and reports to the staging branch...');
				await configureGit(); // Configure git before committing
		
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
				return;
			}

		// Step 18: Remove the cloned repo directory
			try {
				context.log.info('Removing the cloned repo directory...');
				deleteFolderRecursiveSync(cloneTargetDirectory);
			} catch (error: any) {
				context.log.error(`Failed to remove the cloned repo directory: ${error.message}`);
				return;
			}

		// Step 19: Remove the temp storage folder
			try {
				context.log.info('Removing the temp storage folder...');
				deleteFolderRecursiveSync(tempStorageFolder);
			} catch (error: any) {
				context.log.error(`Failed to remove the temp storage folder: ${error.message}`);
				return;
			}

			context.log.info('Sync to staging branch completed successfully');
		}
	});

	// Helper function to delete a folder recursively
	const deleteFolderRecursiveSync = (folderPath: string) => {
		if (fs.existsSync(folderPath)) {
			const files = fs.readdirSync(folderPath);

			files.forEach((file) => {
				const currentPath = path.join(folderPath, file);

				if (fs.statSync(currentPath).isDirectory()) {
					deleteFolderRecursiveSync(currentPath);
				} else {
					fs.unlinkSync(currentPath);
				}
			});

			fs.rmdirSync(folderPath);
		} else {
			app.log.warn(`Folder ${folderPath} does not exist`);
		}
	}

	// Helper function to check if the commit is from our app
	function isAppCommit(context: Context<'push'>) {
		const sender = context.payload.sender;
		const commits = context.payload.commits || [];
		
		// Check both the sender and the commit message
		return (sender && sender.type === 'Bot' && sender.login.endsWith('[bot]')) ||
			   commits.some(commit => commit.message.includes('[bot-commit]'));
	}
};
