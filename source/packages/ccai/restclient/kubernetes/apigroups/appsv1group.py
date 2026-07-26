"""
    .. module:: appsv1group
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: :class:`AppsV1Group` — the ``/apis/apps/v1`` api group.

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


class AppsV1Group(ResourceGroupBase):
    """
        The ``/apis/apps/v1`` api group.
    """

    api_prefix: str = "/apis/apps/v1"

    def create_namespaced_deployment(self, *, namespace: str,
                                  body: Dict[str, Any],
                                  timeout_seconds: Optional[float] = None
                                  ) -> ApiObject:
        """
            Create a deployment in a namespace.

            :param namespace: The namespace.
            :param body: The resource manifest.
            :param timeout_seconds: Optional request timeout.

            :returns: The created resource.
        """
        rtnval = self.create_namespaced(plural="deployments",
                                        namespace=namespace, body=body,
                                        timeout_seconds=timeout_seconds)
        return rtnval

    def read_namespaced_deployment(self, *, name: str, namespace: str,
                                timeout_seconds: Optional[float] = None
                                ) -> ApiObject:
        """
            Read a deployment.

            :param name: The resource name.
            :param namespace: The namespace.
            :param timeout_seconds: Optional request timeout.

            :returns: The resource.
        """
        rtnval = self.read_namespaced(plural="deployments",
                                      namespace=namespace, name=name,
                                      timeout_seconds=timeout_seconds)
        return rtnval

    def list_namespaced_deployment(self, *, namespace: str,
                                label_selector: Optional[str] = None,
                                field_selector: Optional[str] = None,
                                timeout_seconds: Optional[float] = None
                                ) -> ApiObject:
        """
            List the deployments in a namespace.

            :param namespace: The namespace.
            :param label_selector: Optional label selector.
            :param field_selector: Optional field selector.
            :param timeout_seconds: Optional request timeout.

            :returns: The list response, carrying ``items``.
        """
        rtnval = self.list_namespaced(plural="deployments",
                                      namespace=namespace,
                                      label_selector=label_selector,
                                      field_selector=field_selector,
                                      timeout_seconds=timeout_seconds)
        return rtnval

    def patch_namespaced_deployment(self, *, name: str, namespace: str,
                                 body: Dict[str, Any],
                                 timeout_seconds: Optional[float] = None
                                 ) -> ApiObject:
        """
            Patch a deployment.

            :param name: The resource name.
            :param namespace: The namespace.
            :param body: The patch document.
            :param timeout_seconds: Optional request timeout.

            :returns: The patched resource.
        """
        rtnval = self.patch_namespaced(plural="deployments",
                                       namespace=namespace, name=name,
                                       body=body,
                                       timeout_seconds=timeout_seconds)
        return rtnval

    def delete_namespaced_deployment(self, *, name: str, namespace: str,
                                  body: Optional[Dict[str, Any]] = None,
                                  timeout_seconds: Optional[float] = None
                                  ) -> ApiObject:
        """
            Delete a deployment.

            :param name: The resource name.
            :param namespace: The namespace.
            :param body: Optional delete options.
            :param timeout_seconds: Optional request timeout.

            :returns: The delete response.
        """
        rtnval = self.delete_namespaced(plural="deployments",
                                        namespace=namespace, name=name,
                                        body=body,
                                        timeout_seconds=timeout_seconds)
        return rtnval

    def create_namespaced_stateful_set(self, *, namespace: str,
                                  body: Dict[str, Any],
                                  timeout_seconds: Optional[float] = None
                                  ) -> ApiObject:
        """
            Create a stateful set in a namespace.

            :param namespace: The namespace.
            :param body: The resource manifest.
            :param timeout_seconds: Optional request timeout.

            :returns: The created resource.
        """
        rtnval = self.create_namespaced(plural="statefulsets",
                                        namespace=namespace, body=body,
                                        timeout_seconds=timeout_seconds)
        return rtnval

    def read_namespaced_stateful_set(self, *, name: str, namespace: str,
                                timeout_seconds: Optional[float] = None
                                ) -> ApiObject:
        """
            Read a stateful set.

            :param name: The resource name.
            :param namespace: The namespace.
            :param timeout_seconds: Optional request timeout.

            :returns: The resource.
        """
        rtnval = self.read_namespaced(plural="statefulsets",
                                      namespace=namespace, name=name,
                                      timeout_seconds=timeout_seconds)
        return rtnval

    def list_namespaced_stateful_set(self, *, namespace: str,
                                label_selector: Optional[str] = None,
                                field_selector: Optional[str] = None,
                                timeout_seconds: Optional[float] = None
                                ) -> ApiObject:
        """
            List the stateful sets in a namespace.

            :param namespace: The namespace.
            :param label_selector: Optional label selector.
            :param field_selector: Optional field selector.
            :param timeout_seconds: Optional request timeout.

            :returns: The list response, carrying ``items``.
        """
        rtnval = self.list_namespaced(plural="statefulsets",
                                      namespace=namespace,
                                      label_selector=label_selector,
                                      field_selector=field_selector,
                                      timeout_seconds=timeout_seconds)
        return rtnval

    def patch_namespaced_stateful_set(self, *, name: str, namespace: str,
                                 body: Dict[str, Any],
                                 timeout_seconds: Optional[float] = None
                                 ) -> ApiObject:
        """
            Patch a stateful set.

            :param name: The resource name.
            :param namespace: The namespace.
            :param body: The patch document.
            :param timeout_seconds: Optional request timeout.

            :returns: The patched resource.
        """
        rtnval = self.patch_namespaced(plural="statefulsets",
                                       namespace=namespace, name=name,
                                       body=body,
                                       timeout_seconds=timeout_seconds)
        return rtnval

    def delete_namespaced_stateful_set(self, *, name: str, namespace: str,
                                  body: Optional[Dict[str, Any]] = None,
                                  timeout_seconds: Optional[float] = None
                                  ) -> ApiObject:
        """
            Delete a stateful set.

            :param name: The resource name.
            :param namespace: The namespace.
            :param body: Optional delete options.
            :param timeout_seconds: Optional request timeout.

            :returns: The delete response.
        """
        rtnval = self.delete_namespaced(plural="statefulsets",
                                        namespace=namespace, name=name,
                                        body=body,
                                        timeout_seconds=timeout_seconds)
        return rtnval
