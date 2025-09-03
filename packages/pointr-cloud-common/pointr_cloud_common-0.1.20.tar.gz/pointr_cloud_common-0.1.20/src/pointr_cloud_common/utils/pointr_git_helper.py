import os
import urllib.parse
import git
from typing import Dict, Any

class GitHelper:
    """Git helper with configurable credentials."""
    
    def __init__(self, config: Dict[str, str]) -> None:
        self.username = urllib.parse.quote(config.get("pointr_repo_username", ""))
        self.pat = urllib.parse.quote(config.get("pointr_repo_pat", ""))

    def clone_repo(self, repo_url: str, local_folder: str) -> None:
        """Clone a repository to a local folder."""
        if not os.path.exists(local_folder):
            os.makedirs(local_folder)
        git.Repo.clone_from(repo_url, local_folder)

    def pull_repo(self, local_folder: str) -> None:
        """Pull latest changes from a repository."""
        g = git.cmd.Git(local_folder)
        g.pull()

    def sync_repo(self, repo_name: str, data_folder: str = "data/") -> None:
        """Sync a repository (clone if not exists, pull if exists)."""
        repo_url = f"https://{self.username}:{self.pat}@github.com/pointrlabs/{repo_name}"
        local_folder = os.path.join(data_folder, repo_name)
        
        print(f"Repository URL: {repo_url}")
        print(f"Repository Local Folder: {local_folder}")
        
        if os.path.exists(local_folder):
            print(f"Pulling repo {repo_name}...")
            self.pull_repo(local_folder)
            print(f"Repo {repo_name} pulled.")
        else:
            print(f"Local path {local_folder} does not exist. Cloning repo {repo_name}...")
            self.clone_repo(repo_url, local_folder)
            print(f"Repo {repo_name} cloned in {local_folder}")


# Legacy functions for backward compatibility
def cloneRepo(config: Dict[str, str], repo_url: str, local_folder: str) -> None:
    """Legacy function for backward compatibility."""
    helper = GitHelper(config)
    helper.clone_repo(repo_url, local_folder)

def pullRepo(config: Dict[str, str], local_folder: str) -> None:
    """Legacy function for backward compatibility."""
    helper = GitHelper(config)
    helper.pull_repo(local_folder)

def syncRepo(config: Dict[str, str], repo_name: str) -> None:
    """Legacy function for backward compatibility."""
    helper = GitHelper(config)
    helper.sync_repo(repo_name) 