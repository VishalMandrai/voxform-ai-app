"""
CSV rendering for response export.

Kept separate from AnalyticsService on purpose: "what data does a form's
responses contain" (service) and "how is that data serialized to CSV"
(this module) are different responsibilities. A future "export as
XLSX" or "export as JSON" feature is a new function here, not a change
to AnalyticsService.
"""

import csv
import io

from app.analytics.service import FormForExport, ResponseRow


def render_responses_csv(form: FormForExport, rows: list[ResponseRow]) -> str:
    buffer = io.StringIO()
    column_names = _unique_column_names(form.fields)
    fieldnames = ["response_id", "submitted_at"] + list(column_names.values())
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()

    for row in rows:
        csv_row = {
            "response_id": row.response_id,
            "submitted_at": row.submitted_at,
        }
        for f in form.fields:
            csv_row[column_names[f.id]] = row.answers_by_field_id.get(f.id, "")
        writer.writerow(csv_row)

    return buffer.getvalue()


def _unique_column_names(fields) -> dict[str, str]:
    """
    Maps field_id -> a CSV column name, disambiguating duplicate labels.

    Forms don't enforce unique field labels (two "Notes" fields are
    valid), but CSV headers must be unique or csv.DictWriter would
    silently overwrite one column's data with another's. Ties are
    broken by appending the field's position among same-labeled fields.
    """
    seen_counts: dict[str, int] = {}
    column_names: dict[str, str] = {}
    for f in fields:
        seen_counts[f.label] = seen_counts.get(f.label, 0) + 1
        occurrence = seen_counts[f.label]
        column_names[f.id] = f.label if occurrence == 1 else f"{f.label} ({occurrence})"
    return column_names
