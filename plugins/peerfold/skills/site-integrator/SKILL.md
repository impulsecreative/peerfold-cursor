---
name: site-integrator
description: Put Peerfold learner surfaces on a site the customer already owns — script tag, publishable key, auth modes, HubSpot modules, WordPress connect, and the front-end page map. Use when embedding a catalog, course hero, my-learning list, certificates, community, or partner portal into an existing site.
---

# Site integrator

Embedding is the middle path between running on the hosted Peerfold portal and
going fully headless: the customer keeps their own site, their own navigation and
their own domain, and Peerfold data is fetched into it from the browser.

## The three-part setup, and the part everybody forgets

A site that reads a workspace from a browser needs three things:

1. The workspace **base URL** — the portal origin, e.g.
   `https://your-workspace.peerfold.app` or the workspace's custom domain.
2. A **publishable key** (`pk_live_…`). Never a secret key — a browser context
   cannot hold one.
3. The site's **origin on the CORS allowlist**. Miss this and the browser blocks
   the response with nothing in any server log to read, and every surface renders
   its empty state on an otherwise correct page. Check this first when a surface
   is mysteriously blank.

All three live under **Settings → Developers**. Entries on the allowlist are exact
matches — no wildcards, no subdomain expansion — must be https (plain http for
localhost only), and are capped at 20 per workspace. `https://www.example.com` and
`https://example.com` are two different origins.

## Connect a site in one call

`POST /api/v1/connect/wordpress` (secret key, server to server) does all three at
once, which is what a plugin's or an installer's setup screen should call:

```bash
curl -X POST https://app.peerfold.com/api/v1/connect/wordpress \
  -H "Authorization: Bearer $PEERFOLD_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"origin":"https://www.example.com","site_name":"Example"}'
```

It allowlists the origin FIRST (the step that can legitimately fail, so no orphan
credential is left behind), then finds or mints a publishable key named for the
origin, then reports what the site needs. The response carries `origin`,
`base_url`, `admin_base_url`, `sdk_url`, `publishable_key`, `key_id`, `key_name`,
`key_created`, `origin_added`, `cors_origins`, `workspace`, and a `capabilities`
object to branch on rather than deriving behavior from plan names.

It is **idempotent per origin** — the key name is derived from the origin, so a
reactivated plugin, a settings page saved twice, or a retried install finds the
key the last connect made instead of leaving a trail of near-identical keys.
`key_created` and `origin_added` say whether this particular call changed
anything, which is what makes it safe to call on every boot. The key shows up in
Settings → Developers as `WordPress — your-site.com` and is revoked like any
other.

Despite the path name, nothing about it is WordPress-specific: it is
product-neutral and works for any host that can make a server-side call. The
allowlist alone is readable and replaceable at `GET` / `PUT /api/v1/cors-origins`
(the `PUT` replaces it wholesale — send every origin you want kept).

## The browser surfaces

Nine scripts and one stylesheet draw a catalog, a course hero, a my-learning list,
certificates, resources, an account block, a lesson body, community discussions
and a partner portal into any page that can serve a `<script>` tag. Vanilla
ES2019 — no framework, no bundler, no build step.

| File | Draws | Mount selector |
| --- | --- | --- |
| `js/peerfold.js` | the bootstrap: auth, the token, `PF.api` | (whole page) |
| `js/render-cards.js` | catalog / enrollments / certificates / resources grids | `[data-peerfold-cards]` |
| `js/render-hero.js` | one course above the fold | `[data-peerfold-hero]` |
| `js/render-certificate.js` | one certificate, verified by serial | `[data-peerfold-certificate]` |
| `js/render-account.js` | the signed-in learner's name, avatar and links | `[data-peerfold-account]` |
| `js/render-lesson-native.js` | a lesson's block JSON, drawn into the host page | `[data-peerfold-lesson-native]` |
| `js/render-community-cohorts.js` | the cohort directory | `[data-peerfold-community-cohorts]` |
| `js/render-community-threads.js` | one cohort's threads, comments, composer | `[data-peerfold-community-threads]` |
| `js/render-partner.js` | the partner portal, five views | `[data-peerfold-partner]` |

Load `peerfold.js` first; each renderer awaits `window.PeerfoldModules.ready`, so
their order among themselves does not matter and a page may carry several. The
bootstrap also loads the typed browser SDK from `{baseUrl}/sdk/peerfold.js` and
hands it to `window.PeerfoldModules.client` if it arrives — a convenience, since
every renderer uses `PF.api` directly and a blocked SDK costs nothing.

Configuration is one `window.PeerfoldConfig` object (first writer wins) plus
per-surface `data-peerfold-*` attributes. The three auth modes are `assertion`,
`redirect` and `public`. See the `peerfold-embeds` rule in this plugin for the
full contract, the membership-assertion grammar, and why community and partner
surfaces remove themselves on a 404.

