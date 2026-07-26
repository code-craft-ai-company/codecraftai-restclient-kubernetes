"""
    .. module:: kubernetesrestclient
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: :class:`KubernetesRestClient` — a pure-Python client for the
               Kubernetes API server.

    The Kubernetes API is plain REST over HTTPS with JSON bodies, so this
    client speaks it directly with ``requests`` rather than depending on the
    official SDK.  Authentication comes from a
    :class:`KubeConfigResolution` — a bearer token, a client-certificate
    pair, or the in-cluster service account.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import json
import os

from typing import Any, Dict, Optional

import requests

from ccai.restclient.kubernetes.apiobject import ApiObject, wrap_api_value
from ccai.restclient.kubernetes.kubeconfigresolver import (
    KubeConfigResolution
)
from ccai.restclient.kubernetes.kubernetesapierror import (
    KubernetesApiRequestError
)


# The API server distinguishes patch semantics by content type; strategic
# merge patch is what kubectl uses for the built-in resource kinds.
PATCH_CONTENT_TYPE = "application/strategic-merge-patch+json"

DEFAULT_TIMEOUT_SECONDS = 60.0


class KubernetesRestClient:
    """
        REST client for one Kubernetes API server.

        The api groups mirror the API server's own grouping and are reached
        through public attributes: ``core_v1``, ``apps_v1``, ``batch_v1``,
        ``networking_v1`` and ``version``.
    """

    def __init__(self, *, resolution: KubeConfigResolution,
                 session: Optional[Any] = None,
                 timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS) -> None:
        """
            Construct a KubernetesRestClient.

            :param resolution: The resolved connection material.
            :param session: Optional pre-built ``requests.Session`` — the
                test seam, and the way a caller supplies custom transport
                adapters or proxies.
            :param timeout_seconds: The default per-request timeout.
        """
        self._resolution: KubeConfigResolution = resolution
        self._timeout_seconds: float = timeout_seconds

        if session is not None:
            self._session = session
        else:
            self._session = self._build_session()

        from ccai.restclient.kubernetes.apigroups.corev1group import (
            CoreV1Group
        )
        from ccai.restclient.kubernetes.apigroups.appsv1group import (
            AppsV1Group
        )
        from ccai.restclient.kubernetes.apigroups.batchv1group import (
            BatchV1Group
        )
        from ccai.restclient.kubernetes.apigroups.networkingv1group import (
            NetworkingV1Group
        )
        from ccai.restclient.kubernetes.apigroups.versiongroup import (
            VersionGroup
        )

        self.core_v1: CoreV1Group = CoreV1Group(client=self)
        self.apps_v1: AppsV1Group = AppsV1Group(client=self)
        self.batch_v1: BatchV1Group = BatchV1Group(client=self)
        self.networking_v1: NetworkingV1Group = NetworkingV1Group(
            client=self)
        self.version: VersionGroup = VersionGroup(client=self)
        return

    @property
    def resolution(self) -> KubeConfigResolution:
        """
            Return the resolved connection material.

            :returns: The :class:`KubeConfigResolution`.
        """
        rtnval = self._resolution
        return rtnval

    @property
    def server_url(self) -> str:
        """
            Return the API server base URL.

            :returns: The server URL.
        """
        rtnval = self._resolution.server_url
        return rtnval

    def _build_session(self) -> Any:
        """
            Build a ``requests.Session`` carrying the resolved credential
            and TLS material.

            :returns: The configured session.
        """
        session = requests.Session()

        if self._resolution.token is not None:
            session.headers.update({
                "Authorization": "Bearer {}".format(self._resolution.token)
            })

        session.headers.update({"Accept": "application/json"})

        if self._resolution.verify is False:
            session.verify = False
        elif self._resolution.ca_path is not None:
            session.verify = self._resolution.ca_path
        else:
            session.verify = True

        if self._resolution.client_cert_path is not None:
            if self._resolution.client_key_path is not None:
                session.cert = (self._resolution.client_cert_path,
                                self._resolution.client_key_path)
            else:
                session.cert = self._resolution.client_cert_path

        rtnval = session
        return rtnval

    def request(self, *, method: str, path: str,
                params: Optional[Dict[str, Any]] = None,
                body: Optional[Dict[str, Any]] = None,
                content_type: Optional[str] = None,
                timeout_seconds: Optional[float] = None) -> ApiObject:
        """
            Perform one API-server request and return the decoded body.

            :param method: The HTTP method.
            :param path: The API path, beginning with ``/``.
            :param params: Optional query parameters; ``None`` values are
                dropped so an unset label selector is simply absent.
            :param body: Optional JSON request body.
            :param content_type: Optional explicit content type (patch
                requests need a patch-specific type).
            :param timeout_seconds: Optional per-request timeout override.

            :returns: The decoded response as an :class:`ApiObject`; an
                empty :class:`ApiObject` when the response carries no body.

            :raises: :class:`KubernetesApiRequestError` on a non-success
                status.
        """
        url = "{}{}".format(self._resolution.server_url.rstrip("/"), path)

        query: Dict[str, Any] = {}
        if params is not None:
            for key, value in params.items():
                if value is not None:
                    query[key] = value

        headers: Dict[str, str] = {}
        payload = None
        if body is not None:
            payload = json.dumps(body)
            if content_type is not None:
                headers["Content-Type"] = content_type
            else:
                headers["Content-Type"] = "application/json"

        timeout = timeout_seconds
        if timeout is None:
            timeout = self._timeout_seconds

        response = self._session.request(method, url, params=query,
                                         data=payload, headers=headers,
                                         timeout=timeout)

        status = getattr(response, "status_code", 0)

        if status < 200 or status >= 300:
            text = getattr(response, "text", "")
            reason = getattr(response, "reason", "")
            api_reason = reason
            try:
                decoded = response.json()
                if isinstance(decoded, dict) is True:
                    api_reason = decoded.get("reason", reason)
                    if api_reason is None or len(str(api_reason)) == 0:
                        api_reason = decoded.get("message", reason)
            except Exception:
                api_reason = reason

            err_msg_lines = ["The Kubernetes API request failed."]
            err_msg_lines.append("METHOD: {}".format(method))
            err_msg_lines.append("PATH: {}".format(path))
            err_msg_lines.append("STATUS: {}".format(status))
            err_msg_lines.append("REASON: {}".format(api_reason))
            err_msg = os.linesep.join(err_msg_lines)
            raise KubernetesApiRequestError(err_msg, status=status,
                                            reason=str(api_reason),
                                            body=text)

        text = getattr(response, "text", "")
        if text is None or len(text.strip()) == 0:
            rtnval = ApiObject()
            return rtnval

        try:
            decoded = response.json()
        except Exception:
            rtnval = ApiObject()
            return rtnval

        wrapped = wrap_api_value(decoded)
        if isinstance(wrapped, ApiObject) is True:
            rtnval = wrapped
            return rtnval

        rtnval = ApiObject({"items": wrapped})
        return rtnval
