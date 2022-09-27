
# Upgrade procedure

### Preparing the new version.

Before upgrading the version in this app, preparation steps are needed in the [Upstream repo](https://github.com/giantswarm/linkerd2-upstream). Please refer [here](https://github.com/giantswarm/linkerd2-upstream/blob/main/GIANTSWARM.md) for details.

As a result of those steps, a new branch is expected to be present in the **upstream repo** with the format `giantswarm/A.B.C`, where A.B.C is the desired new version.

### Vendoring

In order to reflect the new version in this App, the next step is to update the `vendor.yml` with the desired version.

For example:

```diff
apiVersion: vendir.k14s.io/v1alpha1
kind: Config
directories:
- path: vendor
  contents:
  - path: linkerd-multicluster
    git:
      url: https://github.com/giantswarm/linkerd2-upstream
-      ref: giantswarm/stable-2.11.4
+      ref: giantswarm/stable-2.12.1
    includePaths:
    - multicluster/charts/linkerd-multicluster/**/*
    - charts/partials/**/*
```

This app relies on [Vendir](https://github.com/vmware-tanzu/carvel-vendir) for vendoring. You need the binary present in your machine to proceed.

### Upgrading

The next step is to upgrade the subcharts running:

```
make upgrade-chart
```

The command runs `vendir sync` and copies the necessary files into the subchart. Any change in the chart must be visible and ready to be commited.

Now, the only step left is to update the `AppVersion` in [helm/linkerd2-multicluster-app/Chart.yaml](https://github.com/giantswarm/linkerd2-multicluster-app/blob/main/helm/linkerd2-multicluster-app/Chart.yaml) and the linkerd-multicluster.linkerdVersion in [helm/linkerd2-multicluster-app/values.yaml](https://github.com/giantswarm/linkerd2-multicluster-app/blob/main/helm/linkerd2-multicluster-app/values.yaml)

### PR and merge

You are ready to commit all the changes and open the PR.
One the PR is reviewed, you can `Squash and Merge`.

