from app.analytics.csv_export import render_responses_csv
from app.analytics.service import FormForExport, ResponseRow
from app.forms.models import Field, FieldType


def make_field(label: str, field_type: FieldType = FieldType.TEXT) -> Field:
    return Field(label=label, field_type=field_type)


def test_csv_has_header_row_with_field_labels():
    fields = [make_field("Name"), make_field("Age", FieldType.NUMBER)]
    form = FormForExport(form_id="f1", title="Survey", fields=fields)

    csv_text = render_responses_csv(form, [])

    header = csv_text.splitlines()[0]
    assert header == "response_id,submitted_at,Name,Age"


def test_csv_includes_one_row_per_response():
    name_field = make_field("Name")
    fields = [name_field]
    form = FormForExport(form_id="f1", title="Survey", fields=fields)
    rows = [
        ResponseRow(response_id="r1", submitted_at="2026-01-01T00:00:00", answers_by_field_id={name_field.id: "Asha"}),
        ResponseRow(response_id="r2", submitted_at="2026-01-02T00:00:00", answers_by_field_id={name_field.id: "Ravi"}),
    ]

    csv_text = render_responses_csv(form, rows)
    lines = csv_text.splitlines()

    assert len(lines) == 3  # header + 2 rows
    assert "Asha" in lines[1]
    assert "Ravi" in lines[2]


def test_csv_missing_answer_renders_as_empty_string():
    name_field = make_field("Name")
    age_field = make_field("Age", FieldType.NUMBER)
    form = FormForExport(form_id="f1", title="Survey", fields=[name_field, age_field])
    rows = [
        ResponseRow(response_id="r1", submitted_at="2026-01-01T00:00:00", answers_by_field_id={name_field.id: "Asha"}),
    ]

    csv_text = render_responses_csv(form, rows)
    lines = csv_text.splitlines()

    # "Asha" answered, Age column empty — trailing comma with nothing after it.
    assert lines[1] == "r1,2026-01-01T00:00:00,Asha,"


def test_csv_disambiguates_duplicate_field_labels():
    """Two fields with the same label must not collide into one CSV column."""
    notes_1 = make_field("Notes")
    notes_2 = make_field("Notes")
    form = FormForExport(form_id="f1", title="Survey", fields=[notes_1, notes_2])
    rows = [
        ResponseRow(
            response_id="r1",
            submitted_at="2026-01-01T00:00:00",
            answers_by_field_id={notes_1.id: "first note", notes_2.id: "second note"},
        ),
    ]

    csv_text = render_responses_csv(form, rows)
    lines = csv_text.splitlines()

    assert lines[0] == "response_id,submitted_at,Notes,Notes (2)"
    assert "first note" in lines[1]
    assert "second note" in lines[1]
