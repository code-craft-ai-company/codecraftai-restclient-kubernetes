"""
    .. module:: test_kubernetesrestclient
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Tests for the Kubernetes REST client — request shaping, auth
               material, error mapping, and the api-group paths.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from ccai import testbase

from ccai.restclient.kubernetes.apiobject import ApiObject
from ccai.restclient.kubernetes.kubeconfigresolver import (
    KubeConfigResolution
)
from ccai.restclient.kubernetes.kubernetesapierror import (
    KubernetesApiRequestError
)
from ccai.restclient.kubernetes.kubernetesrestclient import (
    KubernetesRestClient, PATCH_CONTENT_TYPE
)

from .fakesession import (
    FakeResponse, FakeSession
)


def _client(session=None, resolution=None):
    if session is None:
        session = FakeSession()
    if resolution is None:
        resolution = KubeConfigResolution(
            server_url="https://k8s.example.com:6443", token="tkn")
    rtnval = KubernetesRestClient(resolution=resolution, session=session)
    return rtnval


def test_token_becomes_a_bearer_header():
    """
        A resolved token is sent as an Authorization header.
    """
    resolution = KubeConfigResolution(server_url="https://k8s:6443",
                                      token="abc123")
    client = KubernetesRestClient(resolution=resolution)
    assert client._session.headers["Authorization"] == "Bearer abc123"
    return


def test_ca_path_becomes_the_verify_target():
    """
        A CA bundle path is used for TLS verification.
    """
    resolution = KubeConfigResolution(server_url="https://k8s:6443",
                                      token="t", ca_path="/tmp/ca.pem")
    client = KubernetesRestClient(resolution=resolution)
    assert client._session.verify == "/tmp/ca.pem"
    return


def test_client_certificate_pair_is_applied():
    """
        A client-cert pair is applied for mTLS.
    """
    resolution = KubeConfigResolution(
        server_url="https://k8s:6443", client_cert_path="/tmp/c.pem",
        client_key_path="/tmp/k.pem")
    client = KubernetesRestClient(resolution=resolution)
    assert client._session.cert == ("/tmp/c.pem", "/tmp/k.pem")
    return


def test_insecure_resolution_disables_verification():
    """
        A resolution with verify=False disables TLS verification.
    """
    resolution = KubeConfigResolution(server_url="https://k8s:6443",
                                      token="t", verify=False)
    client = KubernetesRestClient(resolution=resolution)
    assert client._session.verify is False
    return


def test_namespaced_create_targets_the_right_path():
    """
        Creating a job POSTs to the batch/v1 namespaced jobs collection.
    """
    session = FakeSession()
    client = _client(session=session)

    client.batch_v1.create_namespaced_job(namespace="lab",
                                          body={"metadata": {"name": "j"}})

    call = session.calls[-1]
    assert call["method"] == "POST"
    assert call["url"].endswith("/apis/batch/v1/namespaces/lab/jobs")
    assert call["body"] == {"metadata": {"name": "j"}}
    return


def test_cluster_scoped_list_targets_the_core_collection():
    """
        Listing nodes GETs the core/v1 cluster-scoped nodes collection.
    """
    session = FakeSession()
    client = _client(session=session)

    client.core_v1.list_node()

    call = session.calls[-1]
    assert call["method"] == "GET"
    assert call["url"].endswith("/api/v1/nodes")
    return


def test_label_selector_becomes_a_query_parameter():
    """
        A label selector is sent as labelSelector.
    """
    session = FakeSession()
    client = _client(session=session)

    client.core_v1.list_node(label_selector="pool=gpu")

    assert session.calls[-1]["params"]["labelSelector"] == "pool=gpu"
    return


def test_absent_selectors_are_omitted_entirely():
    """
        Unset selectors must not be sent as empty parameters — the API
        server treats an empty selector differently from an absent one.
    """
    session = FakeSession()
    client = _client(session=session)

    client.core_v1.list_node()

    params = session.calls[-1]["params"]
    assert "labelSelector" not in params
    assert "fieldSelector" not in params
    return


def test_patch_uses_strategic_merge_content_type():
    """
        Patches carry the strategic-merge content type kubectl uses.
    """
    session = FakeSession()
    client = _client(session=session)

    client.apps_v1.patch_namespaced_deployment(
        name="web", namespace="lab", body={"spec": {"replicas": 3}})

    call = session.calls[-1]
    assert call["method"] == "PATCH"
    assert call["headers"]["Content-Type"] == PATCH_CONTENT_TYPE
    return


def test_ingress_group_uses_the_networking_api_prefix():
    """
        Ingresses live under networking.k8s.io/v1.
    """
    session = FakeSession()
    client = _client(session=session)

    client.networking_v1.list_namespaced_ingress(namespace="lab")

    assert session.calls[-1]["url"].endswith(
        "/apis/networking.k8s.io/v1/namespaces/lab/ingresses")
    return


def test_statefulset_plural_is_the_wire_spelling():
    """
        The wire plural is 'statefulsets', not 'stateful_sets'.
    """
    session = FakeSession()
    client = _client(session=session)

    client.apps_v1.read_namespaced_stateful_set(name="db", namespace="lab")

    assert session.calls[-1]["url"].endswith(
        "/apis/apps/v1/namespaces/lab/statefulsets/db")
    return


def test_pvc_plural_is_the_wire_spelling():
    """
        The wire plural is 'persistentvolumeclaims'.
    """
    session = FakeSession()
    client = _client(session=session)

    client.core_v1.read_namespaced_persistent_volume_claim(
        name="data", namespace="lab")

    assert session.calls[-1]["url"].endswith(
        "/api/v1/namespaces/lab/persistentvolumeclaims/data")
    return


def test_version_endpoint_is_read():
    """
        get_code reads /version and exposes gitVersion by both spellings.
    """
    session = FakeSession()
    session.queue(method="GET", path="/version",
                  response=FakeResponse(payload={"gitVersion": "v1.29.3"}))
    client = _client(session=session)

    version_info = client.version.get_code()

    assert version_info.git_version == "v1.29.3"
    assert version_info.gitVersion == "v1.29.3"
    return


def test_failure_status_raises_with_status_reason_and_body():
    """
        A non-success status raises an error carrying the fields consumers
        reclassify on.
    """
    session = FakeSession()
    session.queue(method="GET", path="/api/v1/namespaces/lab/services/web",
                  response=FakeResponse(status_code=404, reason="Not Found",
                                        payload={"reason": "NotFound",
                                                 "message": "no svc"}))
    client = _client(session=session)

    with testbase.raises(KubernetesApiRequestError) as caught:
        client.core_v1.read_namespaced_service(name="web", namespace="lab")

    error = caught.value
    assert error.status == 404
    assert error.reason == "NotFound"
    assert error.body is not None
    return


def test_empty_response_body_yields_an_empty_object():
    """
        A 200 with no body (some deletes) is not an error.
    """
    session = FakeSession()
    session.queue(method="DELETE",
                  path="/api/v1/namespaces/lab/services/web",
                  response=FakeResponse(status_code=200, text=""))
    client = _client(session=session)

    result = client.core_v1.delete_namespaced_service(name="web",
                                                      namespace="lab")
    assert isinstance(result, ApiObject)
    return


def test_list_items_are_attribute_addressable():
    """
        Nested list items keep the attribute addressing consumers rely on.
    """
    session = FakeSession()
    session.queue(method="GET", path="/api/v1/nodes",
                  response=FakeResponse(payload={
                      "items": [{"metadata": {"name": "node-1",
                                              "labels": {"pool": "gpu"}}}]
                  }))
    client = _client(session=session)

    node_list = client.core_v1.list_node()
    first = node_list.items[0]

    assert first.metadata.name == "node-1"
    assert first.metadata.labels["pool"] == "gpu"
    return


def test_missing_field_reads_as_none():
    """
        An absent field reads as None so getattr guards written for the SDK
        keep working.
    """
    obj = ApiObject({"metadata": {"name": "x"}})
    assert obj.status is None
    assert obj.metadata.labels is None
    return
