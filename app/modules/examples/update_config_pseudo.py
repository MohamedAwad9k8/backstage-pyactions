"""
PSEUDO-CODE EXAMPLE — Update Config via Git

This is NOT a runnable module. It demonstrates a simple yet powerful pattern:
reading a config file from a Git repo, appending an entry, and creating a
merge request. This pattern covers a wide range of real-world use cases:

- Whitelisting domains in egress/firewall policies
- Adding IPs to network allowlists
- Adding entries to DNS configurations
- Adding users or roles to RBAC configs
- Registering services in a catalog or registry
- Adding repos to CI/CD pipeline configs

The pattern is always the same: read → modify → commit → MR.
"""

from pydantic import BaseModel, Field


# --- Schema ---

class UpdateConfigParams(BaseModel):
    ticket: str = Field(description="Ticket number for branch naming")
    environment: str = Field(description="Target environment: staging or production")
    entry: str = Field(description="The value to add (e.g., domain name, IP, role name)")
    custom_port: bool = Field(default=False, alias="custom-port")
    port: int = Field(default=0, description="Port number if custom port is needed")
    protocol: str = Field(default="", description="Protocol (tcp, http, etc.)")

    model_config = {"populate_by_name": True}


# --- Handler ---

async def handler(params: UpdateConfigParams):
    """
    Simple config update workflow.

    This reads a config file from a Git repo, appends a new entry,
    and creates a merge request for review. Quick, auditable, and
    follows GitOps principles — every change goes through a PR.
    """

    logs = []
    merge_urls = []

    # --- Initialize git provider ---
    # from app.core.dependencies import get_git_provider
    # git = get_git_provider("gitlab")  # or "github", or omit for .env default

    # =============================================
    # STEP 1: Determine target file and branch
    # =============================================
    # Map the environment to the correct config file and branch.
    # Each team structures this differently.
    #
    # config_map = {
    #     "staging": {"file": "config/allowlist_staging.yaml", "branch": "staging"},
    #     "production": {"file": "config/allowlist_prod.yaml", "branch": "main"},
    # }
    # target = config_map[params.environment]
    # config_file = target["file"]
    # source_branch = target["branch"]
    logs.append(f"Step 1: Target environment '{params.environment}' mapped")

    # =============================================
    # STEP 2: Create branch and read current config
    # =============================================
    #
    # project = git.get_project("your-org/network-config")
    # new_branch = f"{params.ticket}-add-{params.entry}"
    # git.create_branch(project, new_branch, source_branch)
    #
    # file = project.files.get(file_path=config_file, ref=new_branch)
    # current_content = file.decode().decode("utf-8")
    logs.append("Step 2: Branch created, config file read")

    # =============================================
    # STEP 3: Append new entry
    # =============================================
    # The format depends on your config structure. Examples:
    #
    # Simple YAML list:
    #   new_content = current_content + f"\n  - {params.entry}"
    #
    # With optional port/protocol:
    #   if not params.custom_port:
    #       block = f"\n  - name: {params.entry}"
    #   else:
    #       block = "\n".join([
    #           f"\n  - name: {params.entry}",
    #           f"    port: {params.port}",
    #           f"    protocol: {params.protocol}",
    #       ])
    #   new_content = current_content + block
    #
    # JSON config:
    #   import json
    #   config = json.loads(current_content)
    #   config["entries"].append({"name": params.entry})
    #   new_content = json.dumps(config, indent=2)
    logs.append(f"Step 3: Entry '{params.entry}' appended")

    # =============================================
    # STEP 4: Commit and create merge request
    # =============================================
    #
    # file.content = new_content
    # file.save(branch=new_branch, commit_message=f"Add {params.entry} to {config_file}")
    #
    # mr_url = git.create_merge_request(project, new_branch, source_branch)
    # merge_urls.append(mr_url)
    logs.append("Step 4: Changes committed, merge request created")

    return {
        "status": "success",
        "entry": params.entry,
        "environment": params.environment,
        "logs": logs,
        "merge_request_urls": merge_urls,
    }
