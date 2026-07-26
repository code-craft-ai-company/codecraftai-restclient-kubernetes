"""
    .. module:: kubernetesapierror
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: :class:`KubernetesApiRequestError` — the transport-level
               error raised for a non-success API-server response.

    This is deliberately a THIN error carrying the HTTP status, reason and
    body.  Consumers own the policy of translating status codes into their
    own typed hierarchies; the transport's job is to report faithfully.
    The attribute names (``status`` / ``reason`` / ``body``) match what the
    official SDK's ``ApiException`` carried, so status-based
    reclassification written against the SDK keeps working unchanged.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Optional


class KubernetesApiRequestError(Exception):
    """
        Raised when the API server returns a non-success status.

        :ivar status: The HTTP status code.
        :ivar reason: The HTTP reason phrase or API-server reason.
        :ivar body: The raw response body text.
    """

    def __init__(self, message: str, *, status: int = 0,
                 reason: str = "", body: Optional[str] = None) -> None:
        """
            Construct a KubernetesApiRequestError.

            :param message: The human-readable error message.
            :param status: The HTTP status code.
            :param reason: The reason phrase.
            :param body: The raw response body.
        """
        super().__init__(message)
        self.status: int = status
        self.reason: str = reason
        self.body: Optional[str] = body
        return
