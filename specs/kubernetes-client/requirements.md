# Requirements

## Introduction

The `kubernetes-client` feature provides a pure-Python REST client for the
Kubernetes API server. The Kubernetes API is plain REST over HTTPS with JSON
bodies, so this package speaks it directly with `requests` rather than
depending on the official `kubernetes` SDK — that keeps the fleet's
pure-Python guarantee and avoids pulling a large vendored client and its
transitive dependency tree into every consumer.

Unlike the cloud venues there is no single endpoint. The target is whatever
cluster the caller is configured for, so credential and endpoint resolution
is the package's first concern: `KubeConfigResolver` turns a kubeconfig file
path, an in-memory kubeconfig dict, or the in-cluster service-account context
into a `KubeConfigResolution`, and `KubernetesRestClient` turns that into a
configured session plus api groups mirroring the API server's own grouping.
Responses come back as `ApiObject`, a `dict` of the wire JSON that is also
attribute addressable in both the wire (`gitVersion`) and snake_case
(`git_version`) spellings, so consumers written against the SDK's object
model keep working while migrating.

This client is consumed by `codecraftai-interop-kubernetes`, whose
`KubeConfigLoader` constructs a `KubernetesRestClient` and hands it to
`KubernetesClient` for the workload-primitive surface.

---

## Requirements

### Requirement 1: Resolve Exactly One Kubeconfig Source

**User Story:** As a caller, I want the kubeconfig source to be declared
unambiguously so that the client never silently guesses which cluster it is
talking to.

#### Acceptance Criteria

1. THE SYSTEM SHALL accept exactly one of `kubeconfig_path`,
   `kubeconfig_dict`, or `in_cluster=True` on `KubeConfigResolver`.
2. WHEN no source is supplied THE SYSTEM SHALL raise `SemanticError` naming
   the three accepted sources.
3. WHEN more than one source is supplied THE SYSTEM SHALL raise
   `SemanticError` listing every source that was supplied.
4. WHEN the caller invokes `available_contexts()` THE SYSTEM SHALL return the
   context names declared by the kubeconfig, and SHALL return an empty list
   for an in-cluster resolver because it has no contexts.

### Requirement 2: Select the Active Context

**User Story:** As a caller with a multi-cluster kubeconfig, I want a named
context honoured so that one config file can address several clusters.

#### Acceptance Criteria

1. WHEN `context=` is supplied THE SYSTEM SHALL resolve that context in
   preference to `current-context`.
2. WHEN `context=` is absent THE SYSTEM SHALL resolve `current-context`.
3. WHEN neither is available THE SYSTEM SHALL raise `SemanticError`
   instructing the caller to pass `context=` or set `current-context`.
4. WHEN the requested context is not present THE SYSTEM SHALL raise
   `SemanticError` naming the requested context and listing the available
   ones.
5. WHEN the context's cluster or user entry is absent from the kubeconfig
   THE SYSTEM SHALL raise `SemanticError` naming the missing entry.

### Requirement 3: Resolve Auth Material From a Kubeconfig

**User Story:** As a caller, I want bearer-token and client-certificate
kubeconfigs to resolve into the material `requests` needs so that both auth
modes real clusters issue are usable without extra handling.

#### Acceptance Criteria

1. WHEN the user entry carries `token` THE SYSTEM SHALL populate
   `KubeConfigResolution.token`; WHEN it carries `client-certificate` /
   `client-key` paths THE SYSTEM SHALL populate `client_cert_path` and
   `client_key_path` from them directly.
2. WHEN the user or cluster entry carries base64-inline
   `client-certificate-data`, `client-key-data`, or
   `certificate-authority-data` THE SYSTEM SHALL materialise each into a
   temporary PEM file created with owner-only (`0o600`) permissions and
   record its path, because `requests` takes these as filesystem paths.
3. WHEN a path form and a data form are both present THE SYSTEM SHALL prefer
   the path form and SHALL NOT write a temporary file.
4. WHEN the cluster entry sets `insecure-skip-tls-verify: true` THE SYSTEM
   SHALL set `verify` to `False`.
5. WHEN the cluster entry declares no `server`, or the user entry carries
   neither a token nor a client certificate, THE SYSTEM SHALL raise
   `SemanticError` naming the context.

### Requirement 4: Refuse Credential Plugins

**User Story:** As an operator, I want a kubeconfig that requires a
credential helper to be reported rather than executed, because running an
arbitrary binary to mint a token is a different trust decision than reading
a config file.

#### Acceptance Criteria

1. WHEN the selected user entry declares `exec` or `auth-provider` THE SYSTEM
   SHALL raise `SemanticError` naming the context and the mechanism, and the
   message SHALL direct the caller to supply a bearer token or a
   client-certificate pair instead.
2. THE SYSTEM SHALL NOT invoke any external process as part of resolution.

### Requirement 5: Resolve the In-Cluster Context

**User Story:** As a workload running inside a cluster, I want the injected
service-account context resolved so that no kubeconfig file has to be mounted.

#### Acceptance Criteria

1. WHEN `in_cluster=True` THE SYSTEM SHALL build the server URL from the
   `KUBERNETES_SERVICE_HOST` and `KUBERNETES_SERVICE_PORT` environment
   variables as `https://<host>:<port>`.
2. WHEN either variable is unset THE SYSTEM SHALL raise `SemanticError`
   naming both variables rather than guessing an endpoint.
3. WHEN the service-account token file exists at
   `/var/run/secrets/kubernetes.io/serviceaccount/token` THE SYSTEM SHALL
   read it and strip surrounding whitespace.
4. WHEN the service-account CA exists at
   `/var/run/secrets/kubernetes.io/serviceaccount/ca.crt` THE SYSTEM SHALL
   use it as the CA bundle and SHALL set `verify` to `True`; otherwise
   `verify` SHALL be `False`.

