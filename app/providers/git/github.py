from github import Github, GithubException

from app.core.logging import logger
from app.providers.base import GitProvider


class GitHubProvider(GitProvider):
    def __init__(self, token: str | None):
        if not token:
            raise ValueError("GITHUB_TOKEN is required")
        self._token = token
        self._connection = None

    def get_connection(self):
        if self._connection is None:
            logger.info("Initializing GitHub connection...")
            self._connection = Github(self._token)
        return self._connection

    def get_project(self, project_path: str):
        gh = self.get_connection()
        return gh.get_repo(project_path)

    def create_branch(
        self, project, branch: str, source_branch: str, protect: bool = False
    ) -> None:
        try:
            source_ref = project.get_branch(source_branch)
            project.create_git_ref(
                ref=f"refs/heads/{branch}",
                sha=source_ref.commit.sha,
            )
            logger.info(f"Branch '{branch}' created from '{source_branch}'")

            if protect:
                branch_obj = project.get_branch(branch)
                branch_obj.edit_protection()
                logger.info(f"Branch '{branch}' protected")

        except GithubException as e:
            if e.status == 422:
                logger.warning(f"Branch '{branch}' already exists, continuing...")
            else:
                raise

    def commit_files(
        self, project, branch: str, actions: list, message: str | None = None
    ) -> str | None:
        if message is None:
            message = branch
        try:
            ref = project.get_git_ref(f"heads/{branch}")
            base_tree = project.get_git_tree(ref.object.sha)

            tree_elements = []
            for action in actions:
                from github import InputGitTreeElement

                tree_elements.append(
                    InputGitTreeElement(
                        path=action["file_path"],
                        mode="100644",
                        type="blob",
                        content=action["content"],
                    )
                )

            new_tree = project.create_git_tree(tree_elements, base_tree)
            parent = project.get_git_commit(ref.object.sha)
            commit = project.create_git_commit(message, new_tree, [parent])
            ref.edit(commit.sha)

            commit_url = f"{project.html_url}/commit/{commit.sha}"
            logger.info(f"Commit created: {commit_url}")
            return commit_url
        except GithubException as e:
            logger.error(f"Failed to create commit: {e}")
            return None

    def create_merge_request(
        self, project, source_branch: str, target_branch: str
    ) -> str:
        try:
            pr = project.create_pull(
                title=source_branch,
                body="",
                head=source_branch,
                base=target_branch,
            )
            logger.info(f"Pull request created: {pr.html_url}")
            return pr.html_url
        except GithubException as e:
            if e.status == 422:
                pulls = project.get_pulls(
                    state="open", head=source_branch, base=target_branch
                )
                for pr in pulls:
                    logger.warning(f"Existing pull request found: {pr.html_url}")
                    return pr.html_url
            raise

    def create_project(
        self, name: str, namespace_path: str, visibility: str = "private"
    ):
        gh = self.get_connection()
        if namespace_path:
            try:
                org = gh.get_organization(namespace_path)
                repo = org.create_repo(
                    name=name,
                    private=(visibility == "private"),
                    auto_init=True,
                )
            except GithubException:
                logger.warning(f"Org '{namespace_path}' not found, falling back to personal account")
                user = gh.get_user()
                repo = user.create_repo(
                    name=name,
                    private=(visibility == "private"),
                    auto_init=True,
                )
        else:
            user = gh.get_user()
            repo = user.create_repo(
                name=name,
                private=(visibility == "private"),
                auto_init=True,
            )
        logger.info(f"Project '{name}' created at {repo.html_url}")
        return repo
