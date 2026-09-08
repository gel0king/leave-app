import os
from datetime import date
from datetime import datetime as dt

from pypdf import PdfReader, PdfWriter

from app.utils.config import get_form_path, get_leave_requests_dir


LEAVE_TYPE_FIELD_MAP = {
    "Annual Leave": "leave_annual",
    "Sick Leave": "leave_sick",
    "Emergency Leave": "leave_emergency",
    "Military Leave": "leave_military",
    "Leave Without Pay": "leave_lwop",
    "Extended Sick Leave": "leave_extended_sick",
    "Jury Duty": "leave_jury",
    "Holiday Leave": "leave_holiday",
    "Other": "leave_other",
}

def format_time_12h(time_str):
    if not time_str:
        return ""

    try:
        return dt.strptime(time_str, "%H:%M").strftime("%I:%M %p").lstrip("0")
    except ValueError:
        return time_str

def fill_leave_request_pdf(employee, leave_type_name, other_specify, total_hours, from_date, from_time, to_date, to_time, comments, log_id):
    template_path = get_form_path()

    reader = PdfReader(template_path)
    writer = PdfWriter()
    writer.append(reader)

    field_values = {
        "employee_name": f"{employee.name} #{employee.employee_number}",
        "date_of_request": date.today().strftime("%m/%d/%Y"),
        "total_hours": str(total_hours),
        "from_time": format_time_12h(from_time),
        "from_date": from_date.strftime("%m/%d/%Y") if from_date else "",
        "to_time": format_time_12h(to_time),
        "to_date": to_date.strftime("%m/%d/%Y") if to_date else "",
        "comments": comments or "",
    }

    checkbox_field = LEAVE_TYPE_FIELD_MAP.get(leave_type_name)
    if checkbox_field:
        field_values[checkbox_field] = "/Yes"

    if leave_type_name == "Other" and other_specify:
        field_values["leave_other_specify"] = other_specify

    for page in writer.pages:
        writer.update_page_form_field_values(page, field_values)

    output_dir = get_leave_requests_dir()
    filename = f"{employee.employee_number}_{date.today().isoformat()}_{log_id}.pdf"
    output_path = os.path.join(output_dir, filename)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path