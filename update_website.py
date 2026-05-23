import subprocess
import sys
import datetime

def run_command(command, description):
    print(f"\n--- {description} ---")
    try:
        # shell=True is often needed on Windows for git commands or complex arguments
        # check=True will raise CalledProcessError if the command fails
        subprocess.run(command, check=True, shell=True)
        print(f"[OK] {description} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error during: {description}")
        print(f"Command failed with exit code {e.returncode}")
        sys.exit(e.returncode)

def main():
    print("Starting website update process...")

    # 1. Update the local RSS feed with latest images and episodes
    run_command("python generate_updated_rss.py", "Generating updated RSS feed")

    # 2. Generate individual mathematician pages and search index
    run_command("python generate_mathematician_pages.py", "Generating mathematician pages and search index")

    # 3. Git operations
    # Get current date for the commit message
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    commit_msg = f"update with new episodes {date_str}"

    run_command("git add .", "Staging changes")
    
    # Commit might fail if there are no changes, so we handle that gracefully
    print(f"\n--- Committing changes ---")
    try:
        subprocess.run(f'git commit -m "{commit_msg}"', check=True, shell=True)
        print("[OK] Changes committed.")
    except subprocess.CalledProcessError:
        print("Note: No changes to commit (or commit failed). Continuing...")

    run_command("git push", "Pushing to remote repository")

    print("\n[SUCCESS] Website update complete!")

if __name__ == "__main__":
    main()
