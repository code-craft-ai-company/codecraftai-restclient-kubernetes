"""
    .. module:: networkingv1group
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: :class:`NetworkingV1Group` — the ``/apis/networking.k8s.io/v1`` api group.

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


class NetworkingV1Group(ResourceGroupBase):
    """
        The ``/apis/networking.k8s.io/v1`` api group.
    """

    api_prefix: str = "/apis/networking.k8s.io/v1"

    def create_namespaced_ingress(self, *, namespace: str,
                                  body: Dict[str, Any],
                                  timeout_seconds: Optional[float] = None
                                  ) -> ApiObject:
        """
            Create a ingress in a namespace.

            :param namespace: The namespace.
            :param body: The resource manifest.
            :param timeout_seconds: Optional request timeout.

            :returns: The created resource.
        """
        rtnval = self.create_namespaced(plural="ingresses",
                                        namespace=namespace, body=body,
                                        timeout_seconds=timeout_seconds)
        return rtnval

    def read_namespaced_ingress(self, *, name: str, namespace: str,
                                timeout_seconds: Optional[float] = None
                                ) -> ApiObject:
        """
            Read a ingress.

            :param name: The resource name.
            :param namespace: The namespace.
            :param timeout_seconds: Optional request timeout.

            :returns: The resource.
        """
        rtnval = self.read_namespaced(plural="ingresses",
                                      namespace=namespace, name=name,
                                      timeout_seconds=timeout_seconds)
        return rtnval

    def list_namespaced_ingress(self, *, namespace: str,
                                label_selector: Optional[str] = None,
                                field_selector: Optional[str] = None,
                                timeout_seconds: Optional[float] = None
                                ) -> ApiObject:
        """
            List the ingresss in a namespace.

            :param namespace: The namespace.
            :param label_selector: Optional label selector.
            :param field_selector: Optional field selector.
            :param timeout_seconds: Optional request timeout.

            :returns: The list response, carrying ``items``.
        """
        rtnval = self.list_namespaced(plural="ingresses",
                                      namespace=namespace,
                                      label_selector=label_selector,
                                      field_selector=field_selector,
                                      timeout_seconds=timeout_seconds)
        return rtnval

    def patch_namespaced_ingress(self, *, name: str, namespace: str,
                                 body: Dict[str, Any],
                                 timeout_seconds: Optional[float] = None
                                 ) -> ApiObject:
        """
            Patch a ingress.

            :param name: The resource name.
            :param namespace: The namespace.
            :param body: The patch document.
            :param timeout_seconds: Optional request timeout.

            :returns: The patched resource.
        """
        rtnval = self.patch_namespaced(plural="ingresses",
                                       namespace=namespace, name=name,
                                       body=body,
                                       timeout_seconds=timeout_seconds)
        return rtnval

    def delete_namespaced_ingress(self, *, name: str, namespace: str,
                                  body: Optional[Dict[str, Any]] = None,
                                  timeout_seconds: Optional[float] = None
                                  ) -> ApiObject:
        """
            Delete a ingress.

            :param name: The resource name.
            :param namespace: The namespace.
            :param body: Optional delete options.
            :param timeout_seconds: Optional request timeout.

            :returns: The delete response.
        """
        rtnval = self.delete_namespaced(plural="ingresses",
                                        namespace=namespace, name=name,
                                        body=body,
                                        timeout_seconds=timeout_seconds)
        return rtnval
