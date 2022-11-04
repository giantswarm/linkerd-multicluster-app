import json
import logging
import os
import shutil
import subprocess  # nosec
import time
from typing import Any

import pykube
import pytest
import requests
import yaml
from pykube import HTTPClient
from pytest_helm_charts.clusters import Cluster
from pytest_helm_charts.giantswarm_app_platform.app import (
    AppCR,
    AppFactoryFunc,
    ConfiguredApp,
)
from pytest_helm_charts.k8s.deployment import wait_for_deployments_to_run
from pytest_helm_charts.k8s.daemon_set import wait_for_daemon_sets_to_run
from pytest_helm_charts.k8s.namespace import ensure_namespace_exists

logger = logging.getLogger(__name__)

timeout: int = 360

cni_namespace = "linkerd-cni"
cni_app_version = "0.8.0"
cni_app_catalog_url = "https://giantswarm.github.io/giantswarm-catalog/"
cni_app_name = "linkerd2-cni"

linkerd_namespace = "linkerd"
linkerd_app_name = "linkerd-control-plane"
linkerd_app_version = "0.8.0"
linkerd_app_catalog_url = "https://giantswarm.github.io/giantswarm-catalog/"

linkerd_multicluster_namespace = "linkerd-multicluster"
linkerd_multicluster_app_name = "linkerd-multicluster"
test_app_namespace = "helloworld"


def get_linkerd_cli(version) -> None:
    url = f"https://github.com/linkerd/linkerd2/releases/download/{version}/linkerd2-cli-{version}-linux-amd64"
    logger.info(f"Downloading linkerd-cli from url '{url}'")
    local_filename = "linkerd-cli"
    if os.path.isfile(local_filename) and os.access(local_filename, os.X_OK):
        return
    with requests.get(url, stream=True) as r:
        with open(local_filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)

    os.chmod(local_filename, 0o755)


def exec_linkerd_cli(kube_config_path, namespace_cni, namespace) -> Any:
    result = subprocess.run(
        [
            "./linkerd-cli",
            "multicluster",
            "check",
            "--kubeconfig",
            kube_config_path,
            "--cni-namespace",
            namespace_cni,
            "--linkerd-namespace",
            namespace,
            "--output",
            "json",
        ],
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=None,
    ).stdout

    return json.loads(result)


def load_yaml_from_path(filepath) -> Any:
    with open(filepath, "r", encoding="utf-8") as values_file:
        values = values_file.read()

    yaml_config = yaml.safe_load(values)
    return yaml_config


def wait_for_all_linkerd_deployments_to_run(
    kube_client: HTTPClient, namespace: str, timeout_sec: int
) -> None:
    wait_for_deployments_to_run(
        kube_client,
        [
            "linkerd-destination",
            "linkerd-identity",
            "linkerd-proxy-injector",
        ],
        namespace,
        timeout_sec,
    )

def wait_for_all_linkerd_multicluster_deployments_to_run(
    kube_client: HTTPClient, namespace: str, timeout_sec: int
) -> None:
    wait_for_deployments_to_run(
        kube_client,
        [
            "linkerd-gateway",
        ],
        namespace,
        timeout_sec,
    )


@pytest.fixture(scope="module")
def linkerd_cni_app_cr(
    kube_cluster: Cluster, app_factory: AppFactoryFunc
) -> ConfiguredApp:
    # app platform is too slow to correctly delete AppCatalog between 'smoke' and 'functional' runs,
    # so to work-around we're adding test type to the name of the created AppCatalog
    # FIXME: this should be provided by the pytest-helm-chart lib, will be fixed there
    #  after that, it can be removed here
    ensure_namespace_exists(kube_cluster.kube_client, cni_namespace)
    res = app_factory(
        cni_app_name,
        cni_app_version,
        f"giantswarm-stable",
        cni_namespace,
        cni_app_catalog_url,
        timeout_sec=timeout,
        namespace="giantswarm",
        deployment_namespace=cni_namespace,
        extra_spec={
            "namespaceConfig": {
                "annotations": {"linkerd.io/inject": "disabled"},
                "labels": {
                    "linkerd.io/cni-resource": "true",
                    "config.linkerd.io/admission-webhooks": "disabled",
                },
            }
        },
    )
    return res


# As the fixture doesn't detect nor manage pre-created appCatalogs,
# it can't manage the one created earlier apptestctl.
# We're registering the same catalog here, just with different name to avoid name conflict.
@pytest.fixture(scope="module")
def linkerd_app_cr(
    app_factory: AppFactoryFunc, linkerd_cni_app_cr: ConfiguredApp
) -> ConfiguredApp:
    res = app_factory(
        linkerd_app_name,
        linkerd_app_version,
        f"giantswarm-stable",
        linkerd_namespace,
        linkerd_app_catalog_url,
        timeout_sec=timeout,
        namespace="giantswarm",
        deployment_namespace=linkerd_namespace,
        config_values=load_yaml_from_path("test-values.yaml"),
        extra_spec={
            "namespaceConfig": {
                "annotations": {"linkerd.io/inject": "disabled"},
                "labels": {
                    "linkerd.io/is-control-plane": "true",
                    "config.linkerd.io/admission-webhooks": "disabled",
                    "linkerd.io/control-plane-ns": linkerd_namespace,
                },
            }
        },
    )
    return res

