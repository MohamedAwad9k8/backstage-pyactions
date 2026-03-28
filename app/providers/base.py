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
    def create_project(
        self, name: str, namespace_path: str, visibility: str = "private"
    ):
        ...
