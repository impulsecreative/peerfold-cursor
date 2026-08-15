---
name: api-integrator
description: Integrate the Peerfold REST API the OpenAPI-first way — discover an operation with list_api_endpoints and describe_endpoint, dry-run it with try_endpoint, then generate typed client code. Use when writing code that calls Peerfold, choosing an auth model, or handling webhooks.
---

# API integrator

The Peerfold API is generated from one OpenAPI 3.1 contract, which also generates
the route validation, the SDK types and the MCP tool schemas. If the docs and the
API disagree, that is a bug rather than a nuance — so read the contract instead of
recalling an endpoint.

## Discover before you write

Five MCP tools cover the whole loop, and none of them costs a failed request:

| Tool | Use it for |
| --- | --- |
| `list_api_endpoints` | The catalog: method, path, summary, tags, auth level, plane. Filter by `tag`, by `plane` (`lms` / `platform` / `community`), or by `auth` (`learner` / `secret` / `public`). |
| `describe_endpoint` | One operation in full — parameters, request body, responses, security, and every referenced component schema. Identify it by `operationId` (`listCatalog`) or `"METHOD /path"`. |
| `generate_client_snippet` | A ready-to-run curl and/or TypeScript-fetch snippet with auth-header placeholders and an example body. `language: "curl" | "typescript" | "both"`. |
| `try_endpoint` | Validate and optionally run a real call. `mode: "dry_run"` (the default) echoes the exact validated request with no side effects; `mode: "execute"` runs it, and ONLY under a test-mode secret key. A live key is refused. |
| `scaffold_integration` | A starter for a named use case — "custom course player", "progress dashboard", "hubspot membership relay" — with a fetch snippet, an env checklist and the recommended auth flow. |

`search_help` searches the shipped Help Center for this exact build, and each hit
names a `peerfold://help/{slug}` resource you can read in full. Reach for it
before answering a question about how Peerfold works from memory.

Note that the `plane` filter has no `prm` value; find partner routes with
`tag: "prm"`.

Outside MCP, the live contract is at
`https://app.peerfold.com/api/v1/openapi.json`, with agent-oriented summaries at
`/llms.txt` and `/llms-full.txt`.

## The namespaces

Platform routes are product-neutral; product resources are namespaced.

| Namespace | Plane |
| --- | --- |
| `/api/v1/me`, `/api/v1/auth/*` | Identity and learner auth |
| `/api/v1/keys*`, `/api/v1/webhooks*`, `/api/v1/cors-origins`, `/api/v1/connect/*`, `/api/v1/language/*`, `/api/v1/admin-embed/*` | Platform administration, secret key |
| `/api/v1/lms/*` | Courses, catalog, enrollments, progress, assessment, certificates, cart, reporting |
| `/api/v1/community/*` | Cohorts, threads, comments, reactions, ideas, members, notifications, moderation reports |
| `/api/v1/prm/*` | The partner plane |

Auth by namespace, as declared in the spec:

- **Community is learner-JWT only.** Every route on `/api/v1/community/*` requires
  a signed-in member's token. There is no secret-key read of the community.
- **PRM is split.** `/api/v1/prm/{me,leads,deals,commissions,referral-links,attributions}`
  is the partner's own view and takes the same learner JWT every other surface
  carries — a partner is not a second login, just a member with a partner row
  resolved server-side. `/api/v1/prm/program/*` is the program-owner view
  (partners, tiers, leads, deals, commissions, attribution) and takes the secret
  key or an OAuth token.
- **LMS is mixed.** The catalog and a course by slug also answer a
  publishable-key-only request (`X-Peerfold-Publishable-Key`, no `Authorization`)
  and return the public shell: catalog-visible courses with title, description,
  image, categories, credits and price — no enrollment, no progress, no lesson
  content. Lesson bodies always need a learner token. Learner administration,
  reporting, exams and CEU configuration take the secret key.
- Both `community` and `prm` are add-ons and answer **404** rather than a paywall
  when a workspace does not have one.

## Choosing an auth model

This is the decision that is expensive to undo. Learner-plane calls need a learner
JWT (15 minutes, tenant-scoped, one learner); the flows differ only in how it is
obtained.

| Use this | When | The secret lives |
| --- | --- | --- |
| Admin secret key | Server to server only: reporting, bulk enrollment, provisioning, back-office jobs. No end user involved. | Your server |
| Learner PKCE | You own a frontend and want Peerfold to handle sign-in. The default for a headless portal or SPA. | Nowhere |
| Trusted relay (token exchange) | Your app already authenticated the person and you want to hand them straight in. | Your server or serverless function |
| Membership assertion | A HubSpot CMS page whose visitor is already a logged-in member. | The theme's settings, digest only |

