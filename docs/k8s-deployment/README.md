# Kubernetes Deployment

Deploy Backstage PyActions to Kubernetes using the included Helm chart.

## Prerequisites

- Kubernetes cluster
- Helm 3 installed
- Container image built and pushed to your registry

## Build and Push the Image

```bash
docker build -t your-registry/backstage-pyactions:latest .
docker push your-registry/backstage-pyactions:latest
```

Update `image.repository` and `image.tag` in `helm/values.yaml` to match.

## Configuration

Non-sensitive values are stored in a **ConfigMap** (generated from the `env` block in `values.yaml`):

```yaml
# values.yaml
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
  --from-literal=GITHUB_TOKEN=your-github-token
```

All three keys are optional. Only include the ones you need.

## Install

Deploy in the same namespace as Backstage so the NetworkPolicy can restrict traffic to Backstage pods only.

### From the Local Chart

If you have the repository cloned:

```bash
# Create the namespace (skip if it already exists)
kubectl create namespace backstage

# Install the chart
helm install backstage-pyactions ./helm -n backstage
```

### From ArtifactHub

```bash
# Add the Helm repo
helm repo add backstage-pyactions https://mohamedawad9k8.github.io/backstage-pyactions
helm repo update

# Create the namespace (skip if it already exists)
kubectl create namespace backstage

# Install the chart, setting your container image
helm install backstage-pyactions backstage-pyactions/backstage-pyactions \
  --set image.repository=your-registry/backstage-pyactions \
  --set image.tag=v1.0.0 \
  -n backstage
```

## Override Values

You can override any value in `values.yaml` at install time:

```bash
helm install backstage-pyactions ./helm \
  --set image.repository=ghcr.io/my-org/backstage-pyactions \
  --set image.tag=v1.0.0 \
  --set replicaCount=3
```

Or use a custom values file:

```bash
helm install backstage-pyactions ./helm -f my-values.yaml
```

## Verify

```bash
# Check pods are running
kubectl get pods -l app=backstage-pyactions

# Check the service
kubectl get svc backstage-pyactions

# Test the health endpoint
kubectl port-forward svc/backstage-pyactions 8000:8000
curl http://localhost:8000/health
```

## Network Policy

PyActions executes automation workflows that may have access to git providers, infrastructure APIs, and internal systems. It should never be exposed to end users directly. The included NetworkPolicy ensures only Backstage pods can reach PyActions — no other service or user in the cluster can send requests to it.

Backstage is responsible for authenticating and authorizing users before requests reach PyActions. It offers several ways to configure this, so make sure your Backstage instance has proper auth in place.

By default, a NetworkPolicy is created that only allows traffic from pods labeled `app: backstage`. To change the allowed labels or disable it:

```yaml
# values.yaml
networkPolicy:
  enabled: false  # disable entirely (not recommended)
  backstageLabels:
    app: my-backstage  # or change the label selector
```

## Update the Container Image

When you have a new version of the app, you can update the deployment image directly:

```bash
kubectl set image deployment/backstage-pyactions \
  backstage-pyactions=your-registry/backstage-pyactions:v2.0.0 \
  -n backstage
```

Or if you installed with Helm, upgrade the release:

```bash
helm upgrade backstage-pyactions ./helm \
  --set image.tag=v2.0.0 \
  -n backstage
```

## Uninstall

```bash
helm uninstall backstage-pyactions -n backstage
```
