pipenv run pytest \
  -s \
  -o log_cli=true -o log_cli_level=INFO \
  -m smoke \
    --cluster-type external \
    --kube-config /abs/workdir/kubebox-kubeconfig \
    --chart-path linkerd2-app-0.6.0-beta-27b94b26a29e06b2347245efa4a68fce82abc157.tgz \
    --chart-version 0.6.0-beta-27b94b26a29e06b2347245efa4a68fce82abc157 \
    --chart-extra-info external_cluster_version=1.21.1 \
    --log-cli-level info
