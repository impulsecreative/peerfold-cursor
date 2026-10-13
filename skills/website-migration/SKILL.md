---
name: website-migration
description: Migrate a public website into Peerfold Sites as close to one-for-one as possible, with a custom theme and custom modules, then make it WCAG 2.2 AA, SEO, privacy and consent compliant and fully working. Use when asked to move, rebuild, clone or demo an existing website in Peerfold Sites.
---
# Peerfold website migration

This skill moves a public website into Peerfold Sites. The target is a visual one-for-one copy. The result must also be accessible, semantic, findable and fully working.

Use only the client-facing Peerfold MCP connector (`use_workspace`, `list_workspaces`, `sites_*`, `mint_image_upload` and related tools). Do not use admin tools.

Read these files before you start. Paths are relative to this skill's folder,
`skills/website-migration/`:
- `reference/LESSONS.md`: platform quirks and workarounds.
- `reference/MODULE_PATTERNS.md`: module patterns and CSS that worked.
- `reference/COMPLIANCE_CHECKLIST.md`: the compliance pass.
- `scripts/`: Python helpers. The table at the end of this file says what each one does.

The script commands below are written from the skill folder. From a project folder, put the skill folder's path in front of `scripts/`, or copy `scripts/` into the project. Every script writes only to the folder you run it from.

## Rules for every phase
- Use real source copy only. Do not invent copy, counts, quotes or credentials. Mark each placeholder as `[PLACEHOLDER]` and list it in the report.
- Keep it custom. Use a custom theme and custom modules that match the source. Do not use stock sections. Do not replace a source gradient, photo or pattern with a solid theme color.
- Before every write: call `use_workspace`, then confirm the active workspace with `list_workspaces`. Never write to a different workspace.
- Before every page write: read the page again with `sites_get_page` and use the current `base_version`.
- Log every server request and response to `log.md` with the time (ET). Keep exact rejection text.
- Publishing is public. Publish only when the user asked for it or approved it.

## Phase 1: Intake
Steps:
1. Get the source URL and the target Peerfold workspace (name or slug).
2. Ask the user ONE question and wait for the answer before you build: "Start with the homepage only, or migrate the whole site?" Suggest homepage only as the default.
3. If the user picks the whole site: do the homepage first, get approval, then do the other pages.
4. Ask which pages are in scope if the site is large. Ask if testimonials should become a slider.
Checks:
- The source URL returns 200 and is public.
Stop rules:
- Do not start the build until the user answers the scope question. You can start Phase 2 capture while you wait, because capture writes nothing.

## Phase 2: Crawl and capture
Steps:
1. Read `robots.txt` and `sitemap.xml`. Save the page list to `paths.txt`.
2. Take full-page shots of the source at 1440px and 390px: `SHOT_PREFIX=src_ python3 scripts/shot.py https://example.com 1440 /` and again with `390`.
3. Save the rendered HTML and the visible text of each in-scope page (`scripts/styles.py` writes `text.txt`).
4. List every section of the homepage in order: name, background, heading, copy, images, buttons, motion.
5. List the header (utility bar, logo, nav, CTA, overlay or scrim), the footer, all forms and their fields, all anchors, all embeds (video, maps, iframes), and all third-party scripts (analytics, chat, consent).
Checks:
- Every section in the shot has a row in the section list.
- Every form field and every anchor target is recorded.
Stop rules:
- If the site blocks headless browsers, stop and tell the user. Do not bypass bot protection.

