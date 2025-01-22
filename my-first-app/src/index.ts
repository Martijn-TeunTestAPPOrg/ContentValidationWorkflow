import { Probot } from "probot";

export default (app: Probot) => {
  app.on("push", async (context) => {
    const issueComment = context.issue({
      body: "Thanks for opening this issue!",
    });
    await context.octokit.issues.createComment(issueComment);
  });
  // For more information on building apps:
  // https://probot.github.io/docs/

  // To get your app running against GitHub, see:
  // https://probot.github.io/docs/development/
  app.on('push', async (context) => {
    const payload = context.payload;

    // Extract push details
    const branch = payload.ref.replace('refs/heads/', ''); // Get branch name
    context.log.info(`Push detected on branch ${branch}`);

    // Example: Add a comment to the latest commit
    await context.octokit.issues.create({
      owner: payload.repository.owner.login,
      repo: payload.repository.name,
      title: `New push to ${branch}`,
      body: `A push was made in ${branch}`
    });
  });
};
