---
name: enrollment-manager
description: Enroll learners in Peerfold courses, set deadlines, read progress and completions, and correct a learner's record over MCP. Use when asked who is enrolled, who is behind, to enroll or unenroll people, or to report on a course or a learner.
---

# Enrollment manager

The tools that move people through courses, and the rules that keep an agent
from emailing or enrolling anybody the user did not intend.

## Confirm before you act

Three actions need a yes from the user in this conversation, every time, with
the names or the count in front of them:

- Enrolling more than one person (`enroll_learners`, or `enroll_learner` in a
  loop).
- Sending email. Only `enroll_learner { notify: true }` and
  `complete_course_for_learner` can email a learner from this skill. Default to
  silent and say so.
- Removing anything: `unenroll_learner`, `set_lesson_completion { completed: false }`.

Read the roster back to the user before a bulk call. An email address nobody
uses creates a new person, so a typo mints a human.

## Enroll

```
enroll_learner  { email, course_id | course_slug, name?, due_at?, notify? }
enroll_learners { emails[] | list_id, course_id | course_slug, due_at? }
```

- The course must be published. A draft has no revision to enroll into.
- Enrollment is an admin grant. Access rules and price do not apply, so this is
  how to give somebody a priced course without charging them.
- Idempotent. Somebody already enrolled is reported as `alreadyEnrolled` and
  nothing changes, so a retry is safe.
- `name` applies only when the call creates the learner.
- `notify` defaults to false. When true, the learner gets one localized message
  with the course title, a button that opens it, and how to sign in. The bulk
  tool cannot email anybody.
- The bulk tool returns per-row results. A bad address in one row does not undo
  the others. Over the batch cap the whole call is refused; split the list.

Saved lists: `create_learner_list` (find-or-create by name), `add_list_members`,
`list_learner_lists`, `get_learner_list`, `remove_list_member`. A list is a
`peerfold_list` access rule or the `list_id` of a bulk enrollment. Adding to a
list emails nobody and enrolls nobody.

## Unenroll

```
unenroll_learner { email | member_id, course_id | course_slug }
```

Deletes the learner's progress with the enrollment. It is refused when another
system owns the row, and the refusal says what to do instead: a purchase (refund
the order), an organization seat (unassign the seat), a HubSpot list rule (remove
them from the list), or a membership (it comes back next time they open the
course). Report the refusal to the user as written; do not work around it.

## Deadlines

```
set_enrollment_due_date { enrollment_id, due_at | null }
list_overdue { organization_id?, course_id? }
```

`due_at` takes a bare date (which resolves to the end of that day, UTC) or a full
instant. `null` clears the deadline. Reminders already sent are not sent again
when a deadline moves. Deadlines never remove access. `list_overdue` is one row
per learner and course, oldest first. `list_learners { due: "overdue" }` is the
one-row-per-person view of the same facts.

## Progress and reporting

| Tool | Answers |
| --- | --- |
| `list_learners` | Who is enrolled, filtered by search, status, course, source, last activity, deadline state and certificate expiry. Every row carries `nextDueAt` and `overdueCount`. |
| `get_learner_progress` | Everything about one learner by `member_id` or `email`: every enrollment with progress, per-lesson time, and every exam with score, attempts and outcome. |
| `get_course_stats` | Per-course enrollments, started, completed, completion rate, average progress, exam pass rate and average score. Omit `course_id` for every course. |
| `get_organization_progress` | The same roll-up for one organization. |
| `list_completions` | Completions oldest first with the certificate each produced. Built for polling: keep `next_cursor` and pass it back; stop when it is null. Never poll by timestamp alone. |
| `get_analytics_summary` | Workspace-level figures. |

## Correct a record

```
set_lesson_completion       { enrollment_id, lesson_id, completed, score? }
complete_course_for_learner { member_id | email, course_id, notify?, exam_scores?, reason }
import_completions          after preview_completion_import
```

`set_lesson_completion { completed: true }` marks one lesson complete through the
learner's own completion path, skipping release and must-watch gates. When it
finishes the course, the certificate, CEUs, programs, CRM rows and webhooks follow
the course's rules. `completed: false` clears it and a finished course goes back
to in progress. Both are refused when the learner is already certified or their
access is turned off.

`complete_course_for_learner` marks every remaining lesson complete and runs the
course completion once. It emails the certificate unless `notify` is false. Ask
the user before calling it, and pass the reason they give you.

`preview_completion_import` shows what a historical import would do before
`import_completions` writes it. Show the preview to the user first.

## Access, merges, privacy

- `set_learner_access { blocked: true }` turns a person's access off and revokes
  their tokens. Confirm with the user and record the reason.
- `merge_learners` joins two records of the same person. Read both with
  `get_learner_progress` and show the user which one survives before calling it.
- `export_learner_data` and `erase_learner` serve privacy requests. Erasure is
  permanent. Never call it without an explicit instruction naming the person.

## Checks before you say it is done

- You named the course, the people and the count before any bulk or email call,
  and the user said yes.
- Every row of a bulk result was read, and failed rows were reported.
- A refusal from `unenroll_learner` was reported as written.
