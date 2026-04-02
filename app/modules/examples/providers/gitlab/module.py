from jinja2 import Environment, FileSystemLoader

from app.core.dependencies import get_git_provider
from app.core.logging import ActionLogger
from .schemas import TestGitlabProviderParams


async def handler(params: TestGitlabProviderParams):
    action_log = ActionLogger()

    git = get_git_provider("gitlab")
    templates = Environment(loader=FileSystemLoader("app/templates/examples"))

    # Render templates
    dockerfile = templates.get_template("docker/Dockerfile.node").render(
        base_image=params.base_image,
        container_port=params.container_port,
    )
    ci_config = templates.get_template("ci/gitlab-ci.yml").render(
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
    project = git.create_project(params.app_name, params.project_path)
    action_log.append(f"Project '{params.app_name}' created under '{params.project_path}'")
    git.create_branch(project, "init-branch", "main")
    action_log.append("Branch 'init-branch' created")

    # Commit files
    file_names = ["Dockerfile", ".gitlab-ci.yml", "values.yml"]
    actions = [
        {"action": "create", "file_path": "Dockerfile", "content": dockerfile},
        {"action": "create", "file_path": ".gitlab-ci.yml", "content": ci_config},
        {"action": "create", "file_path": "values.yml", "content": helm_values},
    ]
    git.commit_files(
        project,
        "init-branch",
        actions,
        f"initializing new project, added files: {', '.join(file_names)}",
    )
    action_log.append("Files committed")

    # Create merge request
    mr_url = git.create_merge_request(project, "init-branch", "main")
    action_log.append(f"Merge request created: {mr_url}")

    return {
        "status": "success",
        "merge_request_url": mr_url,
        "logs": action_log.logs,
    }
