---
name: peerfold-api-scaffold
description: Generate a typed Peerfold integration for a named endpoint. Discover the operation from the spec, dry-run it, then write client code that matches this project's conventions.
---

# Scaffold a Peerfold integration

Given an endpoint or a use case the user names, produce working, typed code in
this project. Never write the call from memory. The OpenAPI contract is the
source of truth, and it is one tool call away.

Follow the `api-integrator` skill for the auth models and the namespaces.

## 1. Find the operation

If the user named a use case, start with `list_api_endpoints`, filtering by `tag`
or by `plane` (`lms`, `platform`, `community`; partner routes carry `tag: "prm"`),
or by `auth` (`learner`, `secret`, `public`).

If they named an endpoint, go straight to `describe_endpoint` with the
`operationId` or `"METHOD /path"`. Read the parameters, the request body, every
response, and the security requirement before writing a line.

For a whole use case (a custom course player, a progress dashboard, a HubSpot
membership relay) call `scaffold_integration { kind }` first. It returns a
starter, an env checklist, and the recommended auth flow.

## 2. Dry-run it

```
try_endpoint { operation, params, body, mode: "dry_run" }
```

The dry run echoes the exact request that would be sent (method, resolved URL,
headers, body), validated against the spec, with no side effects. It catches a
wrong parameter name before any code exists.

If the connection is on a test-mode secret key, `mode: "execute"` runs it for real
against the sandbox. A live key is refused, and that refusal is correct.

## 3. Decide where the code runs

- Secret key: server only. A Node route handler, a serverless function, or a
  background job. Read the key from `process.env.PEERFOLD_SECRET_KEY`.
- Learner JWT: the browser, obtained by PKCE or through a relay you own.
- Publishable key: the browser, for the catalog and a course by slug only.

Never place a secret-key call in a file that ships to the browser. If the project
has no server boundary and the operation needs a secret key, say so and propose
one. Do not downgrade the auth.

## 4. Write the code

Match this project's existing conventions: its HTTP client, error handling, types
and file layout. If the project already depends on `@peerfold/api-client`, use
`PeerfoldClient`. If it uses `@peerfold/react`, prefer the hooks. Otherwise
`generate_client_snippet { operation, language: "typescript" }` gives a starting
point to adapt.

Include, every time:

- `Peerfold-Version: 2026-07-01`.
- Cursor pagination handled. Walk `next_cursor`; do not assume one page.
- RFC 7807 error handling that surfaces the `code` and logs `X-Request-Id`.
- 429 backoff, or a note that the SDK surfaces `err.retryable` and `err.rateLimit`.
- Idempotency where the operation supports it, especially progress writes.

## 5. Report

Tell the user the operation you used (method, path, operationId), the credential
it needs and where that credential lives, the files you created or changed, and
anything you could not verify, for example whether the workspace's plan includes
the entitlement the route is gated on.
