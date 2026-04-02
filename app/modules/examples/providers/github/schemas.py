from pydantic import BaseModel, Field

# --- Schema ---

class TestGithubProviderParams(BaseModel):
    project_owner: str = Field(default="", alias="project-owner", description="GitHub org or user (leave empty for personal account)")
    image_repo: str = Field(alias="image-repo", description="Container registry URL")
    image_tag: str = Field(alias="image-tag", description="Container image tag")
    app_name: str = Field(alias="app-name", description="Name of the service and repository to create")
    base_image: str = Field(alias="base-image", description="Docker base image")
    container_port: int = Field(alias="container-port", description="Port the app listens on")
    replica_count: int = Field(default=2, alias="replica-count", description="Number of pod replicas")
    env: str = Field(default="staging", description="Deployment environment (e.g., staging, production)")

    model_config = {"populate_by_name": True}