@pytest.fixture(scope="module")                                                                                                                                                                                                                    
def linkerd_mutlicluster_app_cr(
    app_factory: AppFactoryFunc, chart_version: str
) -> ConfiguredApp:
    res = app_factory(
        linkerd_multicluster_app_name,
        chart_version,
        f"chartmuseum-test-time",
        linkerd_namespace,
        "http://chartmuseum-chartmuseum:8080/charts/",
        timeout_sec=timeout,
        namespace="giantswarm",
        deployment_namespace=linkerd_multicluster_namespace,
        extra_spec={
            "namespaceConfig": {
                "labels": {
                    "linkerd.io/extension": "multicluster",
                },
            }
        },
    )
    return res


@pytest.mark.smoke
def test_api_working(kube_cluster: Cluster) -> None:
    """
    Test if the kubernetes api works
    """
    assert kube_cluster.kube_client is not None
    assert len(pykube.Node.objects(kube_cluster.kube_client)) >= 1

    kube_cluster.kubectl(
        "annotate --overwrite namespace kube-system linkerd.io/inject=disabled"
    )
    kube_cluster.kubectl(
        "label --overwrite namespace kube-system config.linkerd.io/admission-webhooks=disabled"
    )


@pytest.mark.smoke
def test_linkerd_cni_deployed(kube_cluster: Cluster, linkerd_cni_app_cr: AppCR):
    """Install using the linkerd cni"""
    app_cr = (
        AppCR.objects(kube_cluster.kube_client)
        .filter(namespace="giantswarm")
        .get_by_name(cni_app_name)
    )
    app_version = app_cr.obj["status"]["version"]
    wait_for_daemon_sets_to_run(
        kube_cluster.kube_client,
        # this is the name of DaemonSet, not App
        ["linkerd-cni"],
        cni_namespace,
        timeout,
    )
    assert app_version == cni_app_version
    logger.info(f"cni App CR shows installed appVersion {app_version}")


@pytest.mark.smoke
def test_linkerd_deployed(
    kube_cluster: Cluster, linkerd_app_cr: AppCR):
    """Test using the linkerd cli using 'check'"""
    app_cr = (
        AppCR.objects(kube_cluster.kube_client)
        .filter(namespace="giantswarm")
        .get_by_name(linkerd_app_name)
    )
    app_version = app_cr.obj["status"]["version"]
    assert app_version == linkerd_app_version
    wait_for_all_linkerd_deployments_to_run(
        kube_cluster.kube_client, linkerd_namespace, timeout
    )
    logger.info(f"Installed App CR shows installed appVersion {app_version}")


@pytest.mark.smoke
def test_linkerd_multicluster_deployed(
    kube_cluster: Cluster, linkerd_mutlicluster_app_cr: AppCR, chart_version: str
):
    """Test using the linkerd cli using 'check'"""
    app_cr = (
        AppCR.objects(kube_cluster.kube_client)
        .filter(namespace="giantswarm")
        .get_by_name(linkerd_multicluster_app_name)
    )
    app_version = app_cr.obj["status"]["version"]
    assert app_version == chart_version
    wait_for_all_linkerd_multicluster_deployments_to_run(
        kube_cluster.kube_client, linkerd_multicluster_namespace, timeout
    )
    logger.info(f"Installed App CR shows installed appVersion {app_version}")


# FIXME: this should be an upgrade and functional test, but this needs some fixes from
#  pytest-helm-charts lib - otherwise there's a reace condition between deleting the app and
#  starting it again
@pytest.mark.smoke
def test_linkerd_cli_check_passes(kube_cluster: Cluster, linkerd_app_cr: AppCR):
    wait_for_all_linkerd_deployments_to_run(
        kube_cluster.kube_client, linkerd_namespace, timeout
    )
    app_cr = (
        AppCR.objects(kube_cluster.kube_client)
        .filter(namespace="giantswarm")
        .get_by_name(linkerd_app_name)
    )
    app_version = app_cr.obj["status"]["appVersion"]
    kube_cluster.kubectl("apply", filename="test-app-manifests.yaml", output_format="")
    logger.info("Installed additional manifest with app to be included in the mesh")

    get_linkerd_cli(app_version)

    curr = 0
    cli_output = {}
    while curr < timeout:
        cli_output = exec_linkerd_cli(
            kube_cluster.kube_config_path,
            cni_namespace,
            linkerd_namespace,
        )
        if cli_output["success"]:
            break
        time.sleep(1)

    logger.info(f"Final output of 'linkerd check`: {cli_output}")
    assert cli_output["success"]
    kube_cluster.kubectl("delete", filename="test-app-manifests.yaml", output_format="")
