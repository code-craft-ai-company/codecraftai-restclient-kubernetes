"""
    .. module:: resourcegroupbase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: :class:`ResourceGroupBase` — the shared CRUD surface every
               Kubernetes api group is built from.

    Kubernetes resource operations are uniform: the verb and the path shape
    are the same for every kind, only the API prefix and the plural resource
    name change.  This base expresses that once, so each api group is a thin
    declaration of the kinds it owns rather than a repetition of the same
    five requests.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, Optional

from ccai.restclient.kubernetes.apiobject import ApiObject
from ccai.restclient.kubernetes.kubernetesrestclient import (
    PATCH_CONTENT_TYPE
)


class ResourceGroupBase:
    """
        Shared CRUD operations for one API prefix.

        :ivar api_prefix: The API path prefix, e.g. ``/api/v1`` or
            ``/apis/apps/v1``.
    """

    api_prefix: str = ""

    def __init__(self, *, client: Any) -> None:
        """
            Construct a ResourceGroupBase.

            :param client: The owning :class:`KubernetesRestClient`.
        """
        self._client: Any = client
        return

    @property
    def client(self) -> Any:
        """
            Return the owning REST client.

            :returns: The :class:`KubernetesRestClient`.
        """
        rtnval = self._client
        return rtnval

    def _namespaced_path(self, *, namespace: str, plural: str,
                         name: Optional[str] = None) -> str:
        """
            Build a namespaced resource path.

            :param namespace: The namespace.
            :param plural: The plural resource name, e.g. ``jobs``.
            :param name: Optional resource name for item paths.

            :returns: The API path.
        """
        base = "{}/namespaces/{}/{}".format(self.api_prefix, namespace,
                                           plural)
        if name is None:
            rtnval = base
            return rtnval
        rtnval = "{}/{}".format(base, name)
        return rtnval

    def _cluster_path(self, *, plural: str,
                      name: Optional[str] = None) -> str:
        """
            Build a cluster-scoped resource path.

            :param plural: The plural resource name, e.g. ``nodes``.
            :param name: Optional resource name for item paths.

            :returns: The API path.
        """
        base = "{}/{}".format(self.api_prefix, plural)
        if name is None:
            rtnval = base
            return rtnval
        rtnval = "{}/{}".format(base, name)
        return rtnval

    # ---------------------------------------------------- namespaced verbs

    def create_namespaced(self, *, plural: str, namespace: str,
                          body: Dict[str, Any],
                          timeout_seconds: Optional[float] = None
                          ) -> ApiObject:
        """
            Create a namespaced resource.

            :param plural: The plural resource name.
            :param namespace: The namespace.
            :param body: The resource manifest.
            :param timeout_seconds: Optional request timeout.

            :returns: The created resource.
        """
        path = self._namespaced_path(namespace=namespace, plural=plural)
        rtnval = self._client.request(method="POST", path=path, body=body,
                                     timeout_seconds=timeout_seconds)
        return rtnval

    def read_namespaced(self, *, plural: str, namespace: str, name: str,
                        timeout_seconds: Optional[float] = None
                        ) -> ApiObject:
        """
            Read a namespaced resource.

            :param plural: The plural resource name.
            :param namespace: The namespace.
            :param name: The resource name.
            :param timeout_seconds: Optional request timeout.

            :returns: The resource.
        """
        path = self._namespaced_path(namespace=namespace, plural=plural,
                                     name=name)
        rtnval = self._client.request(method="GET", path=path,
                                     timeout_seconds=timeout_seconds)
        return rtnval

    def list_namespaced(self, *, plural: str, namespace: str,
                        label_selector: Optional[str] = None,
                        field_selector: Optional[str] = None,
                        timeout_seconds: Optional[float] = None
                        ) -> ApiObject:
        """
            List namespaced resources.

            :param plural: The plural resource name.
            :param namespace: The namespace.
            :param label_selector: Optional label selector.
            :param field_selector: Optional field selector.
            :param timeout_seconds: Optional request timeout.

            :returns: The list response, carrying ``items``.
        """
        path = self._namespaced_path(namespace=namespace, plural=plural)
        params = {"labelSelector": label_selector,
                  "fieldSelector": field_selector}
        rtnval = self._client.request(method="GET", path=path,
                                     params=params,
                                     timeout_seconds=timeout_seconds)
        return rtnval

    def patch_namespaced(self, *, plural: str, namespace: str, name: str,
                         body: Dict[str, Any],
                         timeout_seconds: Optional[float] = None
                         ) -> ApiObject:
        """
            Patch a namespaced resource with strategic merge semantics.

            :param plural: The plural resource name.
            :param namespace: The namespace.
            :param name: The resource name.
            :param body: The patch document.
            :param timeout_seconds: Optional request timeout.

            :returns: The patched resource.
        """
        path = self._namespaced_path(namespace=namespace, plural=plural,
                                     name=name)
        rtnval = self._client.request(method="PATCH", path=path, body=body,
                                     content_type=PATCH_CONTENT_TYPE,
                                     timeout_seconds=timeout_seconds)
        return rtnval

    def delete_namespaced(self, *, plural: str, namespace: str, name: str,
                          body: Optional[Dict[str, Any]] = None,
                          timeout_seconds: Optional[float] = None
                          ) -> ApiObject:
        """
            Delete a namespaced resource.

            :param plural: The plural resource name.
            :param namespace: The namespace.
            :param name: The resource name.
            :param body: Optional delete options.
            :param timeout_seconds: Optional request timeout.

            :returns: The delete response.
        """
        path = self._namespaced_path(namespace=namespace, plural=plural,
                                     name=name)
        rtnval = self._client.request(method="DELETE", path=path, body=body,
                                     timeout_seconds=timeout_seconds)
        return rtnval

    # ----------------------------------------------- cluster-scoped verbs

    def create_cluster_scoped(self, *, plural: str, body: Dict[str, Any],
                              timeout_seconds: Optional[float] = None
                              ) -> ApiObject:
        """
            Create a cluster-scoped resource.

            :param plural: The plural resource name.
            :param body: The resource manifest.
            :param timeout_seconds: Optional request timeout.

            :returns: The created resource.
        """
        path = self._cluster_path(plural=plural)
        rtnval = self._client.request(method="POST", path=path, body=body,
                                     timeout_seconds=timeout_seconds)
        return rtnval

    def read_cluster_scoped(self, *, plural: str, name: str,
                            timeout_seconds: Optional[float] = None
                            ) -> ApiObject:
        """
            Read a cluster-scoped resource.

            :param plural: The plural resource name.
            :param name: The resource name.
            :param timeout_seconds: Optional request timeout.

            :returns: The resource.
        """
        path = self._cluster_path(plural=plural, name=name)
        rtnval = self._client.request(method="GET", path=path,
                                     timeout_seconds=timeout_seconds)
        return rtnval

    def list_cluster_scoped(self, *, plural: str,
                            label_selector: Optional[str] = None,
                            field_selector: Optional[str] = None,
                            timeout_seconds: Optional[float] = None
                            ) -> ApiObject:
        """
            List cluster-scoped resources.

            :param plural: The plural resource name.
            :param label_selector: Optional label selector.
            :param field_selector: Optional field selector.
            :param timeout_seconds: Optional request timeout.

            :returns: The list response, carrying ``items``.
        """
        path = self._cluster_path(plural=plural)
        params = {"labelSelector": label_selector,
                  "fieldSelector": field_selector}
        rtnval = self._client.request(method="GET", path=path,
                                     params=params,
                                     timeout_seconds=timeout_seconds)
        return rtnval

    def patch_cluster_scoped(self, *, plural: str, name: str,
                             body: Dict[str, Any],
                             timeout_seconds: Optional[float] = None
                             ) -> ApiObject:
        """
            Patch a cluster-scoped resource.

            :param plural: The plural resource name.
            :param name: The resource name.
            :param body: The patch document.
            :param timeout_seconds: Optional request timeout.

            :returns: The patched resource.
        """
        path = self._cluster_path(plural=plural, name=name)
        rtnval = self._client.request(method="PATCH", path=path, body=body,
                                     content_type=PATCH_CONTENT_TYPE,
                                     timeout_seconds=timeout_seconds)
        return rtnval

    def delete_cluster_scoped(self, *, plural: str, name: str,
                              body: Optional[Dict[str, Any]] = None,
                              timeout_seconds: Optional[float] = None
                              ) -> ApiObject:
        """
            Delete a cluster-scoped resource.

            :param plural: The plural resource name.
            :param name: The resource name.
            :param body: Optional delete options.
            :param timeout_seconds: Optional request timeout.

            :returns: The delete response.
        """
        path = self._cluster_path(plural=plural, name=name)
        rtnval = self._client.request(method="DELETE", path=path, body=body,
                                     timeout_seconds=timeout_seconds)
        return rtnval
