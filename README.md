# Peerfold for Cursor

A Cursor plugin that connects the [Peerfold](https://peerfold.com) MCP server to
your editor. With it, the agent in Cursor can build courses, enroll learners,
read progress, moderate a community, run a partner program and publish Peerfold
Sites pages in your workspace, using the same service layer the Peerfold admin
screens use.

Peerfold is a hosted learning platform with native HubSpot CRM sync, by
[Impulse Creative](https://impulsecreative.com).

## What is in the plugin

- `mcp.json` connects `https://app.peerfold.com/api/mcp` over Streamable HTTP
  with OAuth. No key is typed anywhere.
- Three rules: authoring discipline (`peerfold-authoring`), credentials and base
  URLs (`peerfold-keys`), and embed contracts (`peerfold-embeds`).
- Six skills: `course-builder`, `enrollment-manager`, `sites-builder`,
  `api-integrator`, `site-integrator`, `community-and-partners`.
- Three commands: `/peerfold-new-course`, `/peerfold-embed-audit`,
  `/peerfold-api-scaffold`.
- One agent: `peerfold-course-reviewer`, a read-only review of a draft course.

Every write skill tells the agent to confirm with you before it publishes, sends
email, or enrolls more than one person.

The server's tool catalog is the source of truth for what the agent can do. The
plugin does not list every tool. It teaches the agent to start from
`list_block_types`, `get_block_schema`, `sites_get_schema`,
`list_api_endpoints` and `search_help`, and to read before every write.

## Requirements

- A Peerfold workspace on the Professional plan or above. MCP access is gated on
  the developer platform API entitlement and checked on every request. A
  workspace without it answers `403` whichever credential is presented.
- A Cursor build that can connect to a remote MCP server over HTTP with OAuth.

## Install

### From cursor.directory

Open the Peerfold listing on cursor.directory and install it. Cursor reads this
repository at its root: `mcp.json`, `rules/`, `skills/`, `agents/` and
`commands/`.

### With the Cursor deeplink

This link installs only the MCP server entry, the same one `mcp.json` carries.
It is built the way the Peerfold Developers screen builds it: the server's own
config object, base64-encoded.

```text
cursor://anysphere.cursor-deeplink/mcp/install?name=peerfold&config=eyJ1cmwiOiJodHRwczovL2FwcC5wZWVyZm9sZC5jb20vYXBpL21jcCJ9
```

### For local testing

Clone this repository into Cursor's local plugin folder and restart Cursor:

```bash
git clone https://github.com/impulsecreative/peerfold-cursor ~/.cursor/plugins/local/peerfold
```

## Sign in with OAuth

The first time the agent calls a Peerfold tool, Cursor opens your browser.
`/api/mcp` is an OAuth 2.1 protected resource and `app.peerfold.com` is its
authorization server. The client follows the `WWW-Authenticate` header to the
protected-resource metadata, registers itself, and sends you to a Peerfold
consent screen where you pick the workspace. Approving mints a token bound to
that workspace. Access tokens last one hour and refresh tokens thirty days;
refresh tokens rotate on every use.

If you administer more than one workspace, `list_workspaces` shows which are
reachable and which is active, and `use_workspace` moves the connection without
reconnecting.

### Revoke the connection

A connection is one grant: this client, one workspace, the admin who approved
it. To end it, open Settings > Developers in the workspace and use Connected AI
assistants. Revocation is immediate and invalidates every token the grant ever
minted. A client may also disconnect itself through the RFC 7009 revocation
endpoint at `https://app.peerfold.com/api/oauth/revoke`. Every grant, refresh
and revocation is audit-logged.

The MCP tool `revoke_agent_connection` is a different thing. It disconnects an
AI agent that a learner connected to one of your Peerfold Sites, and it does not
touch your own Cursor connection.

## Optional: a secret key instead of OAuth

A program with no browser to sign in through can present a workspace secret key
instead. Mint one under Settings > Developers; it is shown once. Set it in your
environment and add the header to the server entry in your own Cursor MCP
settings, outside this repository:

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

A secret key is the whole workspace with no per-assistant revocation. Never
commit it, never paste it into a prompt, and prefer OAuth wherever a sign-in is
possible. This plugin's `mcp.json` carries no key and no `${VAR}` placeholder,
so `plugin.json` declares no `variables`.

## Privacy

- No code from this plugin runs on your machine. It holds no hooks and no
  scripts that Cursor executes. The only thing that happens locally is Cursor's
  MCP client connecting to a remote HTTPS endpoint.
- Every tool acts on one workspace, the one your credential resolves to.
- Every write is audit-logged. Writes made over OAuth carry
  `source: "mcp-oauth"` with the grant as the actor, so which assistant did what,
  on whose consent, is answerable from the audit log alone.
- A tool your plan does not include stays listed and answers with the reason it
  cannot run.

Privacy policy: <https://peerfold.com/privacy>. Terms: <https://peerfold.com/terms>.

## Keep it current

Everything the plugin teaches is grounded in the shipped product. When a tool,
endpoint or setting changes, update the plugin from the live sources:

- Developer docs for MCP: <https://app.peerfold.com/help/dev/mcp>
- OpenAPI contract: `https://app.peerfold.com/api/v1/openapi.json`
- Agent knowledge: `https://app.peerfold.com/llms-full.txt`

Checks, which CI also runs:

```bash
node scripts/validate-template.mjs                       # manifest, paths, frontmatter, mcp.json pair, logo
node scripts/check-text.mjs                              # no em dashes, absolute paths, .. segments or secret keys
node scripts/check-tool-names.mjs scripts/registry-snapshot.txt   # every tool name the plugin references exists
scripts/check-endpoint.sh                                # the live endpoint still answers 401 with OAuth metadata
```

`scripts/registry-snapshot.txt` is the list of customer tool names on the
Peerfold MCP server, taken from the server's registry on 2026-10-13. Refresh it
when the server adds or renames tools.

## Support

<support@peerfold.com>

## License

Apache-2.0. See [LICENSE](./LICENSE).
