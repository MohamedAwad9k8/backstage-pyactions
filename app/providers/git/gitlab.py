import gitlab

from app.core.logging import logger
from app.providers.base import GitProvider


class GitLabProvider(GitProvider):
    def __init__(self, url: str | None, token: str | None):
        if not url or not token:
            raise ValueError("GITLAB_URL and GITLAB_TOKEN are required")
        self._url = url
        self._token = token
        self._connection = None

    def get_connection(self):
        if self._connection is None:
            logger.info("Initializing GitLab connection...")
            self._connection = gitlab.Gitlab(
                self._url, private_token=self._token
            )
            try:
                self._connection.auth()
            except gitlab.exceptions.GitlabAuthenticationError as e:
                self._connection = None
                raise ValueError(f"GitLab authentication failed: {e}") from e
        return self._connection

    def get_project(self, project_path: str):
        gl = self.get_connection()
        return gl.projects.get(project_path)

    def create_branch(
        self, project, branch: str, source_branch: str, protect: bool = False
    ) -> None:
        try:
            project.branches.create({"branch": branch, "ref": source_branch})
            logger.info(f"Branch '{branch}' created from '{source_branch}'")

            if protect:
                try:
                    project.protectedbranches.create(
                        {
                            "name": branch,
                            "push_access_level": 40,
                            "merge_access_level": 40,
                        }
                    )
                    logger.info(f"Branch '{branch}' protected")
                except gitlab.exceptions.GitlabCreateError:
                    logger.warning(f"Branch '{branch}' already protected")

        except gitlab.exceptions.GitlabCreateError:
            logger.warning(f"Branch '{branch}' already exists, continuing...")

    def commit_files(
        self, project, branch: str, actions: list, message: str | None = None
    ) -> str | None:
        if message is None:
            message = branch
        try:
            commit = project.commits.create(
                {
                    "branch": branch,
                    "commit_message": message,
                    "actions": actions,
                }
            )
            commit_url = f"{project.web_url}/-/commit/{commit.id}"
            logger.info(f"Commit created: {commit_url}")
            return commit_url
        except gitlab.exceptions.GitlabCreateError as e:
            logger.error(f"Failed to create commit: {e}")
            return None

    def create_merge_request(
        self, project, source_branch: str, target_branch: str
    ) -> str:
        try:
            mr = project.mergerequests.create(
                {
                    "source_branch": source_branch,
                    "target_branch": target_branch,
                    "title": source_branch,
                    "remove_source_branch": True,
                }
            )
            logger.info(f"Merge request created: {mr.web_url}")
            return mr.web_url
        except gitlab.exceptions.GitlabCreateError:
            mr = next(
                (
                    m
                    for m in project.mergerequests.list(state="opened")
                    if m.source_branch == source_branch
                    and m.target_branch == target_branch
                ),
                None,
            )
            if mr:
                logger.warning(f"Existing merge request found: {mr.web_url}")
                return mr.web_url
            raise

    def create_project(
        self, name: str, namespace_path: str, visibility: str = "private"
    ):
        gl = self.get_connection()

        group = gl.groups.get(namespace_path.strip("/"))

        existing = group.projects.list(search=name)
        for proj in existing:
            if proj.path_with_namespace == f"{namespace_path.strip('/')}/{name}":
                logger.info(f"Project '{name}' already exists at {proj.web_url}")
                return gl.projects.get(proj.id)

        project = gl.projects.create(
            {
                "name": name,
                "namespace_id": group.id,
                "visibility": visibility,
                "initialize_with_readme": True,
            }
        )
        logger.info(f"Project '{name}' created at {project.web_url}")
        return project
