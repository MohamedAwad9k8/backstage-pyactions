import time

from jinja2 import Environment, FileSystemLoader

from app.core.dependencies import get_git_provider
from app.core.logging import ActionLogger
from .schemas import TestGithubProviderParams


async def handler(params: TestGithubProviderParams):
    action_log = ActionLogger()

    git = get_git_provider("github")
    templates = Environment(loader=FileSystemLoader("app/templates/examples"))

    # Render templates
    dockerfile = templates.get_template("docker/Dockerfile.python").render(
        base_image=params.base_image,
        container_port=params.container_port,
    )
    ci_config = templates.get_template("ci/github-actions.yml").render(
        app_name=params.app_name,
        image_repo=params.image_repo,
    )
    helm_values = templates.get_template("helm/values.yml").render(
        app_name=params.app_name,
        replica_count=params.replica_count,
        image_repo=params.image_repo,
        image_tag=params.image_tag,
        container_port=params.container_port,
        env=params.env,
    )
    action_log.append("Templates rendered")

    # Create project and branch
    project = git.create_project(params.app_name, params.project_owner)
    action_log.append(f"Project '{params.app_name}' created")

    # GitHub needs a moment after auto_init before the main branch is available
    for _ in range(5):
        try:
            git.create_branch(project, "init-branch", "main")
            break
        except Exception:
            time.sleep(2)
    action_log.append("Branch 'init-branch' created")

    # Commit files
    file_names = ["Dockerfile", ".github/workflows/ci.yml", "values.yml"]
    actions = [
        {"file_path": "Dockerfile", "content": dockerfile},
        {"file_path": ".github/workflows/ci.yml", "content": ci_config},
        {"file_path": "values.yml", "content": helm_values},
    ]
    git.commit_files(
        project,
        "init-branch",
        actions,
        f"initializing new project, added files: {', '.join(file_names)}",
    )
    action_log.append("Files committed")

    # Create pull request
    pr_url = git.create_merge_request(project, "init-branch", "main")
    action_log.append(f"Pull request created: {pr_url}")

    return {
        "status": "success",
        "pull_request_url": pr_url,
        "logs": action_log.logs,
    }
