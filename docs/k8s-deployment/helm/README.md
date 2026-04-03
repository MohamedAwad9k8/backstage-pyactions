# Backstage PyActions

A Python-powered execution layer for [Backstage](https://backstage.io) automation. Extend Backstage's scaffolder capabilities with Python and reuse your existing automation workflows without rebuilding them as custom scaffolder actions in Node.js/TypeScript.

For full project documentation, see the [GitHub repository](https://github.com/MohamedAwad9k8/backstage-pyactions).

## Prerequisites

- Kubernetes cluster
- Helm 3 installed

## Install

Deploy in the same namespace as Backstage so the NetworkPolicy can restrict traffic to Backstage pods only.

```bash
# Add the Helm repo
helm repo add backstage-pyactions https://mohamedawad9k8.github.io/backstage-pyactions
helm repo update

# Create the namespace (skip if it already exists)
kubectl create namespace backstage

# Install the chart
helm install backstage-pyactions backstage-pyactions/backstage-pyactions -n backstage
```

By default, the chart pulls a pre-built image (`mawad98/backstage-pyactions:demo`) from Docker Hub. To use your own image:

```bash
helm install backstage-pyactions backstage-pyactions/backstage-pyactions \
  --set image.repository=your-registry/backstage-pyactions \
  --set image.tag=v1.0.0 \
  -n backstage
```

## Configuration

Non-sensitive values are stored in a **ConfigMap** (generated from the `env` block in `values.yaml`):

```yaml
env:
  APP_NAME: "Backstage-PyActions"
  APP_PORT: "8000"
  DEBUG: "false"
  GIT_PROVIDER: "gitlab"
  GITLAB_URL: "https://gitlab.com"
```

Sensitive values (tokens) are stored in a **Secret**. Create it before installing the chart:

```bash
kubectl create secret generic pyactions-secrets \
  --from-literal=API_TOKEN=your-api-token \
  --from-literal=GITLAB_TOKEN=your-gitlab-token \
  --from-literal=GITHUB_TOKEN=your-github-token \
  -n backstage
```

All three keys are optional. Only include the ones you need.

## Override Values

You can override any value at install time:

```bash
helm install backstage-pyactions backstage-pyactions/backstage-pyactions \
  --set replicaCount=3 \
  --set resources.limits.memory=512Mi \
  -n backstage
```

Or use a custom values file:

```bash
helm install backstage-pyactions backstage-pyactions/backstage-pyactions -f my-values.yaml -n backstage
```

## Network Policy

PyActions should never be exposed to end users directly. The included NetworkPolicy ensures only Backstage pods can reach PyActions.

Backstage is responsible for authenticating and authorizing users before requests reach PyActions. It offers several ways to configure this, so make sure your Backstage instance has proper auth in place.

By default, only pods labeled `app: backstage` can send traffic to PyActions. To change the allowed labels or disable it:

```yaml
networkPolicy:
  enabled: false  # disable entirely (not recommended)
  backstageLabels:
    app: my-backstage  # or change the label selector
```

## Update the Container Image

```bash
kubectl set image deployment/backstage-pyactions \
  backstage-pyactions=your-registry/backstage-pyactions:v2.0.0 \
  -n backstage
```

Or via Helm:

```bash
helm upgrade backstage-pyactions backstage-pyactions/backstage-pyactions \
  --set image.tag=v2.0.0 \
  -n backstage
```

## Uninstall

```bash
helm uninstall backstage-pyactions -n backstage
```
