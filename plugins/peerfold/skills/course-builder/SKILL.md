---
name: course-builder
description: Build a complete Peerfold course over MCP — outline, lesson bodies, media, exam rules and questions, access rules, health check, publish, preview. Use when asked to create, restructure, or ship course content in a Peerfold workspace.
---

# Course builder

The authoring flow the Peerfold MCP server prescribes, in the order that matters.
The order is the part that is easy to get wrong: read before a whole-array write,
validate before spending a save, health before publish, publish before preview.

## Before you start

Confirm the MCP server is connected and tenant-scoped to the workspace you mean.
Every tool operates on the tenant behind the connected credential, and every write
is audit-logged. If you are experimenting, connect with a `sk_test_…` key so you
are working in the sandbox.

## The flow

### 1. Create the course

```
create_course { title, slug, description, empty: true }
```

Pass `empty: true` when you are building the outline yourself — otherwise you get
a Chapter 1 / Lesson 1 scaffold you will spend two calls deleting. Pass an
`idempotency_key` if a retry could double-create.

### 2. Read what you just made

```
get_course { course_id }
```

This returns the chapter and lesson ids every later call needs, including the ids
of anything created for you.

### 3. Build the outline

```
add_chapter { course_id, title }
add_lesson  { course_id, chapter_id, title, kind }
```

`kind` is `"lesson"` (a block body), `"exam"` (graded, configured in step 6) or
`"scorm"` (bound in step 5). `update_chapter` renames a chapter and sets the image
shown beside it; `reorder_outline` applies a full desired order in one call.

### 4. Reuse before you draft

Check whether the workspace already teaches this. Onboarding, safety and
product-basics lessons recur across catalogs.

- `copy_lesson` — this course should OWN the content and diverge. New block ids,
  its own progress, media shared rather than duplicated. A live copy arrives
  unscheduled, so give it a date with `set_live_session`.
- `link_lesson` — the same content should stay in step everywhere it appears. The
  borrowed lesson is read-only, its content is edited in the source course, and
  each borrowing course picks changes up on its own next publish. Content lessons
  and SCORM only; exams and live lessons are copy-only.
- `detach_lesson` — turn a borrowed lesson into a plain independent copy in place.
  The escape hatch for diverging, and for deleting a source other courses borrow.

### 5. Write lesson bodies

Learn the shapes, then write:

```
list_block_types            → the catalog: labels, categories, nesting, prop names
get_block_schema { type }   → one type's JSON Schema, defaults, example node
validate_blocks { blocks }  → free dry run, exact per-block errors
update_lesson_blocks { lesson_id, blocks }
```

Editing an existing body always starts with `get_lesson_blocks` —
`update_lesson_blocks` replaces the WHOLE array, so writing without reading first
deletes every block you did not mention. It is refused on a borrowed lesson; edit
the source, or `detach_lesson` first.

Media tools return PROPS rather than writing a block, so there is one validated
write path: `mint_image_upload`, `mint_file_upload`, `attach_video`. For SCORM,
`list_scorm_packages` then `attach_scorm_package { lesson_id, package_id, sco_id }`
against a lesson that is already `kind: "scorm"` — importing the .zip itself stays
in the admin UI. For an interactive experience, ask
`scaffold_integration { kind: "interactive lesson content" }` BEFORE writing the
file: the reply carries the adapter to inline verbatim, the four functions, and
the sandbox rules a generated file would otherwise violate silently. Then
`mint_interactive_upload` → PUT → `confirm_interactive_upload` (this is where a
zip is unpacked and checked) → `attach_interactive_experience` → save the props
through `update_lesson_blocks`.

`generate_lesson_audio { lesson_id }` advances a background narration run a batch
at a time — call it while `pending` is true. It attaches an `audio` block itself,
is idempotent unless you pass `force: true`, and needs a connected speech account.

### 6. Exam rules and exam questions are two calls

This is the split integrations miss.

- RULES live in `set_course_settings { exam }` — passing score, attempts, whether
  results are shown.
- QUESTIONS live in `get_exam` / `set_exam_questions`, and `set_exam_questions`
  REPLACES the whole list.

A question is `{ prompt, answers[], multiple, isOpenEnded?, explanation?, image?, images? }`.
`multiple: false` (the default) is radio buttons and exactly one answer may be
correct — two keys on a radio question can never be answered, so it is refused.
`multiple: true` is checkboxes: the learner must pick every correct answer and no
incorrect one, with no partial credit. `isOpenEnded: true` carries no answers,
is graded manually, and parks every attempt containing it as `pending_manual`
until an admin awards it. Omit ids on first write; send ids read from `get_exam`
to edit in place, because in-flight attempts key on them.

### 7. Make it behave

```
set_course_settings { commerce | leadgen | certificate | exam | display |
                      sequencing | brief | seo | visibility | overview |
                      deadline | recertification | categories }
```

A merge patch field by field: send a value to change it, omit it to keep it, send
`null` to clear it. Two text pairs are easy to confuse — `brief` is the summary
learner search and `/llms.txt` read, `seo` is the title tag and meta description a
search engine shows. Commerce and lead capture are mutually exclusive server-side:
pricing a course turns lead capture off, and purchase always wins.

### 8. Decide who may enroll

```
set_access_rules { course_id, rules }
```

Replaces the rule set; an empty set is public. Rules are any-match. A price
supersedes rules entirely.

### 9. Give it a marketing page (optional)

```
get_program_landing_schema   → the section vocabulary, shared by courses and programs
get_course { course_id }     → the current landing.sections
set_course_landing { course_id, enabled, sections }
```

A validated section document, never free-form HTML, so an invalid page fails at
save rather than in front of a visitor. `sections` replaces the document whole;
`enabled` is a separate switch, and with it off the URL renders the course
overview it always has. An empty array is valid and restores the fully composed
default page. `set_program_landing` is the same call for a program.

### 10. Check, publish, preview

```
course_health  { course_id }   → warnings + issues (advisory), blockers (predictive)
publish_course { course_id }   → revision number, live learner URL, admin review URL
preview_course { course_id, lesson_id? }
```

Empty `blockers` means publish will succeed. `publish_course` refuses once on
structural issues and names them; re-call with `confirm_issues: true` to publish
anyway, deliberately. Nothing else publishes as a side effect. `preview_course`
returns a single-use link into the published revision as the reserved preview
member — no enrollment, and never synced to the CRM.

## Related tools worth knowing

- `duplicate_course`, `create_curated_course`, `create_program` /
  `set_program_courses` / `update_program` for multi-course credentials.
- `enroll_learner` / `enroll_learners` / `unenroll_learner`, and
  `set_enrollment_due_date` for deadlines.
- `get_course_stats`, `get_learner_progress`, `list_completions`,
  `get_analytics_summary` for reporting after the fact.
- `set_course_ceus` / `get_course_ceus` / `list_ceu_types` for continuing-education
  credit. `set_course_ceus` replaces the whole list.
- `delete_course` moves a course into a 30-day hold and requires `confirm_title`
  matching the exact title plus a reason; `restore_course` takes it back out
  before the hold expires. Issued certificates keep verifying either way.

## Checks before you say it is done

- `course_health` returns no blockers.
- Every lesson body was validated before it was written.
- Exam questions were written with `set_exam_questions`, not assumed to be part of
  `set_course_settings`.
- `publish_course` was called explicitly, and you reported the revision number and
  the live URL it returned.
