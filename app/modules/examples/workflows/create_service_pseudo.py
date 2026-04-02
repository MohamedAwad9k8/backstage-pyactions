"""
PSEUDO-CODE EXAMPLE — Create New Service

This is NOT a runnable module. It demonstrates what a complex, multi-step
automation workflow looks like when built on this framework. This is the kind
of workflow that makes exposing Python automation to Backstage valuable —
orchestrating multiple systems in a single request.

A real implementation would replace the placeholder paths, repo names, and
logic with your organization's specific infrastructure.
"""

from pydantic import BaseModel, Field
from app.core.logging import ActionLogger


# --- Schema ---

class CreateServiceParams(BaseModel):
    ticket: str = Field(description="Ticket number for branch naming")
    service_name: str = Field(alias="service-name")
    service_path: str = Field(alias="service-path", description="Git namespace/group path")
    db_needed: bool = Field(default=False, alias="db-needed")
    db_name: str = Field(default="", alias="db-name")
    db_type: str = Field(default="", alias="db-type")
    replica_count: str = Field(default="2", alias="replica-count")
    app_domain: str = Field(default="backend", alias="app-domain")
    docker_base_image: str = Field(default="node:18-alpine", alias="docker-base-image")

    model_config = {"populate_by_name": True}


# --- Handler ---

async def handler(params: CreateServiceParams):
    """
    Full service scaffolding workflow.

    This creates everything a new microservice needs:
    1. Container registry entry (via IaC repo)
    2. GitOps application manifest (via GitOps repo)
    3. New Git repository for the service
    4. Initial files committed to the new repo

    Each step creates a branch, commits changes, and opens a merge request
    for review. The response returns all MR URLs so the developer can
    track approvals.
    """

    action_log = ActionLogger()
    merge_urls = []

    # --- Initialize git provider ---
    # from app.core.dependencies import get_git_provider
    # git = get_git_provider("gitlab")  # or "github", or omit for .env default

    # =============================================
    # STEP 1: Register container image repository
    # =============================================
    # Many teams manage container registries (ECR, GCR, ACR) via Terraform
    # or similar IaC. This step modifies the IaC repo to add a new entry.
    #
    # infra_project = git.get_project("your-org/infrastructure")
    # branch = f"{params.ticket}-add-registry-{params.service_name}"
    # git.create_branch(infra_project, branch, "main")
    #
    # # Read current registry config
    # file = infra_project.files.get(file_path="registries/config.tf", ref="main")
    # content = file.decode().decode("utf-8")
    #
    # # Append new registry entry
    # new_entry = f'  "{params.service_name}" = {{}}\n'
    # content = content + new_entry
    #
    # # Commit and create MR
    # actions = [{"action": "update", "file_path": "registries/config.tf", "content": content}]
    # git.commit_files(infra_project, branch, actions, f"Add registry for {params.service_name}")
    # merge_urls.append(git.create_merge_request(infra_project, branch, "main"))
    action_log.append("Step 1: Container registry entry created")

    # =============================================
    # STEP 2: Create GitOps application manifest
    # =============================================
    # If you use ArgoCD, Flux, or similar, you have a repo that defines
    # which apps to deploy. This step adds the new service to that repo.
    #
    # from jinja2 import Environment, FileSystemLoader
    # env = Environment(loader=FileSystemLoader("app/templates/examples"))
    #
    # gitops_project = git.get_project("your-org/gitops-apps")
    # branch = f"{params.ticket}-add-{params.service_name}"
    # git.create_branch(gitops_project, branch, "main")
    #
    # # Render the GitOps app template
    # template = env.get_template("kubernetes/argo-app.yml")
    # rendered = template.render(
    #     app_name=params.service_name,
    #     domain=params.app_domain,
    #     repo_url=f"https://gitlab.example.com/{params.service_path}/{params.service_name}.git",
    #     target_revision="main",
    #     helm_path="helm_values.yml",
    # )
    #
    # actions = [{"action": "create", "file_path": f"{params.app_domain}/{params.service_name}.yml", "content": rendered}]
    # git.commit_files(gitops_project, branch, actions)
    # merge_urls.append(git.create_merge_request(gitops_project, branch, "main"))
    action_log.append("Step 2: GitOps application manifest created")

    # =============================================
    # STEP 3: Create new repository
    # =============================================
    # Create the actual service repo where the team will work.
    #
    # service_project = git.create_project(params.service_name, params.service_path)
    action_log.append("Step 3: Git repository created")

    # =============================================
    # STEP 4: Upload initial scaffolded files
    # =============================================
    # Render templates (Dockerfile, CI config, Helm values) with the
    # service-specific values and commit them to the new repo.
    #
    # # Pick the right Dockerfile template based on the runtime
    # docker_template = "docker/Dockerfile.node" if params.app_domain == "frontend" else "docker/Dockerfile.python"
    # dockerfile = env.get_template(docker_template).render(
    #     base_image=params.docker_base_image,
    #     container_port=params.container_port,
    # )
    # ci_config = env.get_template("ci/gitlab-ci.yml").render(
    #     app_name=params.service_name,
    #     domain=params.app_domain,
    # )
    # helm_values = env.get_template("helm/values.yml").render(
    #     replica_count=params.replica_count,
    #     db_needed=params.db_needed,
    #     db_type=params.db_type,
    #     db_name=params.db_name,
    # )
    #
    # actions = [
    #     {"action": "create", "file_path": "Dockerfile", "content": dockerfile},
    #     {"action": "create", "file_path": ".gitlab-ci.yml", "content": ci_config},
    #     {"action": "create", "file_path": "helm_values.yml", "content": helm_values},
    # ]
    # git.commit_files(service_project, "main", actions, f"{params.ticket} Initial scaffolding")
    #
    # # Create a staging branch from main
    # git.create_branch(service_project, "staging", "main", protect=True)
    action_log.append("Step 4: Initial files scaffolded")

    # =============================================
    # Add Any Other Steps Your Workflow Requires
    # =============================================
    #   Below are some examples of what might follow:
    #   1. API Gateway route registration — Add a route entry to Kong, AWS API Gateway, or an Nginx config repo so external traffic can reach the new service.                     
    #   2. DNS record creation (Cloudflare) — Create a CNAME or A record pointing the service's subdomain to your ingress controller.
    #   3. CDN cache rules — Configure cache policies for static assets or public-facing endpoints (Cloudflare cache rules, CloudFront distribution, etc.).                        
    #   4. Secrets provisioning — Create a Vault path or AWS Secrets Manager entries for the service and inject initial secrets (DB credentials, API keys).                        
    #   5. Monitoring & alerting setup — Register the service in Datadog/Grafana dashboards, create default alert rules (latency, error rate, CPU).                                
    #   6. Slack/Teams notification channel — Create a dedicated alerting channel and wire it up to PagerDuty or OpsGenie for on-call routing.                                     
    #   7. Database provisioning — If db_needed is true, create the database instance, user, and schema via IaC (Terraform) or a managed DB API.                                   
    #   8. Service mesh registration — Add the service to Istio/Linkerd config for mTLS, traffic policies, and retries between services.
    
    # Finally return the response, including all the action logs and merge request URLs for tracking.
    # Backstage makes it easy to display the merge urls, and it has it's own logs, so it's good for auditing as well.
    return {
        "status": "success",
        "service_name": params.service_name,
        "logs": action_log.logs,
        "merge_request_urls": merge_urls,
    }
