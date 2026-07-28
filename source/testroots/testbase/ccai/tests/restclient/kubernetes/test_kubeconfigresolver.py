"""
    .. module:: test_kubeconfigresolver
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Tests for kubeconfig resolution — source validation, context
               selection, and the auth modes real kubeconfigs carry.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import base64
import os
import tempfile

from pathlib import Path
from unittest.mock import patch

from ccai import testbase
import yaml

from ccai.errors.exceptions import SemanticError

from ccai.restclient.kubernetes.kubeconfigresolver import (
    IN_CLUSTER_HOST_VARIABLE, IN_CLUSTER_PORT_VARIABLE, KubeConfigResolver
)


def _token_config():
    rtnval = {
        "apiVersion": "v1",
        "current-context": "lab",
        "clusters": [{"name": "lab-cluster",
                      "cluster": {"server": "https://k8s.example.com:6443"}}],
        "users": [{"name": "lab-user", "user": {"token": "s3cr3t-token"}}],
        "contexts": [{"name": "lab",
                      "context": {"cluster": "lab-cluster",
                                  "user": "lab-user"}}],
    }
    return rtnval


def test_no_source_is_rejected():
    """
        A resolver with no source names the three valid options.
    """
    with testbase.raises(SemanticError) as caught:
        KubeConfigResolver()
    assert "kubeconfig_path" in str(caught.value)
    return


def test_multiple_sources_are_rejected():
    """
        Ambiguous sources are refused rather than silently ranked.
    """
    with testbase.raises(SemanticError):
        KubeConfigResolver(kubeconfig_path="/tmp/kubeconfig",
                           in_cluster=True)
    return


def test_token_auth_resolves_server_and_token():
    """
        A token kubeconfig yields the server URL and bearer token.
    """
    resolver = KubeConfigResolver(kubeconfig_dict=_token_config())
    resolution = resolver.resolve()

    assert resolution.server_url == "https://k8s.example.com:6443"
    assert resolution.token == "s3cr3t-token"
    assert resolution.context == "lab"
    assert resolution.client_cert_path is None
    return


def test_current_context_is_honoured():
    """
        With no explicit context the kubeconfig's current-context wins.
    """
    config = _token_config()
    config["clusters"].append({"name": "prod-cluster",
                               "cluster": {"server": "https://prod:6443"}})
    config["users"].append({"name": "prod-user",
                            "user": {"token": "prod-token"}})
    config["contexts"].append({"name": "prod",
                               "context": {"cluster": "prod-cluster",
                                           "user": "prod-user"}})
    config["current-context"] = "prod"

    resolution = KubeConfigResolver(kubeconfig_dict=config).resolve()
    assert resolution.server_url == "https://prod:6443"
    return


def test_explicit_context_overrides_current_context():
    """
        An explicit context selection beats current-context.
    """
    config = _token_config()
    config["clusters"].append({"name": "prod-cluster",
                               "cluster": {"server": "https://prod:6443"}})
    config["users"].append({"name": "prod-user",
                            "user": {"token": "prod-token"}})
    config["contexts"].append({"name": "prod",
                               "context": {"cluster": "prod-cluster",
                                           "user": "prod-user"}})

    resolution = KubeConfigResolver(kubeconfig_dict=config,
                                   context="prod").resolve()
    assert resolution.token == "prod-token"
    return


def test_unknown_context_lists_the_available_ones():
    """
        An unknown context names what WAS available — the error a typo
        actually needs.
    """
    with testbase.raises(SemanticError) as caught:
        KubeConfigResolver(kubeconfig_dict=_token_config(),
                           context="ghost").resolve()
    message = str(caught.value)
    assert "ghost" in message
    assert "lab" in message
    return


def test_client_certificate_auth_writes_pem_files():
    """
        Embedded client-cert material is materialised to files, because
        the transport takes paths.
    """
    config = _token_config()
    config["users"] = [{
        "name": "lab-user",
        "user": {
            "client-certificate-data": base64.b64encode(
                b"-----BEGIN CERTIFICATE-----\n").decode("ascii"),
            "client-key-data": base64.b64encode(
                b"-----BEGIN PRIVATE KEY-----\n").decode("ascii"),
        },
    }]

    resolution = KubeConfigResolver(kubeconfig_dict=config).resolve()

    assert resolution.token is None
    assert os.path.exists(resolution.client_cert_path)
    assert os.path.exists(resolution.client_key_path)
    # A private key must not be world readable.
    mode = os.stat(resolution.client_key_path).st_mode & 0o777
    assert mode == 0o600
    return


def test_certificate_authority_data_is_materialised():
    """
        An embedded CA bundle becomes a verify path.
    """
    config = _token_config()
    config["clusters"][0]["cluster"]["certificate-authority-data"] = (
        base64.b64encode(b"-----BEGIN CERTIFICATE-----\n").decode("ascii")
    )

    resolution = KubeConfigResolver(kubeconfig_dict=config).resolve()
    assert os.path.exists(resolution.ca_path)
    assert resolution.verify is True
    return


def test_insecure_skip_tls_verify_is_honoured():
    """
        A kubeconfig that disables verification is obeyed, not overridden.
    """
    config = _token_config()
    config["clusters"][0]["cluster"]["insecure-skip-tls-verify"] = True

    resolution = KubeConfigResolver(kubeconfig_dict=config).resolve()
    assert resolution.verify is False
    return


def test_credential_plugin_is_reported_unsupported():
    """
        An exec-plugin kubeconfig is refused explicitly rather than
        silently executing a helper binary.
    """
    config = _token_config()
    config["users"] = [{"name": "lab-user",
                        "user": {"exec": {"command": "aws"}}}]

    with testbase.raises(SemanticError) as caught:
        KubeConfigResolver(kubeconfig_dict=config).resolve()
    assert "exec" in str(caught.value)
    return


def test_user_without_credential_is_rejected():
    """
        A user with neither token nor client cert cannot authenticate and
        says so at resolve time, not at first request.
    """
    config = _token_config()
    config["users"] = [{"name": "lab-user", "user": {}}]

    with testbase.raises(SemanticError):
        KubeConfigResolver(kubeconfig_dict=config).resolve()
    return


def test_available_contexts_enumerates_names():
    """
        Context enumeration reads the kubeconfig without resolving.
    """
    contexts = KubeConfigResolver(
        kubeconfig_dict=_token_config()).available_contexts()
    assert contexts == ["lab"]
    return


def test_kubeconfig_path_is_read_from_disk():
    """
        A path source is read and parsed.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_file = Path(tmp_dir) / "kubeconfig"
        config_file.write_text(yaml.safe_dump(_token_config()))

        resolution = KubeConfigResolver(
            kubeconfig_path=str(config_file)).resolve()
        assert resolution.token == "s3cr3t-token"
    return