## Phase 3: Design tokens
Steps:
1. Run `python3 scripts/styles.py https://example.com 1440 src` and again at 390.
2. Record for each element type: font family, size, weight, style, line height, letter spacing, text case, color.
3. Record button fills (including gradients, for example `linear-gradient(135deg, #f59700 0%, #eb004f 100%)`), hover states, border radius, padding.
4. Record italic or colored accent words in headings. Record section backgrounds (photo, overlay color and opacity, pattern, canvas or SVG animation).
5. Find the real web font files from `fonts.json` (for example Changa One on Google Fonts). Note the woff2 URLs.
6. Write `tokens.md`: colors, fonts, type scale, spacing, radius, shadows, motion.
Checks:
- Each heading level has a size at 1440 and at 390.
- Each brand color pair has a contrast ratio. Flag pairs under 4.5:1 (text) or 3:1 (large text and UI).
Stop rules:
- If a font is not licensed for web use, stop and ask the user which fallback to use.

## Phase 4: Workspace setup
Steps:
1. `use_workspace`, then `list_workspaces`. Confirm the slug.
2. Check that Sites is on and that the workspace has enough page capacity for the scope (`sites_list`, `sites_list_all_pages`; the layout and blog count toward the limit).
3. Create the site with `sites_create_site` (no theme key) if none exists. Set the address folder with `sites_set_address_folder`, for example `/site`.
4. Read `sites_get_schema` once and keep it local.
Checks:
- The site id and the live base URL are in `log.md`.
Stop rules:
- If the workspace does not exist, Sites is off, or the page limit is too low: stop. Ask the user to set it up in Peerfold or to ask their Peerfold admin. Do not try to change plans or limits.

## Phase 5: Theme
Steps:
1. Build a custom theme with `sites_set_asset`: colors, heading and body fonts, type scale, content width (match the source container), radius, button colors.
2. Theme tokens accept hex only. Put gradients and real web fonts in custom modules (see MODULE_PATTERNS.md).
3. Apply with `sites_apply_theme`. Use `dry_run: true` first and read the plan.
4. Build the layout (`/_layout`): header with logo only (drop `brandName`), nav from the source, one header CTA, footer.
Checks:
- The theme validator accepts all token pairs. If it refuses a low-contrast pair, darken the token and record the change.
Stop rules:
- Do not use a stock or shared theme as the final look.

## Phase 6: Custom modules
Steps:
1. Make one module per source section that core blocks cannot match. Use a short key prefix per site, for example `ex-hero`, `ex-quotes`.
2. Each module has `fields`, `html`, `css` and an optional `script`. Use the patterns in MODULE_PATTERNS.md.
3. Load real web fonts from a module script with the FontFace API.
4. Use real copy as field values. Split headings into parts when one word is italic or colored.
5. Publish each module with `sites_publish_module`. Log the key and version.
Checks:
- Module CSS has no ids, no `position:fixed`, no inline styles. `color:` uses a hex or theme token (no rgba).
- Interactive parts have keyboard support, visible focus and 44px targets.
- Motion stops under `prefers-reduced-motion: reduce`.
Stop rules:
- Modules cannot contain `<video>` or `<iframe>`. Create video at runtime from the module script, or use a core embed block. If neither works, stop and flag it.

## Phase 7: Homepage assembly
Steps:
1. Prepare images: `python3 scripts/prep_images.py src/images.json img --bg '#ffffff'`. Crop people photos with `scripts/square_crop.py`.
2. Upload each image: call `mint_image_upload`, then `python3 scripts/upload.py FILE UPLOAD_URL CONTENT_TYPE FINAL_URL`.
3. Build the homepage tree in the source section order. Use core blocks for the h1 and h2 where you can, so the checklist sees them.
4. Validate with `sites_validate_page`. Then write with `sites_apply_operations`. For big edits use `scripts/diffops.py` to send small `set_props` operations.
5. Set page meta in one call: title (60 characters or less), description (70 to 160), social image (1200px wide or more), structured data.
6. Map every source form to a native form (`sites_create_form`). Keep labels, required flags, placeholders and help text.
Checks:
- Section count and order match the source list.
- Every link starts with `https://`, `/`, `mailto:` or `tel:`. Anchors use `/#id` and the ids exist.
Stop rules:
- If the scope is homepage only, stop here and go to Phase 8. Build other pages only after the user approves the homepage.

