"""
    .. module:: kubeconfigresolver
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: :class:`KubeConfigResolver` — resolves a kubeconfig source
               into the server URL and TLS / token material needed to reach
               an API server.

    Handles the three sources the fleet uses: a kubeconfig file path, an
    in-memory kubeconfig dict, and the in-cluster service-account context.
    Supports bearer-token auth, client-certificate (mTLS) auth, and custom
    CA bundles — the auth modes real kubeconfigs carry.

    ``exec`` / ``auth-provider`` credential plugins are deliberately NOT
    executed: running an arbitrary helper binary to mint a token is a
    different trust decision than reading a config file, so a kubeconfig
    that requires one is reported as unsupported rather than silently
    shelling out.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import base64
import os
import tempfile

from typing import Dict, List, Optional

import yaml

from ccai.errors.exceptions import SemanticError


# Well-known in-cluster service-account locations, mounted by the kubelet.
IN_CLUSTER_TOKEN_PATH = (
    "/var/run/secrets/kubernetes.io/serviceaccount/token"
)
IN_CLUSTER_CA_PATH = (
    "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
)
IN_CLUSTER_HOST_VARIABLE = "KUBERNETES_SERVICE_HOST"
IN_CLUSTER_PORT_VARIABLE = "KUBERNETES_SERVICE_PORT"


class KubeConfigResolution:
    """
        The resolved connection material for one API server.

        :ivar server_url: The API server base URL.
        :ivar token: The bearer token, or ``None`` when using client certs.
        :ivar ca_path: Path to a CA bundle file, or ``None``.
        :ivar client_cert_path: Path to a client certificate, or ``None``.
        :ivar client_key_path: Path to the client key, or ``None``.
        :ivar verify: ``False`` when the kubeconfig disables TLS
            verification, otherwise ``True``.
        :ivar context: The context name this resolution came from.
    """

    def __init__(self, *, server_url: str, token: Optional[str] = None,
                 ca_path: Optional[str] = None,
                 client_cert_path: Optional[str] = None,
                 client_key_path: Optional[str] = None,
                 verify: bool = True,
                 context: Optional[str] = None) -> None:
        """
            Construct a KubeConfigResolution.

            :param server_url: The API server base URL.
            :param token: Optional bearer token.
            :param ca_path: Optional CA bundle path.
            :param client_cert_path: Optional client certificate path.
            :param client_key_path: Optional client key path.
            :param verify: Whether TLS verification is enabled.
            :param context: The originating context name.
        """
        self.server_url: str = server_url
        self.token: Optional[str] = token
        self.ca_path: Optional[str] = ca_path
        self.client_cert_path: Optional[str] = client_cert_path
        self.client_key_path: Optional[str] = client_key_path
        self.verify: bool = verify
        self.context: Optional[str] = context
        return


def _write_temp_pem(*, data_b64: str, suffix: str) -> str:
    """
        Materialise base64 PEM data from a kubeconfig into a temp file.

        ``requests`` takes CA bundles and client certs as filesystem paths,
        while kubeconfigs embed them base64-inline, so embedded material has
        to be written out.  The file is created with owner-only permissions
        because it may carry a private key.

        :param data_b64: The base64-encoded PEM text.
        :param suffix: The file suffix to use.

        :returns: The path of the written file.
    """
    decoded = base64.b64decode(data_b64)
    handle = tempfile.NamedTemporaryFile(mode="wb", suffix=suffix,
                                         delete=False)
    try:
        os.chmod(handle.name, 0o600)
        handle.write(decoded)
    finally:
        handle.close()
    rtnval = handle.name
    return rtnval


class KubeConfigResolver:
    """
        Resolves a kubeconfig source into a :class:`KubeConfigResolution`.

        Exactly one of ``kubeconfig_path``, ``kubeconfig_dict`` or
        ``in_cluster`` must be supplied.
    """

    def __init__(self, *, kubeconfig_path: Optional[str] = None,
                 kubeconfig_dict: Optional[Dict[str, object]] = None,
                 in_cluster: bool = False,
                 context: Optional[str] = None) -> None:
        """
            Construct a KubeConfigResolver.

            :param kubeconfig_path: Filesystem path of a kubeconfig file.
            :param kubeconfig_dict: An in-memory kubeconfig dict.
            :param in_cluster: When ``True`` use the in-cluster context.
            :param context: The named context to activate.

            :raises: SemanticError when zero or multiple sources are given.
        """
        sources_supplied: List[str] = []

        if kubeconfig_path is not None:
            sources_supplied.append("kubeconfig_path")
        if kubeconfig_dict is not None:
            sources_supplied.append("kubeconfig_dict")
        if in_cluster is True:
            sources_supplied.append("in_cluster")

        if len(sources_supplied) == 0:
            err_msg_lines = [
                "A kubeconfig source must be supplied.",
                "Provide exactly one of 'kubeconfig_path', "
                "'kubeconfig_dict' or 'in_cluster=True'.",
            ]
            err_msg = os.linesep.join(err_msg_lines)
            raise SemanticError(err_msg) from None

        if len(sources_supplied) > 1:
            err_msg_lines = ["Only one kubeconfig source may be supplied."]
            err_msg_lines.append("SUPPLIED: ({})".format(
                len(sources_supplied)))
            for source_name in sources_supplied:
                err_msg_lines.append("    {}".format(source_name))
            err_msg = os.linesep.join(err_msg_lines)
            raise SemanticError(err_msg) from None

        self.kubeconfig_path: Optional[str] = kubeconfig_path
        self.kubeconfig_dict: Optional[Dict[str, object]] = kubeconfig_dict
        self.in_cluster: bool = in_cluster
        self.context: Optional[str] = context
        return

    def _load_config_dict(self) -> Optional[Dict[str, object]]:
        """
            Return the kubeconfig dict, reading the file when needed.

            :returns: The kubeconfig dict, or ``None`` for in-cluster.
        """
        if self.in_cluster is True:
            rtnval = None
            return rtnval

        if self.kubeconfig_dict is not None:
            rtnval = self.kubeconfig_dict
            return rtnval

        with open(self.kubeconfig_path, "r") as config_handle:
            rtnval = yaml.safe_load(config_handle)
        return rtnval

    def available_contexts(self) -> List[str]:
        """
            Enumerate the context names available in the kubeconfig.

            :returns: The list of context names.  An in-cluster resolver
                yields an empty list because it has no contexts.
        """
        context_names: List[str] = []

        config_dict = self._load_config_dict()
        if config_dict is None:
            rtnval = context_names
            return rtnval

        contexts = config_dict.get("contexts", None)
        if contexts is None:
            rtnval = context_names
            return rtnval

        for context_entry in contexts:
            entry_name = context_entry.get("name", None)
            if entry_name is not None:
                context_names.append(entry_name)

        rtnval = context_names
        return rtnval

    def _resolve_in_cluster(self) -> KubeConfigResolution:
        """
            Resolve the in-cluster service-account context.

            :returns: A :class:`KubeConfigResolution`.

            :raises: SemanticError when the service-account material is
                absent (the process is not running in a cluster).
        """
        host = os.environ.get(IN_CLUSTER_HOST_VARIABLE, None)
        port = os.environ.get(IN_CLUSTER_PORT_VARIABLE, None)

        if host is None or port is None:
            err_msg_lines = ["The in-cluster context is not available."]
            err_msg_lines.append("{} and {} must both be set.".format(
                IN_CLUSTER_HOST_VARIABLE, IN_CLUSTER_PORT_VARIABLE))
            err_msg = os.linesep.join(err_msg_lines)
            raise SemanticError(err_msg) from None

        token = None
        if os.path.exists(IN_CLUSTER_TOKEN_PATH) is True:
            with open(IN_CLUSTER_TOKEN_PATH, "r") as token_handle:
                token = token_handle.read().strip()

        ca_path = None
        if os.path.exists(IN_CLUSTER_CA_PATH) is True:
            ca_path = IN_CLUSTER_CA_PATH

        rtnval = KubeConfigResolution(
            server_url="https://{}:{}".format(host, port),
            token=token, ca_path=ca_path, verify=ca_path is not None,
            context=None)
        return rtnval

    def _select_context_entry(self, *, config_dict: Dict[str, object]
                              ) -> Dict[str, object]:
        """
            Select the active context entry from a kubeconfig.

            :param config_dict: The kubeconfig dict.

            :returns: The selected context entry.

            :raises: SemanticError when the requested context is absent or
                no context can be determined.
        """
        contexts = config_dict.get("contexts", None)
        if contexts is None or len(contexts) == 0:
            err_msg = "The kubeconfig declares no contexts."
            raise SemanticError(err_msg) from None

        wanted = self.context
        if wanted is None:
            wanted = config_dict.get("current-context", None)

        if wanted is None:
            err_msg_lines = ["No kubeconfig context was selected."]
            err_msg_lines.append("Pass 'context=' or set "
                                 "'current-context' in the kubeconfig.")
            err_msg = os.linesep.join(err_msg_lines)
            raise SemanticError(err_msg) from None

        for context_entry in contexts:
            if context_entry.get("name", None) == wanted:
                rtnval = context_entry
                return rtnval

        err_msg_lines = ["The requested kubeconfig context was not found."]
        err_msg_lines.append("REQUESTED: {}".format(wanted))
        err_msg_lines.append("AVAILABLE: ({})".format(len(contexts)))
        for context_entry in contexts:
            err_msg_lines.append("    {}".format(
                context_entry.get("name", "")))
        err_msg = os.linesep.join(err_msg_lines)
        raise SemanticError(err_msg) from None

    def _find_named(self, *, entries: object, name: str,
                    kind: str) -> Dict[str, object]:
        """
            Find a named cluster / user entry in a kubeconfig list.

            :param entries: The list of entries.
            :param name: The name to match.
            :param kind: The entry kind, for error messages.

            :returns: The entry's inner definition dict.

            :raises: SemanticError when the entry is absent.
        """
        if entries is not None:
            for entry in entries:
                if entry.get("name", None) == name:
                    inner = entry.get(kind, None)
                    rtnval = inner if inner is not None else {}
                    return rtnval

        err_msg_lines = ["The kubeconfig {} was not found.".format(kind)]
        err_msg_lines.append("NAME: {}".format(name))
        err_msg = os.linesep.join(err_msg_lines)
        raise SemanticError(err_msg) from None

    def resolve(self) -> KubeConfigResolution:
        """
            Resolve the configured source into connection material.

            :returns: A :class:`KubeConfigResolution`.

            :raises: SemanticError when the kubeconfig is unusable or
                requires an unsupported credential plugin.
        """
        if self.in_cluster is True:
            rtnval = self._resolve_in_cluster()
            return rtnval

        config_dict = self._load_config_dict()
        context_entry = self._select_context_entry(config_dict=config_dict)
        context_name = context_entry.get("name", None)
        context_body = context_entry.get("context", None)
        if context_body is None:
            context_body = {}

        cluster = self._find_named(
            entries=config_dict.get("clusters", None),
            name=context_body.get("cluster", ""), kind="cluster")
        user = self._find_named(
            entries=config_dict.get("users", None),
            name=context_body.get("user", ""), kind="user")

        server_url = cluster.get("server", None)
        if server_url is None:
            err_msg_lines = ["The kubeconfig cluster declares no server."]
            err_msg_lines.append("CONTEXT: {}".format(context_name))
            err_msg = os.linesep.join(err_msg_lines)
            raise SemanticError(err_msg) from None

        for unsupported in ("exec", "auth-provider"):
            if user.get(unsupported, None) is not None:
                err_msg_lines = [
                    "The kubeconfig user requires an unsupported "
                    "credential plugin."
                ]
                err_msg_lines.append("CONTEXT: {}".format(context_name))
                err_msg_lines.append("MECHANISM: {}".format(unsupported))
                err_msg_lines.append(
                    "Supply a bearer token or client certificate instead; "
                    "credential plugins are not executed.")
                err_msg = os.linesep.join(err_msg_lines)
                raise SemanticError(err_msg) from None

        verify = cluster.get("insecure-skip-tls-verify", False) is not True

        ca_path = cluster.get("certificate-authority", None)
        ca_data = cluster.get("certificate-authority-data", None)
        if ca_path is None and ca_data is not None:
            ca_path = _write_temp_pem(data_b64=ca_data, suffix="-ca.pem")

        token = user.get("token", None)

        client_cert_path = user.get("client-certificate", None)
        client_cert_data = user.get("client-certificate-data", None)
        if client_cert_path is None and client_cert_data is not None:
            client_cert_path = _write_temp_pem(data_b64=client_cert_data,
                                               suffix="-cert.pem")

        client_key_path = user.get("client-key", None)
        client_key_data = user.get("client-key-data", None)
        if client_key_path is None and client_key_data is not None:
            client_key_path = _write_temp_pem(data_b64=client_key_data,
                                              suffix="-key.pem")

        if token is None and client_cert_path is None:
            err_msg_lines = ["The kubeconfig user carries no credential."]
            err_msg_lines.append("CONTEXT: {}".format(context_name))
            err_msg_lines.append(
                "A 'token' or a 'client-certificate' pair is required.")
            err_msg = os.linesep.join(err_msg_lines)
            raise SemanticError(err_msg) from None

        rtnval = KubeConfigResolution(
            server_url=server_url, token=token, ca_path=ca_path,
            client_cert_path=client_cert_path,
            client_key_path=client_key_path, verify=verify,
            context=context_name)
        return rtnval
