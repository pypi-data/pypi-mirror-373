from typing import Dict, Any


class GithubRepository:
    def __init__(self, github_repository_info: Dict[str, Any]) -> None:
        self.id: int = github_repository_info["id"]
        self.repository_owner: str = github_repository_info["repository_owner"]
        self.repository_name: str = github_repository_info["repository_name"]
        self.repository_full_name: str = github_repository_info["repository_full_name"]
        self.repository_ssh_url: str = github_repository_info["repository_ssh_url"]
        self.github_account_id: int = github_repository_info["github_account_id"]
