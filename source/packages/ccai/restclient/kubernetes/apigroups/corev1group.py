"""
    .. module:: corev1group
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: :class:`CoreV1Group` — the ``/api/v1`` api group.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, Optional

from ccai.restclient.kubernetes.apiobject import ApiObject
from ccai.restclient.kubernetes.apigroups.resourcegroupbase import (
    ResourceGroupBase
)


class CoreV1Group(ResourceGroupBase):
    """
        The ``/api/v1`` api group.
    """

    api_prefix: str = "/api/v1"

    def create_namespaced_service(self, *, namespace: str,
                                  body: Dict[str, Any],
                                  timeout_seconds: Optional[float] = None
                                  ) -> ApiObject:
        """
            Create a service in a namespace.

            :param namespace: The namespace.
            :param body: The resource manifest.
            :param timeout_seconds: Optional request timeout.

            :returns: The created resource.
        """
        rtnval = self.create_namespaced(plural="services",
                                        namespace=namespace, body=body,
                                        timeout_seconds=timeout_seconds)
        return rtnval

    def read_namespaced_service(self, *, name: str, namespace: str,
                                timeout_seconds: Optional[float] = None
                                ) -> ApiObject:
        """
            Read a service.

            :param name: The resource name.
            :param namespace: The namespace.
            :param timeout_seconds: Optional request timeout.

            :returns: The resource.
        """
        rtnval = self.read_namespaced(plural="services",
                                      namespace=namespace, name=name,
                                      timeout_seconds=timeout_seconds)
        return rtnval

    def list_namespaced_service(self, *, namespace: str,
                                label_selector: Optional[str] = None,
                                field_selector: Optional[str] = None,
                                timeout_seconds: Optional[float] = None
                                ) -> ApiObject:
        """
            List the services in a namespace.

            :param namespace: The namespace.
            :param label_selector: Optional label selector.
            :param field_selector: Optional field selector.
            :param timeout_seconds: Optional request timeout.

            :returns: The list response, carrying ``items``.
        """
        rtnval = self.list_namespaced(plural="services",
                                      namespace=namespace,
                                      label_selector=label_selector,
                                      field_selector=field_selector,
                                      timeout_seconds=timeout_seconds)
        return rtnval

    def patch_namespaced_service(self, *, name: str, namespace: str,
                                 body: Dict[str, Any],
                                 timeout_seconds: Optional[float] = None
                                 ) -> ApiObject:
        """
            Patch a service.

            :param name: The resource name.
            :param namespace: The namespace.
            :param body: The patch document.
            :param timeout_seconds: Optional request timeout.

            :returns: The patched resource.
        """
        rtnval = self.patch_namespaced(plural="services",
                                       namespace=namespace, name=name,
                                       body=body,
                                       timeout_seconds=timeout_seconds)
        return rtnval

    def delete_namespaced_service(self, *, name: str, namespace: str,
                                  body: Optional[Dict[str, Any]] = None,
                                  timeout_seconds: Optional[float] = None
                                  ) -> ApiObject:
        """
            Delete a service.

            :param name: The resource name.
            :param namespace: The namespace.
            :param body: Optional delete options.
            :param timeout_seconds: Optional request timeout.

            :returns: The delete response.
        """
        rtnval = self.delete_namespaced(plural="services",
                                        namespace=namespace, name=name,
                                        body=body,
                                        timeout_seconds=timeout_seconds)
        return rtnval

    def create_namespaced_persistent_volume_claim(self, *, namespace: str,
                                  body: Dict[str, Any],
                                  timeout_seconds: Optional[float] = None
                                  ) -> ApiObject:
        """
            Create a persistent volume claim in a namespace.

            :param namespace: The namespace.
            :param body: The resource manifest.
            :param timeout_seconds: Optional request timeout.

            :returns: The created resource.
        """
        rtnval = self.create_namespaced(plural="persistentvolumeclaims",
                                        namespace=namespace, body=body,
                                        timeout_seconds=timeout_seconds)
        return rtnval

    def read_namespaced_persistent_volume_claim(self, *, name: str, namespace: str,
                                timeout_seconds: Optional[float] = None
                                ) -> ApiObject:
        """
            Read a persistent volume claim.

            :param name: The resource name.
            :param namespace: The namespace.
            :param timeout_seconds: Optional request timeout.

            :returns: The resource.
        """
        rtnval = self.read_namespaced(plural="persistentvolumeclaims",
                                      namespace=namespace, name=name,
                                      timeout_seconds=timeout_seconds)
        return rtnval

    def list_namespaced_persistent_volume_claim(self, *, namespace: str,
                                label_selector: Optional[str] = None,
                                field_selector: Optional[str] = None,
                                timeout_seconds: Optional[float] = None
                                ) -> ApiObject:
        """
            List the persistent volume claims in a namespace.

            :param namespace: The namespace.
            :param label_selector: Optional label selector.
            :param field_selector: Optional field selector.
            :param timeout_seconds: Optional request timeout.

            :returns: The list response, carrying ``items``.
        """
        rtnval = self.list_namespaced(plural="persistentvolumeclaims",
                                      namespace=namespace,
                                      label_selector=label_selector,
                                      field_selector=field_selector,
                                      timeout_seconds=timeout_seconds)
        return rtnval

    def patch_namespaced_persistent_volume_claim(self, *, name: str, namespace: str,
                                 body: Dict[str, Any],
                                 timeout_seconds: Optional[float] = None
                                 ) -> ApiObject:
        """
            Patch a persistent volume claim.

            :param name: The resource name.
            :param namespace: The namespace.
            :param body: The patch document.
            :param timeout_seconds: Optional request timeout.

            :returns: The patched resource.
        """
        rtnval = self.patch_namespaced(plural="persistentvolumeclaims",
                                       namespace=namespace, name=name,
                                       body=body,
                                       timeout_seconds=timeout_seconds)
        return rtnval

    def delete_namespaced_persistent_volume_claim(self, *, name: str, namespace: str,
                                  body: Optional[Dict[str, Any]] = None,
                                  timeout_seconds: Optional[float] = None
                                  ) -> ApiObject:
        """
            Delete a persistent volume claim.

            :param name: The resource name.
            :param namespace: The namespace.
            :param body: Optional delete options.
            :param timeout_seconds: Optional request timeout.

            :returns: The delete response.
        """
        rtnval = self.delete_namespaced(plural="persistentvolumeclaims",
                                        namespace=namespace, name=name,
                                        body=body,
                                        timeout_seconds=timeout_seconds)
        return rtnval

    def create_namespace(self, *, body: Dict[str, Any],
                       timeout_seconds: Optional[float] = None
                       ) -> ApiObject:
        """
            Create a namespace.

            :param body: The resource manifest.
            :param timeout_seconds: Optional request timeout.

            :returns: The created resource.
        """
        rtnval = self.create_cluster_scoped(plural="namespaces", body=body,
                                            timeout_seconds=timeout_seconds)
        return rtnval

    def read_namespace(self, *, name: str,
                     timeout_seconds: Optional[float] = None) -> ApiObject:
        """
            Read a namespace.

            :param name: The resource name.
            :param timeout_seconds: Optional request timeout.

            :returns: The resource.
        """
        rtnval = self.read_cluster_scoped(plural="namespaces", name=name,
                                          timeout_seconds=timeout_seconds)
        return rtnval

    def list_namespace(self, *, label_selector: Optional[str] = None,
                     field_selector: Optional[str] = None,
                     timeout_seconds: Optional[float] = None) -> ApiObject:
        """
            List the namespaces in the cluster.

            :param label_selector: Optional label selector.
            :param field_selector: Optional field selector.
            :param timeout_seconds: Optional request timeout.

            :returns: The list response, carrying ``items``.
        """
        rtnval = self.list_cluster_scoped(plural="namespaces",
                                          label_selector=label_selector,
                                          field_selector=field_selector,
                                          timeout_seconds=timeout_seconds)
        return rtnval

    def patch_namespace(self, *, name: str, body: Dict[str, Any],
                      timeout_seconds: Optional[float] = None) -> ApiObject:
        """
            Patch a namespace.

            :param name: The resource name.
            :param body: The patch document.
            :param timeout_seconds: Optional request timeout.

            :returns: The patched resource.
        """
        rtnval = self.patch_cluster_scoped(plural="namespaces", name=name,
                                           body=body,
                                           timeout_seconds=timeout_seconds)
        return rtnval

    def delete_namespace(self, *, name: str,
                       body: Optional[Dict[str, Any]] = None,
                       timeout_seconds: Optional[float] = None
                       ) -> ApiObject:
        """
            Delete a namespace.

            :param name: The resource name.
            :param body: Optional delete options.
            :param timeout_seconds: Optional request timeout.

            :returns: The delete response.
        """
        rtnval = self.delete_cluster_scoped(plural="namespaces", name=name,
                                            body=body,
                                            timeout_seconds=timeout_seconds)
        return rtnval

    def create_node(self, *, body: Dict[str, Any],
                       timeout_seconds: Optional[float] = None
                       ) -> ApiObject:
        """
            Create a node.

            :param body: The resource manifest.
            :param timeout_seconds: Optional request timeout.

            :returns: The created resource.
        """
        rtnval = self.create_cluster_scoped(plural="nodes", body=body,
                                            timeout_seconds=timeout_seconds)
        return rtnval

    def read_node(self, *, name: str,
                     timeout_seconds: Optional[float] = None) -> ApiObject:
        """
            Read a node.

            :param name: The resource name.
            :param timeout_seconds: Optional request timeout.

            :returns: The resource.
        """
        rtnval = self.read_cluster_scoped(plural="nodes", name=name,
                                          timeout_seconds=timeout_seconds)
        return rtnval

    def list_node(self, *, label_selector: Optional[str] = None,
                     field_selector: Optional[str] = None,
                     timeout_seconds: Optional[float] = None) -> ApiObject:
        """
            List the nodes in the cluster.

            :param label_selector: Optional label selector.
            :param field_selector: Optional field selector.
            :param timeout_seconds: Optional request timeout.

            :returns: The list response, carrying ``items``.
        """
        rtnval = self.list_cluster_scoped(plural="nodes",
                                          label_selector=label_selector,
                                          field_selector=field_selector,
                                          timeout_seconds=timeout_seconds)
        return rtnval

    def patch_node(self, *, name: str, body: Dict[str, Any],
                      timeout_seconds: Optional[float] = None) -> ApiObject:
        """
            Patch a node.

            :param name: The resource name.
            :param body: The patch document.
            :param timeout_seconds: Optional request timeout.

            :returns: The patched resource.
        """
        rtnval = self.patch_cluster_scoped(plural="nodes", name=name,
                                           body=body,
                                           timeout_seconds=timeout_seconds)
        return rtnval

    def delete_node(self, *, name: str,
                       body: Optional[Dict[str, Any]] = None,
                       timeout_seconds: Optional[float] = None
                       ) -> ApiObject:
        """
            Delete a node.

            :param name: The resource name.
            :param body: Optional delete options.
            :param timeout_seconds: Optional request timeout.

            :returns: The delete response.
        """
        rtnval = self.delete_cluster_scoped(plural="nodes", name=name,
                                            body=body,
                                            timeout_seconds=timeout_seconds)
        return rtnval
