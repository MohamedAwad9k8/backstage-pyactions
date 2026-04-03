# Backstage PyActions

A Python-powered execution layer for [Backstage](https://backstage.io) automation. Extend Backstage's scaffolder capabilities with Python and reuse your existing automation workflows without rebuilding them as custom scaffolder actions in Node.js/TypeScript.

> For a full guide on integrating with Backstage scaffolder templates, see [Backstage Integration Guide](docs/backstage-integration/README.md).

## The Problem

Backstage is Node.js-first. Writing custom scaffolder actions means TypeScript, the Backstage plugin SDK, and dealing with plugin update breakages. But most DevOps and Platform Engineering teams already have automation written in Python. Scripts that provision infrastructure, create repos, manage deployments, configure services.

Today, the only way to use those workflows from Backstage is to rewrite them in TypeScript. That's time-consuming, fragile, and often poorly documented.

## The Solution

Backstage PyActions creates a clean separation of concerns:

- **Backstage** handles orchestration and UI - what the developer sees
- **PyActions** handles execution - what actually runs

Your Python automation becomes a backend that Backstage calls over HTTP. No rewriting, no TypeScript, no plugin SDK. Drop in your existing scripts, map them to endpoints, and Backstage can trigger them from scaffolder templates.

This bridges the Node.js and Python ecosystems, letting platform teams use the best tool for each job. Backstage for the developer portal, Python for the automation engine behind it.

## Quick Start

```bash
# Clone and configure
git clone https://github.com/MohamedAwad9k8/backstage-pyactions.git
cd backstage-pyactions
cp .env.example .env
# Edit .env with your settings

# Run with Docker
docker compose up --build

# Or install locally
pip install -e ".[dev]"
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` to see the Swagger UI with all registered endpoints (port depends on `APP_PORT` in your `.env`, defaults to 8000).

### Deployment

This project is designed with **Kubernetes deployment in mind**. The recommended deployment method is via Helm chart. The chart is packaged and available on [ArtifactHub](https://artifacthub.io/packages/search?repo=backstage-pyactions) for easy deployment on Kubernetes.

By default, the Helm chart pulls a pre-built Docker image (`mawad98/backstage-pyactions:demo`) from Docker Hub. This can be overridden with your own image.

For the full Kubernetes deployment guide (configuration, secrets, network policy, upgrades), see [Kubernetes Deployment Guide](docs/k8s-deployment/README.md).

| Method     | Command                                   |
| ---------- | ----------------------------------------- |
| Local      | `uvicorn main:app --reload`               |
| Docker     | `docker compose up --build`               |
| Kubernetes | Via Helm chart, see [K8s Deployment Guide](docs/k8s-deployment/README.md) |

## How It Works

### 1. Define your module

Create a folder under `app/modules/` with a handler function and a Pydantic schema:

```python
# app/modules/my_workflow/schemas.py
from pydantic import BaseModel

class MyParams(BaseModel):
    ticket: str
    service_name: str

# app/modules/my_workflow/module.py
from .schemas import MyParams

async def handler(params: MyParams):
    # Your automation logic here
    return {"status": "success", "service": params.service_name}
```

### 2. Register it in modules.yaml

```yaml
modules:
  - name: My Workflow
    path: app.modules.my_workflow
    route: /my-workflow
    description: Short description shown in API docs
```

### 3. Call it from Backstage

Use an HTTP request action in your Backstage scaffolder template to call your module's endpoint through Backstage's proxy:

```yaml
steps:
  - id: trigger-workflow
    action: http:backstage:request
    input:
      method: 'POST'
      path: '/proxy/pyactions/your-endpoint'
      headers:
        Content-Type: 'application/json'
      body: |
        {
          "param-one": "${{ parameters.paramOne }}",
          "param-two": "${{ parameters.paramTwo }}"
        }
```

For the full Backstage integration setup (installing the HTTP action plugin, proxy configuration, example templates, authentication), see [Backstage Integration Guide](docs/backstage-integration/README.md).

> **Not using Backstage?** Any HTTP client works - CI pipelines, cron jobs, Slack bots, or `curl`.

## Project Structure

```
backstage-pyactions/
├── app/
│   ├── core/                    # Framework - config, discovery, auth, logging
│   ├── providers/               # Optional - Git integrations (GitLab, GitHub)
│   ├── modules/                 # Your workflows go here
│   │   └── examples/
│   │       ├── create_service_pseudo.py    # Pseudo-code: complex multi-step workflow
│   │       ├── update_config_pseudo.py     # Pseudo-code: simple git config update
│   │       ├── list_directory/             # Working demo module
│   │       ├── print_working_dir/          # Working demo module
│   │       └── make_directory/             # Working demo module
│   └── templates/               # Jinja2 templates for scaffolding
│       └── examples/
├── modules.yaml                 # Route-to-module mapping
├── main.py                      # App entry point
├── pyproject.toml               # Dependencies and project config
└── .env.example                 # Configuration reference
```

### Core (framework)

| File                   | Purpose                                                 |
| ---------------------- | ------------------------------------------------------- |
| `core/config.py`       | Pydantic BaseSettings - reads `.env`                    |
| `core/discovery.py`    | Reads `modules.yaml`, registers routes at startup       |
| `core/security.py`     | Static API token validation (see [Security](#security)) |
| `core/dependencies.py` | FastAPI `Depends()` wiring for providers                |
| `core/logging.py`      | Structured logging to stdout                            |

### Providers (optional)

Pre-built Git integrations you can use in your modules. Import them directly or use `Depends()`. If your script already talks to GitLab/GitHub directly, you can ignore providers entirely.

- `providers/git/gitlab.py` - GitLab API operations (repos, branches, commits, MRs)
- `providers/git/github.py` - GitHub API operations (repos, branches, commits, PRs)

### Modules (your code)

Each module is a folder with:

- `module.py` - exports an `async def handler(params)` function
- `schemas.py` - Pydantic model defining expected parameters
- `__init__.py` - empty file required by Python to recognize the folder as an importable package

The framework discovers modules via `modules.yaml` and registers them as POST endpoints. See `create_service_pseudo.py` and `update_config_pseudo.py` for pseudo-code examples of real-world workflows.

### Example Use Cases

The pseudo-code examples demonstrate patterns that cover a wide range of automation workflows:

- **Service scaffolding** - create repos, container registries, GitOps manifests, and CI/CD configs in one request
- **Config updates via Git** - append entries to allowlists, firewall rules, RBAC configs, DNS records, or any config managed in Git
- **Production deployments** - promote services from staging to production by copying configs and creating GitOps apps
- **Infrastructure provisioning** - trigger Terraform, create databases, provision cloud resources
- **Lambda/serverless creation** - scaffold serverless functions with boilerplate

## Backstage Integration

For the full integration guide, including plugin installation, proxy configuration, example templates, and authentication, see [Backstage Integration Guide](docs/backstage-integration/README.md).

## Security

Security is split into two layers:

### Layer 1: Backstage (authentication & authorization)

Backstage handles user-facing security. Users authenticate through Backstage's auth system, and authorization determines which scaffolder templates they can run. By the time a request reaches PyActions, Backstage has already verified the user.

### Layer 2: PyActions (network level)

PyActions itself should not be exposed to end users. It only needs to accept traffic from Backstage.

**On Kubernetes (recommended):** Use a NetworkPolicy to restrict ingress to Backstage pods only. This is sufficient - no API token needed:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: pyactions-allow-backstage-only
spec:
  podSelector:
    matchLabels:
      app: backstage-pyactions
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: backstage
      ports:
        - port: 8000
```

With a NetworkPolicy in place, only Backstage pods can reach PyActions. You can leave `API_TOKEN` unset in your `.env` to disable token validation entirely - the network policy is your security layer.

**Outside Kubernetes (static API token):** For non-Kubernetes deployments, PyActions provides a static shared token mechanism. When `API_TOKEN` is set in `.env`, all incoming requests must include a matching `X-API-Token` header. When `API_TOKEN` is not set, token validation is disabled.

**Future improvement:** Replacing static token with Backstage's own service tokens and validating them through Backstage, they are short-lived and already tied to authenticated requests.

## Logging in Production

The app logs to stdout in structured format, which is the standard approach for containerized applications.

**Recommended:** Use a cluster-level log aggregator to collect and persist logs. Common options:

- **EFK stack** (Elasticsearch + Fluentd/Fluent Bit + Kibana)
- **Loki + Grafana**
- **CloudWatch Logs** (AWS) / **Cloud Logging** (GCP)

These collect stdout from all pods automatically - no code changes needed. Logs persist even when pods restart or crash.

**Fallback:** If you don't have a log aggregator, mount a PersistentVolume to `/var/log/pyactions` and configure the app to write logs to file as well.

## Configuration

All configuration is via environment variables (`.env` file). See `.env.example` for the full list.

| Variable       | Required | Description                                                                                                                       |
| -------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `APP_NAME`     | No       | Application name (default: `Backstage PyActions`)                                                                                 |
| `APP_PORT`     | No       | Port the app listens on (default: `8000`)                                                                                         |
| `DEBUG`        | No       | Enable debug logging (default: `false`)                                                                                           |
| `API_TOKEN`    | No       | Static shared token - if set, all requests must include it in the `X-API-Token` header. If not set, token validation is disabled. |
| `GIT_PROVIDER` | No       | Git backend: `gitlab` or `github` (default: `gitlab`)                                                                             |
| `GITLAB_URL`   | No       | GitLab instance URL                                                                                                               |
| `GITLAB_TOKEN` | No       | GitLab API token                                                                                                                  |
| `GITHUB_TOKEN` | No       | GitHub personal access token                                                                                                      |

## Adding a New Module

### 1. Create the module folder

```
app/modules/your_module/
├── __init__.py      (empty file)
├── schemas.py       (Pydantic model for input parameters)
└── module.py        (handler function with your logic)
```

### 2. Define the input schema

In `schemas.py`, define a Pydantic model describing what parameters your workflow expects:

```python
from pydantic import BaseModel, Field

class YourParams(BaseModel):
    name: str = Field(description="Name of the thing")
    environment: str = Field(default="staging", description="Target environment")
    count: int = Field(default=1, description="How many to create")
```

If Backstage sends parameters with hyphens (e.g., `service-name`), use `Field(alias="service-name")` and add `model_config = {"populate_by_name": True}` to the class.

### 3. Write the handler

In `module.py`, define an `async def handler` function. The function name **must** be `handler`. Its parameter **must** be typed with your Pydantic model, as this is how FastAPI knows how to validate the request body:

```python
from .schemas import YourParams

async def handler(params: YourParams):
    # Your automation logic here
    # Access input via: params.name, params.environment, params.count
    # Access config via: from app.core.config import settings; settings.GITLAB_URL
    # Use providers (optional): from app.providers.git.gitlab import GitLabProvider

    return {"status": "success", "result": f"Created {params.name}"}
```

### 4. Register in modules.yaml

Add one entry:

```yaml
  - name: Your Workflow
    path: app.modules.your_module
    route: /your-endpoint
    description: What this workflow does
```

### 5. Restart the app

Module discovery happens at startup, so restart the app to pick up new modules.

| Deployment        | What to do                                                                   |
| ----------------- | ---------------------------------------------------------------------------- |
| Local (`uvicorn`) | Restart the process, or use `--reload` flag for auto-restart on file changes |
| Docker            | Rebuild and restart: `docker compose up --build`                             |
| Kubernetes        | Rebuild the image, push it, and redeploy the pod                             |

Your endpoint is now live at `POST /your-endpoint` and visible in Swagger at `/docs`.

## Testing Your Own Modules

### Run the full test suite

```bash
python3 -m pytest tests/ -v
```

### Writing tests for a new module

Create a test file in `tests/`:

```python
# tests/test_your_module.py

def test_your_module(client):
    response = client.post(
        "/your-endpoint",
        json={"name": "test", "environment": "staging"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_your_module_validation(client):
    response = client.post("/your-endpoint", json={})
    assert response.status_code == 422
```

The `client` fixture from `conftest.py` gives you a test client that simulates HTTP requests against the full app (with discovery, security, and validation all active) without starting a real server.

### Test with curl

```bash
# Valid request
curl -X POST http://localhost:8000/your-endpoint \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "environment": "staging"}'

# Missing required field, expect 422
curl -X POST http://localhost:8000/your-endpoint \
  -H "Content-Type: application/json" \
  -d '{}'

# With auth enabled (API_TOKEN set in .env)
curl -X POST http://localhost:8000/your-endpoint \
  -H "Content-Type: application/json" \
  -H "X-API-Token: your-token" \
  -d '{"name": "test"}'
```

You can also test interactively via Swagger UI at `http://localhost:8000/docs`.

## License

This project is licensed under the [Apache License 2.0](LICENSE). You are free to use, modify, and distribute it, as long as you preserve the copyright notice and state any changes made.
