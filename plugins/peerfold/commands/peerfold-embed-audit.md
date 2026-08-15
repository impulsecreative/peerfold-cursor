---
name: peerfold-embed-audit
description: Audit a codebase's Peerfold embed wiring — key exposure, config object, data attributes, auth mode, CORS origins, and link resolution.
---

# Audit Peerfold embed wiring

Review this repository for how it embeds Peerfold learner surfaces, and report
what is wrong before a page ships. Read the `peerfold-embeds` and `peerfold-keys`
rules for the contracts you are checking against.

## 1. Find the wiring

Search the repository for:

- `PeerfoldConfig`, `PeerfoldModules`, `PF.api`
- `data-peerfold-` attributes
- `peerfold.js`, `render-cards.js`, `render-hero.js`, `render-account.js`,
  `render-certificate.js`, `render-lesson-native.js`,
  `render-community-cohorts.js`, `render-community-threads.js`,
  `render-partner.js`
- `pk_live_`, `pk_test_`, `sk_live_`, `sk_test_`, `PEERFOLD_SECRET_KEY`
- `X-Peerfold-Publishable-Key`, `Peerfold-Version`, `membership-assertion`

## 2. Key exposure — report as blocking

- Any `sk_live_…` or `sk_test_…` literal anywhere in the repository, in any file
  type, including comments, fixtures and tests.
- A secret key reaching client code: bundled, inlined into a template, or exposed
  through a build-time variable that ships to the browser (for example a
  `NEXT_PUBLIC_`-style prefix, or a Vite `import.meta.env` value without a server
  boundary).
- An assertion signing secret rendered into a page rather than used server-side to
  produce only the digest.

A publishable key in page source is correct and not a finding.

## 3. Config object

- Exactly one `window.PeerfoldConfig`, written with the first-writer-wins guard
  (`window.PeerfoldConfig = window.PeerfoldConfig || { … }`).
- The bootstrap (`peerfold.js`) loads before any renderer.
- Every surface on a page agrees on `baseUrl`, `publishableKey` and `authMode` —
  the first in page order wins, so a second, different config is silently ignored.
- `baseUrl` comes from configuration rather than a hardcoded placeholder
  subdomain, and has no trailing path.

## 4. Auth mode

- `assertion` — the payload is built server-side as
  `portalId|contactVid|email|tsSeconds` and signed as `md5(secret + "|" + payload)`
  in lowercase hex, emitted only inside a signed-in branch, and minted per render
  rather than cached.
- `redirect` — nothing extra is required, but confirm the redirect URI is
  registered in the workspace.
- `public` — confirm the surface actually supports it. Only the catalog honors
  `data-peerfold-public="1"`; the personal lists are about one signed-in person
  and a keyed request for them can only 401 behind the empty state.
- Community and partner surfaces in `public` mode are a finding: those rails are
  session-only.

## 5. Data attributes

- `data-peerfold-cards` is one of `catalog`, `enrollments`, `certificates`,
  `resources`. An unknown value renders the empty state and looks like a bug.
- `data-peerfold-partner` is one of `dashboard`, `leads`, `deals`, `commissions`,
  `referrals`.
- A cohort directory's thread-page pattern is a path on the host's OWN site and
  stays relative — flag any attempt to resolve it against the Peerfold base URL.

## 6. Links and origins

- Course links render `cms_url` from the API response rather than composing a
  portal path, so the workspace's front-end page map is honored.
- Every origin the site is published on — with and without `www` — is expected to
  be on the workspace CORS allowlist. You cannot verify the allowlist from the
  repository, so list the origins the code implies and tell the user to confirm
  them under Settings → Developers.

## 7. Failure posture

- No surface renders a status code, an error box, or an upsell.
- Nothing beside a community or partner surface would outlive it when the surface
  removes itself on a 404 — particularly a heading in a separate element.

## Report

Group findings as **blocking** (key exposure, a secret in client code), **broken**
(wiring that cannot work: two configs, missing bootstrap, invalid attribute
value), and **advisory** (hardcoded base URL, composed links instead of
`cms_url`). Give the file and line for each, and the specific fix. If the
repository contains no Peerfold embed wiring at all, say so plainly rather than
inventing findings.
