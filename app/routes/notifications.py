from app.utils.compliance import (
    get_all_document_expirations,
    get_compliance_summary,
)
from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    send_file
)

from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/summary")
def notification_summary():
    records = get_all_document_expirations()
    summary = get_compliance_summary(records)

    attention_records = [
        record for record in records
        if record["status"] in (
            "expired",
            "expiring_soon",
            "upcoming"
        )
    ]

    attention_records.sort(
        key=lambda r: (
            0 if r["status"] == "expired" else
            1 if r["status"] == "expiring_soon" else 2,
            r["expiration_date"]
        )
    )

    return jsonify({
        "summary": summary,
        "records": [
            {
                **record,
                "expiration_date": record["expiration_date"].isoformat()
            }
            for record in attention_records
        ],
        "attention_count": (
            summary["expired"] + summary["expiring_soon"]
        )
    })



@notifications_bp.route("/compliance")
def compliance():

    records = get_all_document_expirations()

    summary = get_compliance_summary(records)

    document_type = request.args.get("type", "all")
    selected_statuses = request.args.getlist("status")

    if document_type != "all":
        records = [
            r for r in records
            if r["category"] == document_type
        ]

    if selected_statuses:
        records = [
            r for r in records
            if r["status"] in selected_statuses
        ]

    return render_template(
        "compliance.html",
        records=records,
        summary=summary
    )



@notifications_bp.route("/export")
def export_compliance():

    records = get_all_document_expirations()

    document_type = request.args.get("type", "all")
    statuses = request.args.getlist("status")

    if document_type != "all":
        records = [
            r for r in records
            if r["category"] == document_type
        ]

    if statuses:
        records = [
            r for r in records
            if r["status"] in statuses
        ]

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Compliance Report"

    headers = [
        "Employee / Policy",
        "Office",
        "Document Type",
        "Expiration Date",
        "Days Remaining",
        "Status"
    ]

    sheet.append(headers)

    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            "solid",
            fgColor="1E3F3D"
        )

    for record in records:

        sheet.append([
            record["employee_name"],
            record["office"] or "",
            record["category"],
            record["expiration_date"],
            record["days_remaining"],
            record["status"].replace("_", " ").title()
        ])

    for column in sheet.columns:
        max_length = max(
            len(str(cell.value or ""))
            for cell in column
        )

        sheet.column_dimensions[
            get_column_letter(column[0].column)
        ].width = max_length + 3

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="compliance_report.xlsx",
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )
