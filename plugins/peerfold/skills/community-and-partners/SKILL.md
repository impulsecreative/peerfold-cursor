---
name: community-and-partners
description: Work with the Peerfold community (cohorts, threads, moderation) and the partner program (leads, deals, commissions, referral links) over MCP and the REST API, including their embed surfaces. Use when building or administering community discussions or a partner portal.
---

# Community and partners

Two add-on products share the platform with the LMS. Both are entitlement-gated,
both are namespaced, and both answer `404` rather than a paywall when a workspace
does not have them.

## Community

### Over MCP

Community tools are unprefixed, like the LMS tools, and need the community add-on.

**Rooms** — `list_cohorts` shows every discussion room including private and
archived ones, because a room you cannot see is a room you cannot moderate.
`get_cohort` reads one in full: access tier, engagement switches, tags, member and
thread counts. `create_cohort` sets the tier — public, signed-in members, or
invite-only — and it is enforced on every read and every join. `update_cohort` is a
merge patch, and changing a room's URL key changes the live URL, so old links stop
resolving. `set_cohort_active` archives or restores without losing a thread or a
member. `delete_cohort` destroys an EMPTY room and refuses the moment it holds a
post — archive that one instead.

**Discussions** — `list_cohort_threads` returns pinned first then newest, hidden
threads included and deleted ones never. `get_thread` reads one with its comments,
solutions first then oldest first, by slug or id. `create_thread` posts as a NAMED
member: they follow the thread and join the cohort as side effects, and a
moderator is never demoted by that join. `update_thread` and `update_comment` edit
in place. `set_post_flags` pins a thread and marks the comment that answered the
question as the solution. `set_post_reaction` and `vote_poll` carry engagement.

**Moderation** — `moderate_post` hides a post pending review or marks it withdrawn;
its author still sees it and nobody else does. `delete_post` is a soft delete: the
row survives, the URL key is freed, and who removed it is recorded.
`restore_post` puts a hidden or deleted post back, and because the URL key is
re-derived it can return at a suffixed slug. `list_moderation_queue` is the work
list — posts that are not live, oldest first, with the queue tallies.
`list_abuse_reports` shows open reports oldest first (a work list) and resolved
ones newest first (history); `resolve_abuse_report` closes or reopens one and
deliberately does not touch the reported content.

**People** — `list_cohort_members` is one room's roster with role, how they
arrived and how much they have written there. `add_cohort_member` is the grant
path and the only way into an invite-only room; it never lowers an existing role.
`remove_cohort_member` revokes access to a room and leaves their posts, because
membership is not authorship. `set_cohort_role` promotes or demotes a moderator of
ONE room and is the only path that may lower a role;
`set_member_community_role` does it workspace-wide, across every cohort plus the
queue and the reports. `list_community_members` is the directory — where you find
a username — and `get_community_profile` reads one member's bio, workspace role,
badges, followers and leaderboard score.

**Ideas and search** — `create_idea`, `list_ideas`, `vote_idea`, `set_idea_status`
and `get_idea_cap` run an idea board; `search_community` searches across the
community.

### Over the API

Every route under `/api/v1/community/*` requires a **learner JWT**. There is no
secret-key read of the community and no public mode — a discussion is about
signed-in people. The surface covers cohorts and their threads, one thread and its
comments, posting a comment, reactions and poll votes, follows, the member
directory and one profile, notifications, the feed, badges, ideas and their votes,
search, and filing an abuse report.

Bodies are read and written as **plain text** by the shipped surfaces. A post
arrives as a Tiptap document and as server-sanitized `content_html`; the community
renderer renders neither as markup — it walks the document and writes one `<p>`
per block with `textContent`. The composer builds the simplest legal document: one
paragraph of one text node per non-empty line. Preserve that if you write your own
renderer.

## Partners

### Over MCP

Every partner tool is prefixed `prm_`, because names like `list_leads`,
`list_deals` and `get_partner` are ones a CRM-adjacent product will want again.
All of them run on the program-owner (admin) plane and need the `prm` add-on,
which is checked once when the program is opened rather than per tool.

**Reads** — `prm_list_partners` / `prm_get_partner`, `prm_list_tiers`,
`prm_list_leads` / `prm_get_lead`, `prm_list_deals` / `prm_get_deal`,
`prm_list_commissions`, `prm_get_partner_statement`, `prm_list_payout_runs`,
`prm_list_referral_links`, `prm_get_referral_summary`, `prm_get_import_status`.

**Writes** — `prm_register_lead`, `prm_set_lead_status`, `prm_reassign_lead`,
`prm_release_lead`. The admin plane has no partner identity of its own, and a
registered lead belongs to somebody, so `prm_register_lead` takes an explicit
`partner` and registers AS them — exactly as `create_thread` takes an author. The
permission check then runs against THAT partner's tier, so a tier that cannot
create deals still cannot, whoever asked.

**What is deliberately not a tool**: approving an accrual, voiding one, creating
or recording a payout run, and editing a tier's rate. Those decide what a person
is paid and on what terms, and they stay behind an authenticated admin session
with a writing role — "an assistant did it" is not an answer to "who approved this
commission." All of them remain READABLE, which is what an agent asked to
reconcile a payout actually needs.

### Over the API

The partner plane is split by audience:

| Routes | Credential | Whose view |
| --- | --- | --- |
| `/api/v1/prm/me`, `/leads`, `/deals`, `/commissions`, `/referral-links`, `/attributions` | Learner JWT | The signed-in partner's own |
| `/api/v1/prm/program/{partners,tiers,leads,deals,commissions,attribution}` | Secret key or OAuth token | The program owner's |

A partner is **not a second login**. The partner plane takes the same token every
other learner surface carries, and what makes somebody a partner is a row in the
workspace, resolved server-side. Nothing extra is emitted by a host page.

## Embedding either one

Three shipped surfaces cover both — `render-community-cohorts.js`,
`render-community-threads.js` and `render-partner.js` — plus the matching HubSpot
modules (Community Cohorts, Community Discussions, Partner Portal). All three are
**session-only**: they have no public mode and never will, because both rails
require a learner JWT before they read anything. Auth mode is `assertion` (default)
or `redirect`.

The partner module renders any of five views — dashboard, leads, deals,
commissions, referral links — from an identical field set, so a full portal is the
module dropped in several times with a different view on each. The first Peerfold
surface in page order writes the shared connection and the rest inherit it.

The cohort directory links each card to a page on the CUSTOMER's own site, from a
pattern such as `/community?cohort={slug}`. It is the one link in the package that
is not resolved against the Peerfold base URL, and nothing validates it for you.
Pair it with a discussions surface whose cohort field is left blank so it reads
the slug from the address — one page then serves every room.

## The 404 posture, and why it matters here

Both rails answer `404` rather than a paywall when the add-on is absent, and the
partner rail answers the same `404` when the caller simply is not a partner. The
two facts are deliberately indistinguishable.

So these surfaces treat `404` as an answer and remove themselves from the page
entirely, with one `console.info` line. Not an upsell, not an error box, not an
empty bordered box. A partner is somebody else's customer's contractor who cannot
buy the add-on and is not owed the news that a program exists which they are not
in. Two consequences for anything you build:

- Do not put a heading in a separate element beside a self-removing surface — it
  would outlive the surface and tell a member exactly what the `404` declined to
  tell them. Set the heading on the surface's own field.
- On a workspace without the add-on, "my page looks fine but the module is gone"
  is the expected result, not a bug to chase.