def test_in_cluster_requires_the_service_environment():
    """
        The in-cluster context is refused when the process is not running
        in a cluster.
    """
    # patch.dict snapshots and restores os.environ, so removing the two
    # variables cannot leak into another test in the same process.
    with patch.dict(os.environ):
        os.environ.pop(IN_CLUSTER_HOST_VARIABLE, None)
        os.environ.pop(IN_CLUSTER_PORT_VARIABLE, None)

        with testbase.raises(SemanticError):
            KubeConfigResolver(in_cluster=True).resolve()
    return


def test_in_cluster_builds_the_service_url():
    """
        The in-cluster context composes its URL from the injected service
        environment.
    """
    with patch.dict(os.environ, {IN_CLUSTER_HOST_VARIABLE: "10.96.0.1",
                                 IN_CLUSTER_PORT_VARIABLE: "443"}):
        resolution = KubeConfigResolver(in_cluster=True).resolve()
        assert resolution.server_url == "https://10.96.0.1:443"
    return


def test_in_cluster_has_no_contexts():
    """
        In-cluster operation has no kubeconfig contexts.
    """
    with patch.dict(os.environ, {IN_CLUSTER_HOST_VARIABLE: "10.96.0.1",
                                 IN_CLUSTER_PORT_VARIABLE: "443"}):
        assert KubeConfigResolver(in_cluster=True).available_contexts() == []
    return
