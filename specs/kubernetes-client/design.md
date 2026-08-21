# Design

## Overview

`KubernetesRestClient` is a pure-Python client for one Kubernetes API server.
It speaks the API server's plain REST-over-HTTPS surface with `requests`
directly rather than wrapping the official `kubernetes` SDK, so consumers do
not inherit a large vendored client and its transitive dependency tree.

The package splits into three concerns: `KubeConfigResolver` decides *where*
and *as whom* to connect, `KubernetesRestClient` owns the single request
primitive and the session built from that decision, and the api groups under
`apigroups/` are thin declarations of the kinds they own. `ApiObject` shapes
what comes back so consumer code written against the SDK's object model keeps
reading the same way.

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│  codecraftai-interop-kubernetes                          │
│  KubeConfigLoader → KubernetesClient                   │
└──────────┬─────────────────────────────────────────────┘
           │ constructs
           ▼
┌────────────────────────────┐      ┌────────────────────┐
│  KubeConfigResolver        │─────▶│ KubeConfigResolution│
│  path | dict | in-cluster  │      │ url, token, TLS     │
└────────────────────────────┘      └─────────┬──────────┘
                                              │
                                              ▼
┌────────────────────────────────────────────────────────┐
│  KubernetesRestClient                                  │
│  ─ session built once from the resolution              │
│  ─ request(method, path, params, body, content_type)   │
│  ─ core_v1 apps_v1 batch_v1 networking_v1 version      │
└──────────┬─────────────────────────────────────────────┘
           │ HTTPS, bearer token or client cert
           ▼
┌────────────────────────────────────────────────────────┐
│  Kubernetes API server                                 │
└────────────────────────────────────────────────────────┘
```

---

## Data Model

`KubeConfigResolution` is the whole connection state, carried as plain
attributes: `server_url`, `token`, `ca_path`, `client_cert_path`,
`client_key_path`, `verify`, `context`. There is no separate credential type;
the resolution *is* the credential, because a kubeconfig already mixes
endpoint and auth material in one document.

`ApiObject` (`apiobject.py`) is a `dict` subclass, not a generated resource
model. The API server's schema is large, versioned, and extensible with CRDs,
so a hand-maintained model would be perpetually behind; the wire dict is the
model, made ergonomic. `wrap_api_value` wraps nested dicts and lists lazily
on access. `__getattr__` tries the wire spelling first, then walks the keys
comparing `_camel_to_snake(key)`, and returns `None` for a miss.

The `items` collision is the interesting case. Kubernetes list responses carry
their contents under `items`, which shadows `dict.items`. `__getattribute__`
resolves the listed `_SHADOWING_FIELDS` (`items`, `keys`, `values`, `copy`,
`get`, `update`, `clear`, `pop`) to the payload field when the payload
actually contains that key — so `response.items` reads the resource list,
which is what SDK-era consumer code expects. The mapping view stays reachable
as `dict_items()` and via `dict.items(obj)`.

`KubernetesApiRequestError` (`kubernetesapierror.py`) is deliberately thin:
`status`, `reason`, `body` — the attribute names the official SDK's
`ApiException` carried. The transport reports faithfully; the consumer owns
the policy of turning statuses into its own typed hierarchy.

---

## Notable Choices

**Credential plugins are refused, not executed.** A kubeconfig user carrying
`exec` or `auth-provider` raises `SemanticError`. Running an arbitrary helper
binary to mint a token is a different trust decision than reading a config
file, so the client reports it rather than silently shelling out.

**In-cluster mode refuses to guess.** When `KUBERNETES_SERVICE_HOST` and
`KUBERNETES_SERVICE_PORT` are absent the resolver raises rather than falling
back to a default endpoint — the process is simply not running in a cluster.

**Inline PEM material is written to disk.** `requests` takes CA bundles and
client certificates as filesystem paths while kubeconfigs embed them
base64-inline, so `_write_temp_pem` materialises them into `0o600` temp files.

**Verbs live once, in `ResourceGroupBase`.** Kubernetes resource operations
are uniform — only the API prefix and the plural change — so the base carries
`create/read/list/patch/delete` in namespaced and cluster-scoped forms, and
each group is a declaration of its kinds. `VersionGroup` does not inherit it,
because `/version` is not a resource path.

---

## Module Layout

```
source/packages/ccai/restclient/kubernetes/
├── __init__.py
├── kubeconfigresolver.py       # KubeConfigResolver, KubeConfigResolution
├── kubernetesrestclient.py     # KubernetesRestClient, PATCH_CONTENT_TYPE
├── kubernetesapierror.py       # KubernetesApiRequestError
├── apiobject.py                # ApiObject, wrap_api_value
└── apigroups/
    ├── __init__.py
    ├── resourcegroupbase.py    # shared CRUD verbs
    ├── corev1group.py          # /api/v1
    ├── appsv1group.py          # /apis/apps/v1
    ├── batchv1group.py         # /apis/batch/v1
    ├── networkingv1group.py    # /apis/networking.k8s.io/v1
    └── versiongroup.py         # /version
```

---

## See Also

- `codecraftai-interop-kubernetes/specs/kubernetes-client/` — the downstream
  consumer; its `KubeConfigLoader` builds a `KubernetesRestClient`.
- `codecraftai-interop-kubernetes/specs/kubernetes-workload-primitives/` —
  the workload surface layered on this transport.
- `codecraftai-restclient-base/specs/restapigroup-enhancements/` — the fleet's
  shared `RestApiGroup` shape (see the open item in `tasks.md`).
- `codecraftai-testbase/specs/property-testing/` — `ccai.testbase.properties`,
  the fleet's property-testing library.

---

## Testing Strategy

Tests run under the testbase runner, not pytest:

```
PYTHONPATH="$PWD/source/packages:$PWD/source/testroots/testbase" \
    .venv/bin/testbase testing run --root source/testroots/testbase/ccai \
    --includes="*" --output=./.output
```

`FakeSession` / `FakeResponse` (`fakesession.py`) stand in for
`requests.Session`. `FakeSession` records every call and replays responses
queued per `(METHOD, path-suffix)` with a default for anything unmatched, so
a test declares only the exchange it cares about and still asserts on the URL,
query parameters, body, and headers of every request that was made.

`test_kubeconfigresolver.py` covers source selection, context selection, both
auth modes, inline PEM materialisation, `insecure-skip-tls-verify`,
credential-plugin refusal, and the three in-cluster outcomes.
`test_kubernetesrestclient.py` covers session construction from each auth
shape, path composition for namespaced and cluster-scoped verbs, selector
handling including the omission of unset selectors, the strategic-merge patch
content type, the wire plurals, `/version`, error mapping, and the
`ApiObject` behaviours.

The environment is patched with `unittest.mock.patch.dict` and on-disk
kubeconfigs come from `tempfile` — testbase has no `monkeypatch` or
`tmp_path` equivalent, and a test that takes a fixture name as a parameter is
reported as an unresolvable injection rather than skipped.

No live cluster is required. Property-based coverage via
`ccai.testbase.properties` is not yet present — see `tasks.md`.
