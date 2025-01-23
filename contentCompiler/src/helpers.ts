import * as fs from "fs";
import path from "path";
import { Probot, Context } from "probot";
import simpleGit from "simple-git";


// Helper function to check if the commit is from our app
export function isAppCommit(context: Context<'push'>) {
    const sender = context.payload.sender;
    const commits = context.payload.commits || [];
    
    // Check both the sender and the commit message
    return (sender && sender.type === 'Bot' && sender.login.endsWith('[bot]')) ||
           commits.some(commit => commit.message.includes('[bot-commit]'));
}

// Helper function to get the installation token
export const getInstallationToken = async (app: Probot, context: Context<any>) => {
    const octokit = await app.auth();
    const installationId = context.payload.installation?.id;
    if (!installationId) {
        throw new Error('No installation ID found');
    }
    const { token } = await octokit.auth({
        type: 'installation',
        installationId
    }) as { token: string };

    return token;
}

// Helper function to configure git
export const configureGit = async (git: simpleGit.SimpleGit, gitAppName: string, gitAppEmail: string) => {
    if (!gitAppName || !gitAppEmail) {
        throw new Error('Git app name or email not configured in environment variables');
    }
    await git.addConfig("user.name", gitAppName, false, 'local');
    await git.addConfig("user.email", gitAppEmail, false, 'local');
    // Set committer info explicitly
    await git.addConfig("committer.name", gitAppName, false, 'local');
    await git.addConfig("committer.email", gitAppEmail, false, 'local');
}

// Helper function to delete a folder recursively
export const deleteFolderRecursiveSync = (app: Probot, folderPath: string) => {
    if (fs.existsSync(folderPath)) {
        const files = fs.readdirSync(folderPath);

        files.forEach((file) => {
            const currentPath = path.join(folderPath, file);

            if (fs.statSync(currentPath).isDirectory()) {
                deleteFolderRecursiveSync(app,currentPath);
            } else {
                fs.unlinkSync(currentPath);
            }
        });

        fs.rmdirSync(folderPath);
    } else {
        app.log.warn(`Folder ${folderPath} does not exist`);
    }
}
