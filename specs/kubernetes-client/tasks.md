# Implementation Plan — Kubernetes Client

## Package Skeleton

- [x] 1. Create `source/packages/ccai/restclient/kubernetes/` with the `apigroups/` subpackage.
- [x] 2. Declare `requests` and `pyyaml` runtime dependencies in `pyproject.toml`.

## Kubeconfig Resolution

- [x] 3. Implement `KubeConfigResolution` carrying server URL, token, CA path, client cert/key paths, `verify`, and context name.
- [x] 4. Implement `KubeConfigResolver` accepting exactly one of `kubeconfig_path`, `kubeconfig_dict`, `in_cluster`; reject zero or multiple sources with `SemanticError`.
- [x] 5. Implement `available_contexts()`, returning an empty list for in-cluster.
- [x] 6. Implement context selection honouring explicit `context=` over `current-context`, with an error that lists the available contexts.
- [x] 7. Implement `_find_named` cluster/user lookup with a naming error when the entry is absent.
- [x] 8. Implement bearer-token and client-certificate resolution, preferring path forms over inline data.
- [x] 9. Implement `_write_temp_pem` materialising base64 PEM data into `0o600` temp files.
- [x] 10. Honour `insecure-skip-tls-verify`; reject a cluster with no `server` and a user with no credential.
- [x] 11. Refuse `exec` and `auth-provider` credential plugins with `SemanticError` rather than executing them.
- [x] 12. Implement in-cluster resolution from `KUBERNETES_SERVICE_HOST` / `_PORT` plus the mounted service-account token and CA.

## Client Core

- [x] 13. Implement `KubernetesRestClient(resolution=, session=, timeout_seconds=)` with `DEFAULT_TIMEOUT_SECONDS = 60.0`.
- [x] 14. Implement `_build_session` applying the bearer header, `Accept`, TLS verification target, and client certificate pair.
- [x] 15. Expose `resolution` and `server_url` properties.
- [x] 16. Implement `request()` with `None`-valued query parameters dropped and a JSON body encoded with an overridable content type.
- [x] 17. Raise `KubernetesApiRequestError` on non-2xx, preferring the API-server `reason` then `message` then the HTTP reason phrase.
- [x] 18. Return an empty `ApiObject` for an empty or undecodable body; wrap a non-object body as `{"items": ...}`.

## Response Model

- [x] 19. Implement `ApiObject` as a `dict` subclass with wire-spelling and snake_case attribute access, returning `None` for a missing field.
- [x] 20. Implement `wrap_api_value` wrapping nested dicts and lists on access.
- [x] 21. Let payload fields shadow the colliding `dict` methods, keeping the mapping view on `dict_items()`.
- [x] 22. Implement `as_dict()` returning the plain wire-shaped dictionary.

## Errors

- [x] 23. Implement `KubernetesApiRequestError` with `status` / `reason` / `body`, matching the official SDK's `ApiException` attribute names.

## API Groups

- [x] 24. Implement `ResourceGroupBase` with namespaced and cluster-scoped path builders and the five CRUD verbs.
- [x] 25. Define `PATCH_CONTENT_TYPE = "application/strategic-merge-patch+json"` and use it for every patch.
- [x] 26. Implement `CoreV1Group` (`/api/v1`) covering services, persistent volume claims, namespaces, and nodes.
- [x] 27. Implement `AppsV1Group` (`/apis/apps/v1`) covering deployments and stateful sets.
- [x] 28. Implement `BatchV1Group` (`/apis/batch/v1`) covering jobs.
- [x] 29. Implement `NetworkingV1Group` (`/apis/networking.k8s.io/v1`) covering ingresses.
- [x] 30. Implement `VersionGroup.get_code()` reading `/version`.

## Tests

- [x] 31. Implement `FakeSession` / `FakeResponse` recording calls and replaying per-`(method, path)` queued responses.
- [x] 32. Kubeconfig resolver tests: source selection, context selection, both auth modes, inline PEM materialisation, insecure verify, plugin refusal, in-cluster.
- [x] 33. Client tests: session construction, path composition, selector handling and omission, patch content type, wire plurals, `/version`, error mapping, `ApiObject` behaviours.
- [x] 34. Migrate the suite from pytest to testbase — `testbase.raises`, `testbase.parametrize`, `unittest.mock.patch.dict` for `monkeypatch`, `tempfile` for `tmp_path`.

## Open

- [ ] 35. Reconcile with the repository coding standard that every behaviour-bearing method takes a named-only `aspects` parameter. The client exposes `timeout_seconds` instead and has no aspects type, so retry, backoff, and logging policy are not caller-controlled.
- [ ] 36. Reconcile the declared dependencies with the imports. `pyproject.toml` requires `codecraftai-restclient-base` and `codecraftai-credentials`, but the package imports neither — the client subclasses nothing from `RestClientBase` and takes no typed credential object. Either adopt them or drop the dependencies.
- [ ] 37. Add pod coverage. `CoreV1Group` has no `pods` methods, so listing or reading a pod — including the logs of a job's pod — is not reachable through this client.
- [ ] 38. Add list paging. `list_*` sends only `labelSelector` and `fieldSelector`; `limit` and the response's `metadata.continue` token are not handled, so a large collection returns one server-decided page and the rest is silently unseen.
- [ ] 39. Add watch / `resourceVersion` support, or record the decision not to. Change notification is currently unavailable, so consumers must poll.
- [ ] 40. Add property-based tests with `ccai.testbase.properties` — candidates are the camelCase/snake_case round trip in `ApiObject` and path composition in `ResourceGroupBase`. The `hypothesis` library is not used; the fleet ships its own.
- [ ] 41. Remove the unused `requests-mock` dev dependency, or use it. The suite is built entirely on `FakeSession`.
- [ ] 42. Decide the lifetime of the temp PEM files written by `_write_temp_pem`. They are created with `delete=False` and never removed, so a long-running process resolving many kubeconfigs accumulates private-key files.
