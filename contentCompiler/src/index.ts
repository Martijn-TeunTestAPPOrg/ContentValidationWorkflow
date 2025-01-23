import { Probot } from "probot";
import { exec } from 'child_process';
import path from "path";
import { simpleGit } from "simple-git";
import * as fs from "fs";


const git = simpleGit();

export default (app: Probot) => {
  app.on("push", async (context) => {
    const payload = context.payload;
    const branch = payload.ref.replace('refs/heads/', '');
    if (branch === "content") {
      context.log.info(`Push detected on branch ${branch}`);
      const payload = context.payload;
      const repoOwner = payload.repository.owner.login;
      const repoName = payload.repository.name;
      const repoUrl = payload.repository.clone_url;
      const tempContentFolder = 'src/temp_content'
      const tempStorageFolder = 'src/temp_storage';

      const __dirname = process.cwd();
      context.log.info(`Push event received for ${repoOwner}/${repoName}`);
      const cloneDirectory = path.join(__dirname, "src/temp_content");

      ///
      try {
        if (fs.existsSync(cloneDirectory)) {
          deleteFolderRecursiveSync(cloneDirectory)
        }
        context.log.info(`Cloning repository ${repoName} from ${repoUrl}...`);
        await git.clone(repoUrl, cloneDirectory);
        context.log.info(`Repository ${repoName} cloned successfully to ${cloneDirectory}`);
      }
      catch (error: any) {
        context.log.error(`Failed to clone repository: ${error.message}`);
      }

      ///
      try {
        context.log.info(`Checking out to the 'content' branch...`);
        await git.cwd(cloneDirectory).checkout("content");

        context.log.info(`Repository ${repoName} cloned and checked out to 'content' branch successfully`);
      }
      catch (error: any) {
        context.log.error(`Failed to clone and checkout repository: ${error.message}`);
      }
      exec('python3 src/scripts/compile_content.py', (error: any, stdout: any) => {
        if (error) {
          context.log.error(`Execution error: ${error.message}`);
          return;
        }
        context.log.info(`Output: ${stdout}`);
      });

      const sourceFiles = ['taxco_report.md', 'content_report.md'];
      await waitForFiles(path.join(__dirname, tempContentFolder, sourceFiles[0]))

      sourceFiles.forEach((file) => {
        const sourcePath = path.join(__dirname, tempContentFolder, file);
        const destinationPath = path.join(__dirname, tempStorageFolder, file);
        fs.copyFileSync(sourcePath, destinationPath);
      });

      ///
      const sourceBuildDir = path.join(__dirname, tempContentFolder, 'build');
      const destinationBuildDir = path.join(__dirname, tempStorageFolder, 'build');

      if (fs.existsSync(destinationBuildDir)) {
        deleteFolderRecursiveSync(destinationBuildDir)
      }
      fs.mkdirSync(destinationBuildDir);

      fs.readdirSync(sourceBuildDir).forEach((file) => {
        const sourcePath = path.join(sourceBuildDir, file);
        const destinationPath = path.join(destinationBuildDir, file);

        if (fs.lstatSync(sourcePath).isDirectory()) {
          context.log.info(sourcePath)
          fs.cpSync(sourcePath, destinationPath, { recursive: true });
        } else {
          fs.copyFileSync(sourcePath, destinationPath);
        }
      });
      deleteFolderRecursiveSync(sourceBuildDir)

      try {
        await git.add(['content_report.md', 'taxco_report.md'])
        const status = await git.status()
        if (!status.isClean()) {
          await git.commit("Update reports")
          await git.push('origin', 'content')
          context.log.info('Reports committed and pushed to content branch');
        }
        else {
          context.log.info('No changes to commit');
        }
      }
      catch (error: any) {
        context.log.error(`Failed to commit and push reports: ${error.message}`);
      }

      // try {
      //   context.log.info(`Checking out to the 'staging' branch...`);
      //   await git.cwd(cloneDirectory).checkout("content");

      //   if (fs.existsSync(sourceBuildDir)) {
      //     deleteFolderRecursiveSync(sourceBuildDir)
      //   }
      //   fs.mkdirSync(sourceBuildDir)

      //   fs.readdirSync(destinationBuildDir).forEach((file) => {
      //     const sourcePath = path.join(destinationBuildDir, file);
      //     const destinationPath = path.join(sourceBuildDir, file);

      //     if (fs.lstatSync(sourcePath).isDirectory()) {
      //       context.log.info(sourcePath)
      //       fs.cpSync(sourcePath, destinationPath, { recursive: true });
      //     } else {
      //       fs.copyFileSync(sourcePath, destinationPath);
      //     }
      //   });
      //   deleteFolderRecursiveSync(destinationBuildDir)

      //   await git.add('build/')

      //   const sourceFiles = ['taxco_report.md', 'content_report.md'];

      //   sourceFiles.forEach((file) => {
      //     const sourcePath = path.join(__dirname, tempStorageFolder, file);
      //     const destinationPath = path.join(__dirname, tempContentFolder, file);
      //     fs.copyFileSync(sourcePath, destinationPath);
      //   });
      //   await git.add('taxco_report.md')
      //   await git.add('content_report.md')

      //   const statusBeforeCommit = await git.status();
      //   if (!statusBeforeCommit.isClean()) {
      //     await git.commit('Sync compiled files and reports to staging');
      //     await git.push('origin', 'staging')
      //   } else {
      //     context.log.info('No changes to commit');
      //   }

      // }
      // catch (error: any) {
      //   context.log.error(`Failed to sync to staging branch: ${error.message}`);
      // }



    }
  });

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
  const waitForFiles = async (sourcePath: any) => {
    const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
    let attempts = 5;
    while (attempts > 0) {
      if (fs.existsSync(sourcePath)) {
        console.log('File is ready:', sourcePath);
        return true;
      }
      console.log(`Waiting for file to be available... (${5 - attempts + 1}/5)`);
      await delay(1000);
      attempts--;
    }
    throw new Error('File did not become available in time.');
  }
};

