from types import SimpleNamespace
from unittest.mock import Mock

import gitlab
from github import GithubException

from app.providers.git.github import GitHubProvider
from app.providers.git.gitlab import GitLabProvider


def test_github_merge_is_explicit_and_uses_squash():
    provider = object.__new__(GitHubProvider)
    pull_request = Mock(html_url="https://github.com/example/repo/pull/1")
    pull_request.merge.return_value = SimpleNamespace(merged=True, message="merged")
    project = Mock()
    project.get_pulls.return_value = [pull_request]

    provider.merge_merge_request(project, "feature", "main")

    project.get_pulls.assert_called_once_with(state="open", head="feature", base="main")
    pull_request.merge.assert_called_once_with(merge_method="squash")


def test_github_repository_variables_are_created_or_updated():
    provider = object.__new__(GitHubProvider)
    project = Mock()
    existing = SimpleNamespace(value="old")
    project.get_variable.side_effect = [GithubException(404, {}, "missing"), existing]
    existing.edit = Mock(return_value=True)

    provider.create_repository_variables(project, {"NEW_VAR": "one", "OLD_VAR": "two"})

    project.create_variable.assert_called_once_with("NEW_VAR", "one")
    existing.edit.assert_called_once_with("two")


def test_gitlab_merge_is_explicit_and_removes_source_branch():
    provider = object.__new__(GitLabProvider)
    merge_request = Mock(
        source_branch="feature",
        target_branch="main",
        web_url="https://gitlab.example/repo/-/merge_requests/1",
    )
    project = Mock()
    project.mergerequests.list.return_value = [merge_request]

    provider.merge_merge_request(project, "feature", "main")

    merge_request.merge.assert_called_once_with(should_remove_source_branch=True)


def test_gitlab_repository_variables_are_created_or_updated():
    provider = object.__new__(GitLabProvider)
    project = Mock()
    existing = Mock(value="old")
    project.variables.get.side_effect = [
        gitlab.exceptions.GitlabGetError("missing", response_code=404),
        existing,
    ]

    provider.create_repository_variables(project, {"NEW_VAR": "one", "OLD_VAR": "two"})

    project.variables.create.assert_called_once_with({"key": "NEW_VAR", "value": "one"})
    assert existing.value == "two"
    existing.save.assert_called_once_with()
