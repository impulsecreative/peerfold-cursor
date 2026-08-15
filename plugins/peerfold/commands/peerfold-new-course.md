---
name: peerfold-new-course
description: Scaffold a Peerfold course from a content outline over MCP — outline, validated lesson bodies, settings, health check — and stop before publishing.
---

# New Peerfold course

Turn an outline the user supplies (a document, a list of topics, notes in the
chat) into a draft course in the connected Peerfold workspace.

Follow the `course-builder` skill for the full contract. This command is the short
path.

## 1. Agree on the outline first

Restate the chapter and lesson structure you intend to create, with each lesson's
`kind` (`lesson`, `exam`, or `scorm`), and get confirmation. Creating twenty
lessons the user did not want is cheap to do and tedious to undo.

If the user has not named a workspace and more than one key could be in play,
confirm which workspace the MCP connection is scoped to before writing anything.
Prefer a `sk_test_…` sandbox key while iterating.

## 2. Create and read back

```
create_course { title, slug, description, empty: true }
get_course { course_id }
```

`empty: true` skips the Chapter 1 / Lesson 1 scaffold. The read gives you the ids
every later call needs.

## 3. Build the outline

`add_chapter` per chapter, then `add_lesson` per lesson. Before drafting a lesson
from scratch, consider `copy_lesson` or `link_lesson` if the workspace already
teaches that material — ask the user which they want when it is ambiguous.

## 4. Draft bodies against the registry

For each content lesson: `list_block_types` and `get_block_schema` for the types
you plan to use, then `validate_blocks`, then `update_lesson_blocks`. Keep the
`normalized` array from validation so block ids stay stable. Never guess a prop
name.

## 5. Exams

Rules go in `set_course_settings { exam }`. Questions go in `set_exam_questions`,
which replaces the whole list. Radio questions (`multiple: false`) may have
exactly one correct answer.

## 6. Settings, access, health

`set_course_settings` for pricing or lead capture (mutually exclusive),
certificates, display and sequencing. `set_access_rules` for who may enroll.
Then `course_health { course_id }`.

## 7. Stop here

Report to the user:

- The course id and slug.
- The outline as created.
- `course_health` output, with blockers called out separately from advisory
  warnings and issues.
- The exact `publish_course` call they can approve.

**Do not publish.** Publishing is an explicit, deliberate act and it is the user's
to make. Only call `publish_course` if the user asks for it in this conversation,
and only pass `confirm_issues: true` after telling them what the issues are.
