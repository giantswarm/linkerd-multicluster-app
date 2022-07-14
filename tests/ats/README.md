# linkerd2-multicluster-app tests

We want to ensure this app can be installed without any issues, so we're executing these tests.

## General test flow

- Add giantswarm catalog
- Add giantswarm-test catalog
- Install [linkerd2-cni-app](https://github.com/giantswarm/linkerd2-cni-app) from giantswarm-test catalog
- Install [linkerd2-app](https://github.com/giantswarm/linkerd2-cni-app) from giantswarm-test catalog
- Install this chart
- Install a test app ?
- Execute `linkerd multicluster check --cni-namespace linkerd2-cni-app --linkerd-namespace linkerd2-app --output json`


## Updating the test certificates

These instructions loosely follow the original instructions from [this page](https://linkerd.io/2.11/tasks/generate-certificates/)

The tests use a trust anchor certificate and an issuer certificate with its corresponding key present in the tests values file named `test-values.yaml`.

For now, the expiration date of these testing certificates is 2121-07-22.

In case you want to recreate fresh ones (in 100 years), obtain the `step` cli (we're using `step_linux_0.19.0_amd64.tar.gz` from [here](https://github.com/smallstep/cli/releases/tag/v0.19.0)):

```
step certificate create root.linkerd.cluster.local ca.crt ca.key --profile root-ca --no-password --insecure --not-after=876582h
step certificate create identity.linkerd.cluster.local issuer.crt issuer.key --profile intermediate-ca --not-after=876582h --no-password --insecure --ca ca.crt --ca-key ca.key
```

Now replace contents of files in `test-values.yaml`:

- `ca.crt` content goes into `identityTrustAnchorsPEM`
- `issuer.crt` content goes into `identity.issuer.tls.crtPEM`
- `issuer.key` content goes into `identity.issuer.tls.keyPEM`