### Requirement 6: Build a Session From a Resolution

**User Story:** As a caller, I want the resolved material applied to the HTTP
session once at construction so that every request carries the right
credential and TLS settings.

#### Acceptance Criteria

1. WHEN a resolution carries a token THE SYSTEM SHALL set the
   `Authorization: Bearer <token>` header on the session, and SHALL always
   set `Accept: application/json`.
2. WHEN `verify` is `False` THE SYSTEM SHALL disable TLS verification;
   otherwise WHEN `ca_path` is present THE SYSTEM SHALL verify against that
   bundle; otherwise THE SYSTEM SHALL use the default trust store.
3. WHEN the resolution carries a client certificate and key THE SYSTEM SHALL
   set the session certificate to the `(cert, key)` pair; WHEN only a
   certificate is present THE SYSTEM SHALL set it alone.
4. THE SYSTEM SHALL accept a caller-supplied `session=` object, which is both
   the test seam and the way a caller supplies custom transport adapters or
   proxies.

### Requirement 7: Shape and Issue API Requests

**User Story:** As an api group, I want one request primitive with uniform
semantics so that every resource verb is a thin declaration rather than a
repetition of the same HTTP handling.

#### Acceptance Criteria

1. THE SYSTEM SHALL expose `KubernetesRestClient.request(method, path,
   params, body, content_type, timeout_seconds)` as named-only parameters
   and SHALL compose the URL from the resolution's server URL with any
   trailing `/` stripped.
2. WHEN a query parameter's value is `None` THE SYSTEM SHALL drop it, so an
   unset label or field selector is absent from the request rather than sent
   empty.
3. WHEN a body is supplied THE SYSTEM SHALL JSON-encode it and set
   `Content-Type`, defaulting to `application/json` when no explicit content
   type is given.
4. WHEN `timeout_seconds` is not supplied THE SYSTEM SHALL apply the client's
   default of `DEFAULT_TIMEOUT_SECONDS` (60.0 seconds).

### Requirement 8: Report API-Server Failures Faithfully

**User Story:** As a consumer, I want a thin transport error carrying the raw
status so that I own the policy of translating status codes into my own typed
hierarchy.

#### Acceptance Criteria

1. WHEN the response status is outside the 2xx range THE SYSTEM SHALL raise
   `KubernetesApiRequestError` carrying `status`, `reason`, and `body`
   attributes — the names the official SDK's `ApiException` used, so
   status-based reclassification written against the SDK keeps working.
2. WHEN the error body decodes to a JSON object THE SYSTEM SHALL prefer its
   `reason` field, falling back to its `message` field, and then to the HTTP
   reason phrase; WHEN it does not decode THE SYSTEM SHALL fall back to the
   HTTP reason phrase rather than propagating a decode failure.
3. THE error message SHALL name the method, path, status, and reason.
4. THE SYSTEM SHALL NOT map statuses into venue-specific exception types.

### Requirement 9: Return Attribute-Addressable Responses

**User Story:** As a consumer migrating off the official SDK, I want response
fields readable as attributes in either spelling so that field access does not
have to be rewritten.

#### Acceptance Criteria

1. THE SYSTEM SHALL return every successful response as an `ApiObject`, a
   `dict` subclass whose nested dicts and lists are wrapped on access.
2. THE SYSTEM SHALL resolve a field by its wire spelling (`gitVersion`), by
   subscript (`obj["gitVersion"]`), and by its snake_case equivalent
   (`git_version`); WHEN a field is absent THE SYSTEM SHALL return `None`
   rather than raising, matching how the SDK's optional fields behaved.
3. WHEN a payload field collides with an inherited `dict` method — `items`,
   `keys`, `values`, `copy`, `get`, `update`, `clear`, `pop` — THE API field
   SHALL win on attribute access, because `response.items` reading the
   resource list is the point of a list response; the mapping view SHALL
   remain reachable as `dict_items()` and as `dict.items(obj)`.
4. WHEN the response carries no body, or the body does not decode, THE SYSTEM
   SHALL return an empty `ApiObject`; WHEN the decoded body is not a JSON
   object THE SYSTEM SHALL return it wrapped as
   `ApiObject({"items": <value>})`.
5. THE SYSTEM SHALL expose `as_dict()` returning the plain wire-shaped
   dictionary.

### Requirement 10: Mirror the API Server's Own Grouping

**User Story:** As a caller, I want api groups named the way the API server
names them so that a path in the Kubernetes reference maps onto a call
without translation.

#### Acceptance Criteria

1. THE SYSTEM SHALL expose `core_v1`, `apps_v1`, `batch_v1`,
   `networking_v1`, and `version` as public attributes of the client.
2. THE SYSTEM SHALL address `core_v1` at `/api/v1`, `apps_v1` at
   `/apis/apps/v1`, `batch_v1` at `/apis/batch/v1`, and `networking_v1` at
   `/apis/networking.k8s.io/v1`.
3. THE SYSTEM SHALL cover namespaces and nodes as cluster-scoped kinds, and
   services, persistent volume claims, deployments, stateful sets, jobs, and
   ingresses as namespaced kinds, each with create, read, list, patch, and
   delete.
4. THE SYSTEM SHALL use the wire plural in the path — `persistentvolumeclaims`
   and `statefulsets`, not the method's readable spelling.
5. THE SYSTEM SHALL accept `label_selector` and `field_selector` on every
   list method and send them as `labelSelector` and `fieldSelector`.
6. THE SYSTEM SHALL send patches with the
   `application/strategic-merge-patch+json` content type, which is what
   `kubectl` uses for the built-in resource kinds.
7. THE SYSTEM SHALL expose `version.get_code()` reading `/version`.
