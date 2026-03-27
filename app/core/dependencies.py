from app.core.config import settings
from app.providers.base import GitProvider


def get_git_provider(provider: str | None = None) -> GitProvider:
    """Return a GitProvider instance.

    Args:
        provider: "gitlab" or "github". If not specified, falls back to
                  the GIT_PROVIDER value from .env.
    """
    provider = provider or settings.GIT_PROVIDER

    if provider == "gitlab":
        from app.providers.git.gitlab import GitLabProvider

        return GitLabProvider(
            url=settings.GITLAB_URL,
            token=settings.GITLAB_TOKEN,
        )

    if provider == "github":
        from app.providers.git.github import GitHubProvider

        return GitHubProvider(
            token=settings.GITHUB_TOKEN,
        )

    raise ValueError(f"Unsupported git provider: {provider}")
