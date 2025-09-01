import os
import subprocess

from dotenv import load_dotenv

from pixBoards.arguments import args
from pixBoards.config_loader import config, outputDir
from pixBoards.log_utils import setup_logger

logger = setup_logger()


load_dotenv()


def git_push_repo(output_dir, repo_url=None):

    print(f"Pushing to: {repo_url}")
    try:
        output_dir = os.path.abspath(output_dir)

        subprocess.run(
            ["git", "-C", output_dir, "config", "credential.helper", ""], check=True
        )

        # Initialize repo if not already initialized
        if not os.path.exists(os.path.join(output_dir, ".git")):
            subprocess.run(["git", "-C", output_dir, "init"], check=True)

        # Check if 'main' branch exists
        result = subprocess.run(
            ["git", "-C", output_dir, "branch", "--list", "main"],
            capture_output=True,
            text=True,
        )
        if not result.stdout.strip():
            subprocess.run(
                ["git", "-C", output_dir, "checkout", "-b", "main"], check=True
            )
        else:
            subprocess.run(["git", "-C", output_dir, "checkout", "main"], check=True)

        # Add and commit
        subprocess.run(["git", "-C", output_dir, "add", "."], check=True)
        subprocess.run(
            ["git", "-C", output_dir, "commit", "-m", "automated commit"],
            check=False,
        )

        # Check if remote 'main' already exists
        remotes = subprocess.run(
            ["git", "-C", output_dir, "remote"], capture_output=True, text=True
        ).stdout
        if "main" not in remotes:
            subprocess.run(
                ["git", "-C", output_dir, "remote", "add", "origin", repo_url],
                check=True,
            )

        # Push
        subprocess.run(
            ["git", "-C", output_dir, "push", "--set-upstream", "origin", "main"],
            check=True,
        )

        print("✅ Successfully pushed to remote repository.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")


token = os.getenv("GITHUB_PAT")

if args.gitPush:
    remote_url = config["remote_url"]
    username = config["gitUsername"]
    # print(username)
    if token and username:
        authed_url = remote_url.replace("https://", f"https://{username}:{token}@")
        # print(authed_url)
        git_push_repo(outputDir, repo_url=authed_url)
        # git_push_repo(outputDir, remote_url)
    else:
        logger.warning("Missing GitHub username or token; cannot push.")
