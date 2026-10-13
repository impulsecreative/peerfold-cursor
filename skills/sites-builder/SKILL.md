---
name: sites-builder
description: Build and publish Peerfold Sites pages over MCP. Read the schema, create a page, change it with operation batches, validate, run the checklist, and publish only after the user confirms. Use when asked to build, edit, translate or publish a website page, blog post, form or theme on Peerfold Sites.
---

# Sites builder

A Peerfold Sites page is a JSON tree of components, never markup. Every change is
a batch of operations against a draft, and visitors keep seeing the published
revision until a page is published on purpose. The tools enforce that; this skill
keeps you from fighting them.

Sites is a separate product. A workspace without it lists the `sites_` tools and
each one refuses with the plan it needs. Report that refusal; do not retry.

## Confirm before you publish

`sites_publish_page` and `sites_publish_site` refuse their first call with
`confirm_required` and a summary of what would go live. Show that summary to the
user and call again with `confirm: true` only after they say yes. Never send a
`page.publish` operation inside a batch; the server refuses it. Some workspaces
route an assistant's publish to an admin for approval, in which case the
confirmed call answers `awaiting_approval` with an `approval_id`. Report that and
stop.

Also confirm before `sites_archive_page`, `sites_bind_domain` (it moves a domain
off whatever site it showed before), `sites_delete_site` and
`sites_set_page_access` (members-only hides a page from visitors and lists).

## Orientation

```
sites_list                    every site, live first
sites_get { site_id }         one site: key, name, status, theme, address folder
sites_get_current_site        the site the admin's Sites screens are showing
sites_list_pages { site_id }  a site's pages by path, without trees
sites_list_all_pages          pages across every site, most recently edited first
sites_get_schema              the component vocabulary, page kinds, operation shapes and limits
```

Read `sites_get_schema` before building anything. It is free, it reads no page,
and it is scoped to this workspace's plan and this connection, so the components
it lists are the ones you may place.

## Build a page

```
sites_create_site { key, name, default_locale }       only when there is no site yet
sites_create_page { site_id, path, kind? }             a draft at version 1
sites_get_page    { page_id }                          the draft tree and its version
sites_validate_page { page_id, operations, base_version }
sites_apply_operations { page_id, operations, base_version }
```

- Always read the page first and pass its `version` as `base_version`. A stale
  version is refused and nothing is saved.
- A batch is all or nothing. Every problem comes back together with the node and
  the operation it concerns.
- `sites_validate_page` is the same check with nothing saved. Use it before a
  large batch, and with `checklist: true` to learn which checklist findings the
  batch would resolve or introduce.
- `sites_list_presets` and `sites_insert_preset` drop a prefilled section (a hero,
  a call to action, a form section) into the draft with fresh node ids. Prefer a
  preset over composing a section node by node.
- `sites_duplicate_page` copies a page. `sites_get_page_checklist` lists what to
  improve for search, link previews, accessibility and speed. A finding of kind
  `auto` can be applied with `sites_apply_checklist_fix`; a finding of kind
  `guided` needs the user's decision.
- Text settings that accept a CRM field take braces such as
  `{{ person.firstName | there }}`; `sites_get_page` repeats them under
  `authoring` so you can edit them as text.

## Theme, forms, blog, domains

- `sites_list_themes`, `sites_apply_theme`, `sites_get_theme`, `sites_set_theme`.
  Applying a shared theme changes drafts only and clears a workspace `theme_key`;
  the reply names what it cleared.
- `sites_design_brief` writes a prompt for a design assistant from the site's own
  colors, type and allowed components. A design made from it comes back through
  `sites_import_design`.
- `sites_create_form`, `sites_update_form`, `sites_list_forms`. A form needs one
  required email question bound to `email`. Submissions are read with
  `sites_list_form_submissions`.
- `sites_add_blog`, `sites_create_post`, `sites_set_post`, `sites_list_posts`.
- `sites_translate_page`, `sites_get_page_translation`, `sites_set_page_translation`
  for other languages.
- `sites_list_domains` and `sites_bind_domain` choose which site a domain shows.
  A domain serving the portal is changed on the Domains screen, never here.

## Publish

```
sites_publish_page { page_id, base_version }                first call: summary only
sites_publish_page { page_id, base_version, confirm: true } after the user says yes
sites_publish_site { site_id }                              every changed page, same two steps
```

A revision is never edited afterward. A later change is a later revision.

## Checks before you say it is done

- Every batch was built against a fresh `sites_get_page` read and its version.
- The checklist was run and its `error` findings were resolved or reported.
- The publish summary was shown to the user and they said yes before the
  confirmed call.
- You reported the page's address and whether it is live or awaiting approval.