## HubSpot

Twelve drag-and-drop CMS modules render courses, community and the partner portal
on any page of any theme — no parent theme, no `theme.json`, no GraphQL, no HubDB,
no CRM read, no serverless function. Each module emits a skeleton shell plus its
own configuration, and the browser scripts above fetch everything else.

| Module | Reads | Auth modes |
| --- | --- | --- |
| Course Catalog | `/api/v1/lms/catalog` | `assertion` (default), `redirect`, `public` |
| Course Hero | `/api/v1/lms/courses/{slug}` | `public` (default), `assertion`, `redirect` |
| My Courses | `/api/v1/lms/enrollments` | `assertion` (default), `redirect` |
| My Certificates | `/api/v1/lms/certificates` | `assertion` (default), `redirect` |
| Resources | `/api/v1/lms/resources` | `assertion` (default), `redirect` |
| Certificate | `/api/v1/lms/certificates/verify/{serial}` | `public` (default), `assertion`, `redirect` |
| Account | `/api/v1/lms/me` | `assertion` (default), `redirect` |
| Lesson Player | nothing in `embed`; `/api/v1/lms/courses/{slug}` in `native` | assertion only |
| SCORM Player | nothing — the launcher URL carries the signature | assertion only |
| Community Cohorts | `/api/v1/community/cohorts` | `assertion` (default), `redirect` |
| Community Discussions | `/api/v1/community/cohorts/{slug}/threads`, `/api/v1/community/threads/{ref}`, `POST …/comments` | `assertion` (default), `redirect` |
| Partner Portal | one of `/api/v1/prm/{me,leads,deals,commissions,referral-links}`, `POST /api/v1/prm/leads` | `assertion` (default), `redirect` |

Signed-in modules need HubSpot **private content** configured and the assertion
signing secret pasted into each module in the page editor — the field is per
module, not per page. On an unprotected page there is no membership contact to
read, so the module renders a "log in to continue" button instead.

A SCORM launch is a redirect, not an API call:

```text
GET {baseUrl}/api/portal/embed/scorm
  ?client_id=pk_live_…
  &payload=<urlencoded portalId|contactVid|email|tsSeconds>
  &sig=<lowercase hex md5(secret|payload)>
  &course=<course-slug>&lesson=<lesson-slug>
→ 303 {baseUrl}/embed/<course>/<lesson>   (session cookie set)
```

Put that URL in an iframe and let the redirect happen inside the frame. Each
launch spends its signature, and a page admits exactly one player, so a marketing
page should link to a lesson page rather than embed a player beside a hero.

**A worked example**: `github.com/impulsecreative/peerfold-elevate` is a HubSpot
child theme extending HubSpot's Elevate with the twelve modules and five example
pages (academy catalog, course page, my learning, community, partner portal).
Treat it as a reference to clone and cut down — its README is explicit that it is
an example rather than a supported product, and it carries an honest list of what
has not yet been verified against a live portal.

The alternative package is the full HubLMS theme, which extends the Omega theme
and runs the whole learner site. A workspace already on that theme that only wants
its data to come from Peerfold wants **Settings → Repoint** instead, which changes
no files.

## Make links point at the customer's site

**Settings → Developers → Front end** is where a workspace says it reads
somewhere other than the hosted portal. Fill in which front end it runs, the site
address (origin only, no path), and a path pattern per page type — the course,
lesson or program's own slug goes in the placeholder. Leave a row blank and that
link keeps pointing at the Peerfold portal, so a workspace can map only the pages
it actually hosts.

Four rules decide a course's address, in order: an address set on the course
itself, then the pattern you typed, then a page discovered on the site by
Content-index sync, then the Peerfold portal. The **Course pages** card under the
form lists every published course with the address a learner would land on and
which rule produced it — resolved by the same code the API and the emails use, so
it is the answer rather than a preview of one.

Once saved, learner emails, CRM course links, certificate "what this was awarded
for" links, the admin "View live" button, and the `cms_url` / `url` fields on
catalog, course and enrollment reads all follow the map. Nothing needs
republishing: the surfaces and modules render `cms_url` from the API response.

Three link kinds stay on the portal on purpose, because they would break if they
moved — sign-in links (they work only on the address that issued them), checkout
return pages, and the learner's own profile and notification settings. Certificate
verification (`/verify/…`), badge documents (`/credentials/…`), the embedded
players and every `/api/…` endpoint also stay put, whatever is mapped.

## Checks before you say it is done

- The site's exact origin is on the CORS allowlist, with and without `www` if
  both are published.
- No `sk_` key appears anywhere the browser or the repository can see it.
- Surfaces sharing a page agree on base URL, key and auth mode.
- Course links render `cms_url` rather than a composed portal path.
- Community and partner surfaces were tested on a workspace without the add-on:
  the module vanishing with one console line is the pass, not a failure.
