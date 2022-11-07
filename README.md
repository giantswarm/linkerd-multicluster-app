# linkerd-multicluster chart

[![CircleCI](https://circleci.com/gh/giantswarm/linkerd-multicluster-app.svg?style=shield)](https://circleci.com/gh/giantswarm/linkerd-multicluster-app)

Linkerd multicluster app allows to configure the Linkerd components that enable multicluster setup for Giant Swarm clusters. Based on the official Linkerd helm charts with a few changes, required to deploy to Giant Swarm clusters.

**Before you install this app, please review this document from start to finish!**

## Quickstart Guide

### Step 1: Pre-installation and Configuration

- Make sure you have [Linkerd control plane app deployed succesfully](https://github.com/giantswarm/linkerd-control-plane-app)
- The Linkerd control planes should have the same trust anchor (you need to generate the certs from a common root CA).

### Step 2: Deploy Linkerd Multicluster App

We recommend deploying the app by applying an `App` CR (Custom Resource) onto your management cluster. Use the [`kubectl gs`](https://docs.giantswarm.io/ui-api/kubectl-gs/) plugin to generate a valid `App` CR with command:

```bash
kubectl gs template app \
  --catalog giantswarm \
  --name linkerd-multicluster \
  --target-namespace linkerd-multicluster \
  --cluster-name <your-cluster-id> \
  --version 0.9.0 \
  --namespace-labels "linkerd.io/extension=multicluster" > linkerd-multicluster-manifest.yaml
```

The final `App` CR should look like this:

```yaml
...
apiVersion: application.giantswarm.io/v1alpha1
kind: App
metadata:
  name: linkerd-multicluster
  namespace: <your-cluster-id>
spec:
  catalog: giantswarm
  kubeConfig:
    inCluster: false
  name: linkerd-multicluster
  namespace: linkerd-multicluster
  namespaceConfig:
    labels:
      linkerd.io/extension: multicluster
  version: 0.9.0
```

### Step 4: After deployment

-

## Troubleshooting

### The service is not replicated to the source cluster

Check the logs on `linkerd-destination` pod in `linkerd` namespace and see if service mirror complains about the connection. Ensure you have linked both clusters.

## Usage with `linkerd` cli

You can use the `linkerd` cli as usual with this app as we're using the default namespaces. (`linkerd` and `linkerd-cni`). You can download it from the [linkerd release page](https://github.com/linkerd/linkerd2/releases/tag/stable-2.12.2).

## Credit

- <https://linkerd.io/2.12/tasks/install-helm/>
