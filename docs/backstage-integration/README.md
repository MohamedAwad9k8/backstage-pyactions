# Backstage Integration Guide

This guide covers how to connect Backstage to PyActions so developers can trigger Python automation workflows directly from Backstage templates.

## How It Works

Backstage handles orchestration and the developer-facing UI. PyActions handles execution. When a developer fills out a form in Backstage:

1. Backstage sends the form data to PyActions via a proxy route
2. PyActions runs the corresponding Python automation module
3. Results and logs are returned and displayed in Backstage

This keeps Backstage focused on the user experience while Python handles the heavy lifting.

## Files in This Directory

| File | Description |
|------|-------------|
| `app-config-example.yaml` | Backstage config snippets needed for PyActions integration |
| `templates/test-github-provider.yaml` | Working Backstage template that scaffolds a service via GitHub |
| `templates/test-gitlab-provider.yaml` | Working Backstage template that scaffolds a service via GitLab |

## Prerequisites

- A running Backstage instance ([setup guide](https://backstage.io/docs/getting-started/))
- PyActions deployed and reachable from Backstage (see [Kubernetes Deployment](../k8s-deployment/README.md))
- The HTTP Request Scaffolder Action plugin installed in Backstage

## Step 1: Install an HTTP Request Plugin

Backstage doesn't include a built-in HTTP request scaffolder action, so you need a third-party plugin. A good option is [Roadie's HTTP Request Action](https://roadie.io/backstage/plugins/scaffolder-http-requests/), which is what this project uses.

If Backstage adds a native HTTP request scaffolder action in the future, it can be used directly without needing any third-party plugins.

Install Roadie's plugin in your Backstage project:

```bash
yarn --cwd packages/backend add @roadiehq/scaffolder-backend-module-http-request
```

Import it in your backend (`packages/backend/src/index.ts`):

```typescript
backend.add(import('@roadiehq/scaffolder-backend-module-http-request'));
```

Restart Backstage to apply the changes.

## Step 2: Configure the Proxy

Backstage templates reach PyActions through Backstage's built-in proxy. Add this to your `app-config.yaml`:

```yaml
proxy:
  '/pyactions':
    target: 'http://localhost:8000'
    changeOrigin: true
```

On Kubernetes, replace `localhost:8000` with the PyActions service name (e.g., `http://backstage-pyactions:8000`).

See [app-config-example.yaml](app-config-example.yaml) for the full config reference.

## Step 3: Add Templates

Copy the template files from the `templates/` directory into your Backstage project's templates folder, then register them in `app-config.yaml`:

```yaml
catalog:
  locations:
    - type: file
      target: ../../templates/test-github-provider/template.yaml
      rules:
        - allow: [Template]

    - type: file
      target: ../../templates/test-gitlab-provider/template.yaml
      rules:
        - allow: [Template]
```

Restart Backstage or trigger a catalog refresh to pick up the new templates.

## How the Templates Work

Each template defines a multi-step form that collects input from the developer, then sends it to PyActions via the proxy.

### Template structure

1. **Parameters** — multi-step form with validated inputs (service name, base image, container port, environment, etc.)
2. **Steps**:
   - `http:backstage:request` — sends a POST to PyActions through the proxy (e.g., `/proxy/pyactions/test-github-provider`)
   - `debug:log` — captures and displays the response (status code, logs, MR/PR URLs)
3. **Output** — displays clickable links to the created merge/pull request

### How parameters flow from Backstage to PyActions

```
Backstage form (camelCase)  →  Template body (hyphenated)  →  PyActions schema (alias)
─────────────────────────────────────────────────────────────────────────────────────
parameters.appName          →  "app-name"                  →  app_name: str = Field(alias="app-name")
parameters.containerPort    →  "container-port"            →  container_port: int = Field(alias="container-port")
parameters.replicaCount     →  "replica-count"             →  replica_count: int = Field(alias="replica-count")
```

The template body sends hyphenated keys to match the Pydantic `alias` definitions in PyActions schemas.

## Authentication Between Backstage and PyActions

When both services run in the same Kubernetes namespace, use a NetworkPolicy to restrict access to PyActions (see [Kubernetes Deployment](../k8s-deployment/README.md)). This is the recommended approach and no API token is needed.

For non-Kubernetes setups, PyActions supports a static shared token. Set `API_TOKEN` in PyActions' `.env` and include the token in your template's HTTP request headers:

```yaml
headers:
  Content-Type: 'application/json'
  X-API-Token: your-token
```

This token is static and must be kept in sync between both services. A future improvement would be to validate Backstage's own service tokens instead, which are short-lived and already tied to authenticated requests.

## Why Offload Automation to PyActions?

While Backstage's built-in Scaffolder Actions work for simple workflows, they have limitations:

- Built-in actions are minimal, and many third-party actions are outdated or cause dependency conflicts
- Building custom Scaffolder Actions requires Node.js/TypeScript knowledge
- Most DevOps and Platform Engineering teams already have automation written in Python

By shifting the automation logic to PyActions, Backstage stays focused on orchestration and UI while Python handles execution. DevOps engineers can contribute directly to the automation layer without needing to work with Backstage's plugin system.

## Further Reading

- [Backstage Documentation](https://backstage.io/docs/)
- [Backstage Plugins Directory](https://backstage.io/plugins/)
- [Roadie HTTP Request Plugin](https://roadie.io/backstage/plugins/scaffolder-http-requests/)
