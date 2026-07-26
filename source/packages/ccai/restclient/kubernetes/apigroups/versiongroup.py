"""
    .. module:: versiongroup
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: :class:`VersionGroup` — the ``/version`` endpoint.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Optional

from ccai.restclient.kubernetes.apiobject import ApiObject


class VersionGroup:
    """
        The API server's ``/version`` endpoint.
    """

    def __init__(self, *, client: Any) -> None:
        """
            Construct a VersionGroup.

            :param client: The owning :class:`KubernetesRestClient`.
        """
        self._client: Any = client
        return

    def get_code(self, *, timeout_seconds: Optional[float] = None
                 ) -> ApiObject:
        """
            Read the API server version information.

            The response carries ``gitVersion`` — reachable as
            ``git_version`` too, matching the field name consumers used
            with the official SDK.

            :param timeout_seconds: Optional request timeout.

            :returns: The version payload.
        """
        rtnval = self._client.request(method="GET", path="/version",
                                     timeout_seconds=timeout_seconds)
        return rtnval
