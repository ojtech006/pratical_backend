# PracticalDesk COS 101 Exercise Templates

Two selectable layouts have been added, based on the two uploaded COS 101 practical-exercise examples. The examples' personal details are **not** hardcoded; the generated document uses the student's submitted details and exercise text.

## Template choices

- `CLASSIC_SAMPLE` — Classic Student Template: student/course information panel, application letter, separate CV page, and numbered saving instructions.
- `SIMPLE_SAMPLE` — Simple COS 101 Template: compact course/matric/name heading, application letter, CV, saving steps, and renaming/printing section.

The existing `CLASSIC_BLUE`, `MODERN_TEAL`, `BURGUNDY_EDITORIAL`, and `CHARCOAL_GOLD` visual designs remain available independently.

## API

`GET /api/health/` now includes an `exercise_templates` array with the keys, names, and descriptions.

For `POST /api/reports/`, send `assignment_type: "EXERCISES"` and one of these fields:

```json
{
  "assignment_type": "EXERCISES",
  "exercise_template": "CLASSIC_SAMPLE",
  "student_name": "Student Name",
  "matric_number": "MATRIC_NUMBER",
  "course_code": "COS 101",
  "practical_title": "Computer Studies",
  "payment_reference": "YOUR_APPROVED_PAYMENT_REFERENCE",
  "application_letter": "Your application letter text...",
  "cv_content": "Your CV text...",
  "saving_steps": "1. Open Microsoft Word...\n2. Save the document...",
  "extra_notes": "Optional additional instructions..."
}
```

Use `SIMPLE_SAMPLE` to select the second layout. If omitted, the backend defaults to `CLASSIC_SAMPLE`. Invalid keys return HTTP 400 with the available choices. The response includes the selected `exercise_template`.

## Apply the migration

```bash
python manage.py migrate generator
```

Then restart the Django application.

## Frontend integration

Add a template selector only when `assignment_type === "EXERCISES"` and submit its selected key as `exercise_template`. The existing backend ZIP did not include the React frontend, so no frontend files are changed in this patch.
