======================================
Code Craft AI - Kubernetes REST client
======================================

A pure-Python client for the Kubernetes API server.

The Kubernetes API is plain REST over HTTPS with JSON bodies, so this package
speaks it directly on top of ``codecraftai-restclient-base`` rather than
depending on the official ``kubernetes`` SDK. That keeps the fleet's
pure-Python guarantee and avoids dragging a large vendored client (and its
transitive dependency tree) into every consumer.

What it provides
================

* ``KubeConfigResolver`` — resolves a kubeconfig path, an in-memory
  kubeconfig dict, or the in-cluster service-account context into a server
  URL plus the TLS material and bearer token needed to reach it. Supports
  bearer-token auth, client-certificate (mTLS) auth, and custom CA bundles.
* ``KubernetesRestClient`` — the REST client, with api groups mirroring the
  API server's own grouping:

  * ``core_v1`` — namespaces, nodes, services, persistent volume claims
  * ``apps_v1`` — deployments, stateful sets
  * ``batch_v1`` — jobs
  * ``networking_v1`` — ingresses
  * ``version`` — the ``/version`` endpoint

Responses are returned as plain dictionaries matching the API server's JSON,
and are additionally attribute-addressable so callers written against the
SDK's object model keep working.
