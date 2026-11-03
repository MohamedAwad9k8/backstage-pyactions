from abc import ABC, abstractmethod


class GitProvider(ABC):
    """Abstract interface for Git operations."""

    @abstractmethod
    def get_connection(self):
        ...

    @abstractmethod
    def get_project(self, project_path: str):
        ...

    @abstractmethod
    def create_branch(
        self, project, branch: str, source_branch: str, protect: bool = False
    ) -> None:
        ...

    @abstractmethod
    def commit_files(
        self, project, branch: str, actions: list, message: str | None = None
    ) -> str | None:
        ...

    @abstractmethod
    def create_merge_request(
        self, project, source_branch: str, target_branch: str
    ) -> str:
        ...

    @abstractmethod
    def merge_merge_request(
        self, project, source_branch: str, target_branch: str
    ) -> None:
        """Merge the open request for source_branch into target_branch."""
        ...

    @abstractmethod
    def create_repository_variables(
        self, project, variables: dict[str, str]
    ) -> None:
        """Create or update repository-level CI/CD variables."""
        ...

    @abstractmethod
    def create_project(
        self, name: str, namespace_path: str, visibility: str = "private"
    ):
        ...