## Phase 8: Compliance pass
Steps:
1. Work through `reference/COMPLIANCE_CHECKLIST.md`.
2. Run `sites_get_page_checklist` on every page. Fix with `sites_apply_checklist_fix` where it is offered.
Checks:
- 0 errors. Each remaining warning is a known false warning (for example the h1 in a custom module) or is in the report.
Stop rules:
- When a fix breaks the one-for-one look (for example white text on orange), do not choose alone. Flag the tradeoff and ask.

## Phase 9: QA and side-by-sides
Steps:
1. Shoot the build at 1440 and 390: `SHOT_PREFIX=pf_ python3 scripts/shot.py https://<workspace>.peerfold.app/site 1440 /`.
2. Make side-by-sides: `python3 scripts/sidebyside.py shots/src_home.png shots/pf_home.png shots/side_by_side_home_1440.png`.
3. Run `python3 scripts/linkcheck.py BASE example.com paths.txt` for status codes, links, anchors, images and old-domain references.
4. Test the header CTA, nav menus, mobile drawer, forms, sliders and video by hand or with Playwright.
5. Compare computed styles of headings and buttons against `tokens.md`.
Checks:
- All pages 200, 0 broken links, 0 bad anchors, 0 bad images. No horizontal scroll at 320px.
Stop rules:
- Fix and republish until the side-by-sides match. Report any gap you cannot close.

## Phase 10: Publish
Steps:
1. Get approval to publish.
2. `sites_publish_site` (summary, then `confirm: true`).
3. Publish `/_layout` on its own with `sites_publish_page` and the current `base_version`. `sites_publish_site` skips it.
Checks:
- The live page shows the header and footer. The theme change shows on each page after that page is published again.
Stop rules:
- If a publish fails, log the response and stop. Do not retry in a loop.

## Phase 11: Report
Give the user:
- The live URL and the side-by-side images (1440 and 390).
- Modules made (key and version) and pages published (revision).
- Checklist and linkcheck results.
- Placeholders, accessibility tradeoffs, platform gaps and anything left to do.

## How Cursor runs the steps
- Intake: ask the scope question in chat (homepage only, suggested, or the whole site). Wait for the answer. For the whole site, finish and get approval on the homepage before other pages.
- Capture, tokens and QA: run the scripts in the terminal with Playwright. Install first: `pip install playwright pillow requests beautifulsoup4 && playwright install chromium`. Optional: `cairosvg` for SVG sources, `opencv-python` for face detection. Open shots in the editor.
- Peerfold calls: use the Peerfold MCP tools directly. Keep module files in the project (`mod/<key>.html`, `.css`, `.script`, `.fields.json`) and send them from there.
- Keep `log.md` in the project root.

## Scripts
| Script | Use |
|---|---|
| `scripts/shot.py` | Full-page screenshots at a set width. Launches Chromium through Playwright, clicks a consent button if one is shown, scrolls to load lazy images, writes to `shots/`. |
| `scripts/montage.py` | Contact sheet of many page shots from `shots/`. |
| `scripts/sidebyside.py` | Source and build next to each other in one image. |
| `scripts/styles.py` | Computed styles, images, fonts and visible text from a live page, through Playwright, written to an output folder. |
| `scripts/prep_images.py` | Download the source images listed in `images.json`, flatten and resize them, write them to an output folder. |
| `scripts/square_crop.py` | Square crop with the face centered. Local only. |
| `scripts/upload.py` | PUT one file to a `mint_image_upload` URL with `curl`. Records the final URL in `map.json` and appends one line to `log.md`. |
| `scripts/linkcheck.py` | Crawl the built site: status codes, internal links, anchors, images, old-domain references. It also sends a request to every external link and image host it finds. |
| `scripts/diffops.py` | Small `set_props` operations from two page trees. Local only. |

None of the scripts reads a credential. `upload.py` takes the signed upload URL as an argument. That URL is short-lived; do not save it in a file you share.
