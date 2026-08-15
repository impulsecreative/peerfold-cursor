# Peerfold Cursor plugins

The Cursor Marketplace source for [Peerfold](https://peerfold.com), by
[Impulse Creative](https://impulsecreative.com).

One plugin lives here:

- **[`plugins/peerfold`](./plugins/peerfold)** — connect the Peerfold MCP server,
  author courses under the block registry, embed learner surfaces on a site you
  already own, and integrate the REST API without guessing a schema.

## Install

Install **Peerfold** from the Cursor Marketplace, then give the MCP server a
credential — a workspace secret key in `PEERFOLD_SECRET_KEY`, or OAuth with no key
at all. Full setup, including what each rule and skill covers, is in the
[plugin README](./plugins/peerfold/README.md).

Keys are minted in your Peerfold workspace under **Settings → Developers**. The
publishable key (`pk_live_…`) is the only one that may reach a browser; the secret
key (`sk_live_…`) is server-side only and is shown exactly once.

## Repository layout

```text
.cursor-plugin/marketplace.json   the marketplace manifest
plugins/peerfold/                 the plugin
  .cursor-plugin/plugin.json      its manifest
  mcp.json                        the Peerfold MCP server connection
  rules/                          authoring, keys, embeds
  skills/                         course-builder, site-integrator,
                                  api-integrator, community-and-partners
  commands/                       new-course, embed-audit, api-scaffold
  agents/                         course reviewer
  assets/logo.svg
docs/add-a-plugin.md              how to add another plugin here
scripts/validate-template.mjs     manifest and frontmatter validation
```

## Developing

Validate the repository before committing:

```bash
node scripts/validate-template.mjs
```

It checks the marketplace manifest, each plugin manifest, referenced paths, and
the required frontmatter on every rule, skill, agent and command.

There are no hooks and no shell scripts in the plugin — nothing here runs on your
machine except the MCP client connecting to a remote HTTPS endpoint you configured.

Everything the plugin teaches is grounded in the shipped Peerfold product. When a
tool, endpoint or setting changes, update the plugin from the live sources rather
than from memory:

- OpenAPI contract: `https://app.peerfold.com/api/v1/openapi.json`
- Developer docs: `https://app.peerfold.com/help/dev`
- Agent knowledge: `https://app.peerfold.com/llms-full.txt`

## Support

<support@peerfold.com>

## License

Apache-2.0.
