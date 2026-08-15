# Peerfold

Build on [Peerfold](https://peerfold.com) from Cursor: connect the tenant-scoped
MCP server, author courses under the block registry, embed learner surfaces on a
site you already own, and integrate the REST API without guessing a schema.

Peerfold is a hosted learning platform with native HubSpot CRM sync. A workspace
holds courses, learners, enrollments, progress, quizzes and exams, certificates,
memberships and orders — plus optional community and partner-program add-ons.

## What is in here

**MCP server** — `mcp.json` connects `https://app.peerfold.com/api/mcp` over
Streamable HTTP. Roughly 150 tenant-scoped tools — authoring, media, enrollment,
reporting, community, partners, and the discovery tools that read the API contract
and the Help Center — though a workspace sees fewer when it does not have the
community or partner add-ons. Every write is audit-logged.

Do not try to memorize the registry. Start from `list_block_types` and
`get_block_schema` for content shapes, `list_api_endpoints` and
`describe_endpoint` for the REST contract, and `search_help` for how the product
behaves.

**Rules**

| Rule | Covers |
| --- | --- |
| `peerfold-authoring` | Block registry discipline, whole-document writes vs merge patches, exam rules vs questions, explicit publishing |
| `peerfold-keys` | Which key may reach a browser, the two base URLs, sandbox mode, request conventions, the CORS allowlist |
| `peerfold-embeds` | The config object, data attributes, the three auth modes, `cms_url` links, and why a 404 renders nothing |

**Skills**

| Skill | Covers |
| --- | --- |
| `course-builder` | The full authoring flow, in the order the server prescribes |
| `site-integrator` | Embedding surfaces on any site: script tag, HubSpot modules, one-call connect, the front-end page map |
| `api-integrator` | OpenAPI-first integration: discover, dry-run, generate; auth models; webhooks |
| `community-and-partners` | Cohorts, threads and moderation; the partner plane; their embed surfaces |

**Commands** — `/peerfold-new-course` scaffolds a course from an outline and stops
before publishing. `/peerfold-embed-audit` reviews a codebase's embed wiring for
key exposure and broken configuration. `/peerfold-api-scaffold` generates a typed
integration for a named endpoint.

**Agent** — `peerfold-course-reviewer` reads a draft with `get_course`,
`course_health`, `get_lesson_blocks` and `get_exam` and reports structure,
completeness, accessibility and assessment findings. It is read-only.

## Install

Install the plugin from the Cursor Marketplace, then give the MCP server a
credential.

### With a secret key

Mint a key pair in your workspace under **Settings → Developers**. The secret half
(`sk_live_…`, or `sk_test_…` for the sandbox) is shown exactly once. Put it in
your environment as `PEERFOLD_SECRET_KEY` — `mcp.json` reads it from there:

```json
{
  "mcpServers": {
    "peerfold": {
      "url": "https://app.peerfold.com/api/mcp",
      "headers": { "Authorization": "Bearer ${PEERFOLD_SECRET_KEY}" }
    }
  }
}
```

A secret key is the whole workspace. It belongs in the environment, never in a
committed file, a client bundle, or a prompt.

### Without a key

`/api/mcp` is also an OAuth 2.1 protected resource. An unauthenticated request
answers `401` with an RFC 9728 `resource_metadata` pointer, so an MCP client that
supports OAuth can discover the authorization server, register itself, and send a
workspace admin to a consent screen — no key typed anywhere. Remove the `headers`
block to take that path. Each connection is revocable on its own under
**Settings → Developers → Connected AI assistants**.

If your Cursor build cannot reach a remote MCP server directly, bridge it:

```json
{
  "mcpServers": {
    "peerfold": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://app.peerfold.com/api/mcp"],
      "env": { "PEERFOLD_SECRET_KEY": "${PEERFOLD_SECRET_KEY}" }
    }
  }
}
```

### Requirements

MCP access is gated on the **Developer platform API** entitlement (Professional
and above), checked on every request. A workspace without it gets a `403` whichever
credential is presented.

## Where things come from

| Thing | Where |
| --- | --- |
| Secret and publishable keys | Workspace → Settings → Developers |
| Membership assertion secret | Settings → Developers → Membership assertion |
| CORS allowlist and front-end page map | Settings → Developers |
| Connected AI assistants (OAuth grants) | Settings → Developers → Connected AI assistants |
| Live OpenAPI contract | `https://app.peerfold.com/api/v1/openapi.json` |
| Developer docs, personalized to your workspace | `https://app.peerfold.com/help/dev` |
| Agent knowledge dump | `https://app.peerfold.com/llms-full.txt` |

## Learn more

- Product: <https://peerfold.com>
- Developers: <https://peerfold.com/developers>
- Integrations: <https://peerfold.com/integrations>
- Community add-on: <https://peerfold.com/community>
- Partner program add-on: <https://peerfold.com/prm>
- Pricing: <https://peerfold.com/pricing>

## Support

<support@peerfold.com>

## License

Apache-2.0.
