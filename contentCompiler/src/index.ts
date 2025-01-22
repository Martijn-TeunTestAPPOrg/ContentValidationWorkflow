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

      const __dirname = process.cwd();
      context.log.info(`Push event received for ${repoOwner}/${repoName}`);
      const cloneDirectory = path.join(__dirname, "src/temp_content");

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
      try {
        context.log.info(`Checking out to the 'content' branch...`);
        await git.cwd(cloneDirectory).checkout("content");

        context.log.info(`Repository ${repoName} cloned and checked out to 'content' branch successfully`);
      }
      catch (error: any) {
        context.log.error(`Failed to clone and checkout repository: ${error.message}`);
      }
    }
    exec('python3 src/scripts/script.py', (error: any, stdout: any) => {
      if (error) {
        console.error(`Execution error: ${error}`);
        return;
      }
      console.log(`Output: ${stdout}`);
    });
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
};



// - name: Copy reports to root
// run: |
// cp content_report.md ../
// cp taxco_report.md ../
// # Step 6: Move build folder to root
// - name: Move build folder to root
// run: |
// mkdir -p ../build && cp -r build/* ../build/ && rm -rf build
// # Step 7: Commit report.md to content branch
// - name: Commit report.md to content branch
// run: |
// git add content_report.md
// git add taxco_report.md
// if ! git diff-index --quiet HEAD; then
//   git commit -m "Update reports"
//   git push origin content
// else
//   echo "No changes to commit"
// fi
// # Step 8: Sync to staging branch
// - name: Switch to staging branch and sync
// run: |
// git fetch origin
// git checkout staging
// git rm -rf build/ || true
// cp -r ../build/ build
// git add build/
// cp ../content_report.md content_report.md
// cp ../taxco_report.md taxco_report.md
// git add content_report.md
// git add taxco_report.md
// git commit -m "Sync compiled files and reports to staging" || echo "No changes to commit"
// git push origin staging


