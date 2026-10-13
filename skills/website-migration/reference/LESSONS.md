# Peerfold Sites: quirks and workarounds

Lessons from real migrations. Each item is a server rule or a fix that worked.

## Workspace and writes
- Call `use_workspace` and confirm with `list_workspaces` before every write.
- Opening a page in the editor autosaves and bumps the version. Read `base_version` with `sites_get_page` right before each write.
- `sites_publish_page` needs `base_version`. On an unchanged page it asks to confirm "version N replacing N". Do not confirm that.
- Every `sites_apply_operations` call returns the full page tree. Batch edits. Use `scripts/diffops.py` for small `set_props` operations.
- Log every response. Without a log you lose the exact rejection text.
- Page and site limits apply. The layout and the blog page count toward the page limit. If the limit is too low, stop and ask the user or their Peerfold admin to raise it.

## Publishing
- `sites_publish_site` does not publish `/_layout`. Publish the layout with `sites_publish_page`, or pages have no header and footer.
- There is no draft preview. Validate with `sites_validate_page`, then check the live page after publish.
- A theme change reaches a page only when that page is published again.
- `sites_set_asset` on a theme in use goes live at once.
- A new site has no address. Set one with `sites_set_address_folder`. The first fetch can serve the old page for about a minute.
- `/site/x/` redirects (308) to `/site/x`. Write links without a trailing slash.

## Layout and header
- The layout top level accepts only `sites/notice`, `sites/header`, `sites/main` and `sites/footer`. A custom module cannot go at the top level.
- Workaround for a utility bar: put the module inside `sites/footer`. Its script moves its root element above the header (see the topbar pattern).
- Header with `brandName` and a logo shows both. Drop `brandName` for a logo-only header.
- Header CTA style is only primary, outline or ghost. A gradient header CTA needs a module script.
- Overlay header: use mode overlay with a scrim. Give the hero top padding so its content clears the header. A logo baked on a dark plate shows as a box; use a transparent cutout.
- A nav parent with children renders as a toggle. Its URL is ignored, so make its first child the parent page.
- Links to another host in mega menu feature, all and foot links always open in a new tab.

## Custom modules
- Allowed field kinds: text, textarea, url, image, number, boolean, select, and list (one level, sub-fields under `item`).
- Refused in templates: `<video>`, `<iframe>`, ids, inline styles, scripts, event handlers, `position:fixed`, and `blocks/embed` nodes.
- CSS `color:` must be a theme token or `#rrggbb`. Background and border can use rgba.
- `<pf-node>` props inside a module are static.
- A module script (`export default function(root, fields)`) runs on the live page. It can reach `root.ownerDocument`.
- Class names get a `pfm-<key>-<version>-` prefix. In scripts, find elements with `[class$="suffix"]` and build new class names from an existing one.
- The page CSP can block injected `<style>` elements. If it does, set `element.style` from the script.
- Video: create the `<video>` element from the module script at runtime.
- Web fonts: load with the FontFace API from a module script (see MODULE_PATTERNS.md).

## Checklist
- The checklist cannot see headings inside custom modules. An h1 in a module gives a false `seo.heading.main` warning. Module h2s can cause `seo.heading.order` on the next core h3. Use core heading blocks where you can, else record the false warning.
- A question heading needs an answer sentence right after it.
- Social images must be 1200px wide or more. Titles about 60 characters. Descriptions 70 to 160.
- Send title, description and structured data together in one `page.set_meta`.

## Blocks and images
- A card grid holds at most 12 cards. A nav item holds at most 8 links unless `maxLinks` is set.
- Testimonial slider dots are 44px and do not wrap. More than about 4 quotes overflow a 390px phone.
- `style.background` accepts default, soft, brand, dark, page or `#rrggbb`. Use a hex for an exact color.
- Painted dark sections do not remap every surface token. Check tables and highlighted columns on dark.
- Split ratio should match the image aspect, or the image is cropped.
- Transparent PNGs get a grey placeholder. Flatten them onto the section color before upload.
- Image upload: `mint_image_upload`, then PUT the file. No confirm call needed.
- When you edit richText `html`, unset `doc` in the same operation.
- Links must start with `https://`, `/`, `mailto:` or `tel:`. Use `/#anchor`.
- Native forms keep `placeholder` and `help`. They drop `autocomplete` and refuse hidden controls.
- Every page gets a Built on Peerfold badge (bottom left) and a consent banner. Keep key content away from the badge.

## Testing
- Use `wait_until="load"` for pages with video. `networkidle` never ends while video streams.
- Dismiss the consent banner before shots.
- When you hover a nav toggle in Playwright, prefix the selector with `header` so FAQ summaries do not match first.
