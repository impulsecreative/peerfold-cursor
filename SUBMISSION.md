# Submission notes

How this repository maps to Cursor's plugin submission checklist and to the
paths cursor.directory scans. The checklist items below are quoted from
<https://cursor.com/docs/reference/plugins> as read on 2026-10-13.

## Listing text

- Name: Peerfold
- Description: Build courses, manage enrollments and publish Peerfold Sites
  pages from Cursor through the Peerfold MCP server. Sign in with OAuth; no key
  is typed anywhere, and every write is audit-logged in your workspace.
- Keywords: peerfold, lms, courses, enrollments, sites, hubspot, community,
  partners, mcp
- Homepage: <https://peerfold.com>
- Repository: <https://github.com/impulsecreative/peerfold-cursor>
- License: Apache-2.0
- Logo: `assets/logo.svg`

## Cursor's submission checklist

| Checklist item (quoted) | Where it is met |
| --- | --- |
| "Plugin has a valid root plugin.json or .cursor-plugin/plugin.json manifest" | `.cursor-plugin/plugin.json`, validated against Cursor's published schema in CI (`additionalProperties: false`). |
| "name is unique, lowercase, kebab-case (e.g., my-awesome-plugin)" | `"name": "peerfold"`. |
| "description clearly explains the plugin's purpose" | One sentence in `plugin.json`. |
| "All included components have valid files and frontmatter" | `rules/*.mdc` (`description`), `skills/*/SKILL.md` (`name`, `description`), `agents/*.md` (`name`, `description`), `commands/*.md` (`name`, `description`). Checked by `scripts/validate-template.mjs`. |
| "Logo is committed to the repo and referenced by relative path (if provided)" | `assets/logo.svg`, a 96 by 96 square, referenced as `"logo": "assets/logo.svg"`. |
| "README.md documents usage and any configuration" | `README.md`: install, OAuth, revocation, the optional key, requirements, privacy. |
| "Agent Plugins conform to the Agent Plugins schemas" | Not applicable. This is a Cursor Plugin with a `.cursor-plugin/plugin.json` manifest. |
| "Cursor Plugins using variables declare every ${VAR} from mcp.json in the manifest schema" | `mcp.json` uses no variables, so `plugin.json` declares none. `scripts/validate-template.mjs` fails if a `${VAR}` appears in `mcp.json`. |
| "All paths in manifest are relative and valid (no .., no absolute paths)" | The only path is `assets/logo.svg`. `scripts/check-text.mjs` fails the whole repository on `..` segments and absolute home paths. |
| "Plugin has been tested locally" | Clone into `~/.cursor/plugins/local/peerfold` as the README describes. |
| "Cursor multi-plugin repositories have .cursor-plugin/marketplace.json at the repo root with unique plugin names" | Not applicable. This is a single-plugin repository and carries no marketplace manifest. |

The submission steps on the same page: create the plugin, host it in a public
Git repository with the logo committed, then submit the repository link at
cursor.com/marketplace/publish.

## cursor.directory scan paths

cursor.directory reads a public repository at its root.

| Scanned path | In this repository |
| --- | --- |
| `.mcp.json` or `mcp.json` | Both, byte-identical: one server, `peerfold`, at `https://app.peerfold.com/api/mcp`. |
| `rules/*.mdc` | `peerfold-authoring.mdc`, `peerfold-embeds.mdc`, `peerfold-keys.mdc`. |
| `skills/*/SKILL.md` | `api-integrator`, `community-and-partners`, `course-builder`, `enrollment-manager`, `site-integrator`, `sites-builder`, `website-migration`. The last one also carries `reference/` and `scripts/` beside its `SKILL.md`; the Cursor plugin reference describes only `SKILL.md` and is silent on other files in a skill folder, so the scripts are plain Python helpers the agent runs in the terminal and nothing depends on Cursor reading them. |
| `agents/*.md` | `peerfold-course-reviewer.md`. |
| `hooks/hooks.json` | None. Cursor runs nothing from this plugin on its own. |

## What the live endpoint answers

Observed with `curl -i https://app.peerfold.com/api/mcp` on 2026-10-13:
`401`, `WWW-Authenticate: Bearer realm="Peerfold MCP", resource_metadata="https://app.peerfold.com/.well-known/oauth-protected-resource/api/mcp"`,
and a problem-JSON body. The protected-resource document names
`https://app.peerfold.com` as the authorization server, and that server's
metadata lists the authorize, token, register and revoke endpoints with PKCE
S256. `scripts/check-endpoint.sh` asserts all of that in CI.