**Learner PKCE** — register the redirect URI under Settings → Developers (it is an
allowlist), send the browser to `GET {portal}/api/v1/auth/authorize` with
`client_id` (your publishable key), `redirect_uri`, an S256 `code_challenge` and
`state`, then exchange the returned `code` at `POST {portal}/api/v1/auth/token`
with your `code_verifier`. Refresh at the same endpoint with
`grant_type=refresh_token`; refresh tokens rotate on use. No secret key appears
anywhere in this flow, which is exactly why it is the default.

**Trusted relay** — put a small server endpoint in front of
`POST /api/v1/auth/token-exchange` (secret-key authed). It asserts the signed-in
user server-side and returns a learner token to the browser, so the browser never
sees the key. `@peerfold/js` wires this: `createPeerfold({ relayUrl })` re-mints
through your relay whenever the token expires.

**Direct mint** — a secret key can mint a learner token for anyone with
`POST /api/v1/auth/learner-token` (`email` or `member_id`). The trusted-subsystem
shortcut, and the reason a secret key never leaves your server.

## The SDKs

- `@peerfold/api-client` — typed, zero-runtime-dependency wrapper over `fetch`
  (browser, Node, edge). Types are inferred from the same schemas that validate
  the live API, so a contract change breaks your build rather than your users.
- `@peerfold/react` — provider and hooks (`useCatalog`, `useProgressMutation`, …).
- `@peerfold/js` — prebuilt browser bundle exposing `window.Peerfold`, plus the
  embeddable cart drawer.

```ts
import { PeerfoldClient } from "@peerfold/api-client";

// Browser / learner plane.
const client = new PeerfoldClient({
  baseUrl: "https://your-workspace.peerfold.app",
  learnerToken: () => tokenStore.get(),
});

// Server / admin plane — NEVER construct this in browser code.
const admin = new PeerfoldClient({
  baseUrl: "https://app.peerfold.com",
  secretKey: process.env.PEERFOLD_SECRET_KEY,
});
```

Lists are cursor-paginated: pass the `next_cursor` you were given, or let the
SDK's `iterate()` walk it.

## Habits that keep an integration correct

- **Pin the version.** `Peerfold-Version: 2026-07-01`.
- **Grade nothing client-side.** Quiz and exam answers are scored on the server,
  and the payload you rendered does not contain the correct answers.
- **Progress writes are idempotent.** The client generates an `Idempotency-Key`
  per event unless you supply one, so a retry replays the stored response instead
  of double-counting. In React use `useProgressMutation` rather than calling
  `record` directly — it is optimistic, coalesces repeated events for a lesson,
  keeps a stable key per queued item, and retries 429s and 5xxs with backoff. For
  the end of a visit, `Peerfold.progressBeacon(...)` writes with
  `fetch(keepalive)`.
- **Fall back gracefully on an unknown block type.** Block JSON is semver'd and
  additive-only within a major version, so new types arrive without a major bump
  and a player that throws on one breaks on a Tuesday.
- **Log the request id.** Every response carries `X-Request-Id`, and errors carry
  it as `err.requestId`.

## Webhooks, not polling

Register an endpoint and subscribe to what you need: `learner.enrolled`,
`progress.lesson_completed`, `exam.submitted`, `exam.graded`,
`certificate.issued`, `course.published`, `sync.dead_letter`.

Verify every delivery. `X-Peerfold-Signature` is `t=<unix seconds>,v1=<hex>` where
the hex is HMAC-SHA256 of `"{t}.{raw body}"` under the endpoint's `whsec_…`
secret. Compare in constant time, reject stale timestamps, and use the RAW body —
not a re-serialized object.

```ts
import crypto from "node:crypto";

function verify(rawBody: string, header: string, secret: string): boolean {
  const parts = Object.fromEntries(
    header.split(",").map((kv) => kv.split("=") as [string, string]),
  );
  const expected = crypto
    .createHmac("sha256", secret)
    .update(parts.t + "." + rawBody)
    .digest("hex");
  return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(parts.v1));
}
```

Deliveries retry with exponential backoff for up to 24 hours, and an endpoint that
fails persistently is disabled — so return 2xx fast and do the work
asynchronously. If you genuinely cannot receive webhooks, the MCP `list_completions`
tool is a keyset feed built for polling: call it with `limit`, persist
`next_cursor`, resume next run, and stop when `caughtUp` is true.

## Checks before you say it is done

- The operation was confirmed with `describe_endpoint`, not recalled.
- The auth model matches the plane, and no secret key can reach a browser.
- Cursor pagination is walked rather than assumed to be one page.
- Webhook verification uses the raw body and a constant-time compare.
- Development ran against a `sk_test_…` sandbox key.
