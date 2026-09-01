"""
Generates Leave form if leave form is not found
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, black

OUT = "./leave_request_template.pdf"
INK = black
LINE = HexColor("#333333")

W, H = letter
c = canvas.Canvas(OUT, pagesize=letter)
form = c.acroForm


def center(text, y, size=14, bold=True):
    c.setFont("Times-Bold" if bold else "Times-Roman", size)
    c.drawCentredString(W / 2, y, text)


def label(x, y, text, size=11, bold=False, font="Times-Roman"):
    c.setFont(("Times-Bold" if bold else font), size)
    c.drawString(x, y, text)


def box(x, y, w, h):
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.rect(x, y, w, h, fill=False, stroke=True)


def hline(x1, x2, y):
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.line(x1, y, x2, y)


def vline(x, y1, y2):
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.line(x, y1, x, y2)


def checkbox(name, x, y, size=11, tooltip=None):
    form.checkbox(
        name=name, tooltip=tooltip or name,
        x=x, y=y, size=size,
        checked=False, borderColor=LINE, fillColor=None,
        borderWidth=1,
    )


def text_field(name, x, y, w, h=14, tooltip=None, font_size=9, value=""):
    form.textfield(
        name=name, tooltip=tooltip or name,
        x=x, y=y, width=w, height=h,
        borderStyle="underlined", borderColor=LINE, borderWidth=0.75,
        fillColor=None, textColor=INK, fontSize=font_size, forceBorder=True,
        value=value,
    )


# ---------- Title ----------
top = H - 60
center("TEXAS COOPERATIVE INSPECTION PROGRAM", top, size=14)
center("REQUEST FOR APPROVAL OF LEAVE", top - 20, size=14)

# Outer table starts here
left, right = 54, W - 54
y = top - 55

# Row: Employee / Date of Request
row_h = 24
box(left, y - row_h, right - left, row_h)
label(left + 4, y - row_h + 7, "Employee:")
text_field("employee_name", left + 65, y - row_h + 5, 300)
label(left + 380, y - row_h + 7, "Date of Request:")
text_field("date_of_request", left + 480, y - row_h + 5, right - (left + 480) - 4)
y -= row_h

# Row: Program/Office
box(left, y - row_h, right - left, row_h)
label(left + 4, y - row_h + 7, "Program/Office:")
text_field("program_office", left + 100, y - row_h + 5, 260, value="Texas Cooperative Inspection Program")
text_field("office_location", left + 400, y - row_h + 5, right - (left + 400) - 4, value="Alamo, Texas")
y -= row_h

# Row: "I request leave or overtime as specified below" + checkbox grid
grid_h = 145
box(left, y - grid_h, right - left, grid_h)
label(left + 4, y - 14, "I request leave or overtime as specified below:")

col1_x, col2_x, col3_x = left + 12, left + 210, left + 400
row1_y = y - 42
row2_y = y - 74
row3_y = y - 106

checkbox("leave_annual", col1_x, row1_y - 3)
label(col1_x + 16, row1_y, "Annual leave")
checkbox("leave_emergency", col2_x, row1_y - 3)
label(col2_x + 16, row1_y, "Emergency leave")
checkbox("leave_lwop", col3_x, row1_y - 3)
label(col3_x + 16, row1_y, "Leave without pay", size=9)
label(col3_x + 16, row1_y - 10, "(approval attached)", size=7.5)

checkbox("leave_sick", col1_x, row2_y - 3)
label(col1_x + 16, row2_y, "* Sick leave")
checkbox("leave_military", col2_x, row2_y - 3)
label(col2_x + 16, row2_y, "Military leave", size=10)
label(col2_x + 16, row2_y - 10, "(attach orders)", size=7.5)
checkbox("leave_extended_sick", col3_x, row2_y - 3)
label(col3_x + 16, row2_y, "Extended sick leave", size=8.5)
label(col3_x + 16, row2_y - 10, "(Drs letter attached)", size=7.5)

checkbox("leave_jury", col1_x, row3_y - 3)
label(col1_x + 16, row3_y, "Jury Duty", size=10)
label(col1_x + 16, row3_y - 10, "(attach summons)", size=7.5)
checkbox("leave_other", col2_x, row3_y - 3)
label(col2_x + 16, row3_y, "Other")
text_field("leave_other_specify", col2_x + 46, row3_y - 4, 95, h=12, font_size=8)
checkbox("leave_holiday", col3_x, row3_y - 3)
label(col3_x + 16, row3_y, "Holiday leave taken", size=9)
label(col3_x + 16, row3_y - 10, "(Regional office use only)", size=7)

label(col2_x, row3_y - 26, 'Must specify type when requesting "Other"', size=7.5)

y -= grid_h

# Row: sick leave note
note_h = 55
box(left, y - note_h, right - left, note_h)
c.setFont("Times-Bold", 9)
note_lines = [
    "*If you are absent more than three days due to illness, attach a doctor's certificate stating you",
    "were under the care of a physician, OR attach a written statement concerning the facts of your",
    "illness.  (A Doctor's bill is NOT acceptable.)",
]
ny = y - 14
for line in note_lines:
    c.drawString(left + 6, ny, line)
    ny -= 13
y -= note_h

# Row: hours / from / to
hrow_h = 34
box(left, y - hrow_h, right - left, hrow_h)
label(left + 4, y - 14, "No. of hours:")
text_field("total_hours", left + 4, y - 30, 90, h=13)

label(left + 105, y - 14, "From (Time):")
text_field("from_time", left + 105, y - 30, 90, h=13)
label(left + 210, y - 14, "Date:")
text_field("from_date", left + 210, y - 30, 100, h=13)

label(left + 340, y - 14, "To (Time):")
text_field("to_time", left + 340, y - 30, 90, h=13)
label(left + 445, y - 14, "Date:")
text_field("to_date", left + 445, y - 30, right - (left + 445) - 4, h=13)
y -= hrow_h

# Row: comments
crow_h = 40
box(left, y - crow_h, right - left, crow_h)
label(left + 4, y - 14, "Comments (optional).  Use for giving additional information:")
text_field("comments", left + 4, y - crow_h + 6, right - left - 8, h=14, font_size=8)
y -= crow_h

y -= 14  # gap between tables

# Emergency contact block
ec_h = 55
box(left, y - ec_h, right - left, ec_h)
label(left + 4, y - 14, "For emergency purposes I may be contacted at the following location:")
hline(left, left + (right - left) * 0.55, y - 20)
vline(left + (right - left) * 0.55, y - ec_h, y - 20)
label(left + 4, y - 33, "Address")
text_field("contact_address", left + 4, y - ec_h + 6, (right - left) * 0.55 - 10, h=14, font_size=9)
label(left + (right - left) * 0.55 + 6, y - 33, "Telephone (area code and number)")
text_field("contact_phone", left + (right - left) * 0.55 + 6, y - ec_h + 6, right - (left + (right - left) * 0.55 + 6) - 4, h=14, font_size=9)
y -= ec_h + 14

# Employee signature block
sig_h = 60
box(left, y - sig_h, right - left, sig_h)
label(left + 4, y - 14, "Employee's signature", bold=True)
text_field("employee_signature", left + 4, y - 34, right - left - 8, h=16, font_size=11)
c.setFont("Times-Roman", 8)
c.drawCentredString(W / 2, y - 42, "I hereby certify that the above information is true and correct.")
checkbox("supporting_docs_attached", left + 8, y - 55)
label(left + 24, y - 53, "Check here if supporting documents are attached (Doctor's certificate, PAF, military records, jury summons, etc.)", size=8)
y -= sig_h + 12

# Approvals block
appr_h = 55
box(left, y - appr_h, right - left, appr_h)
label(left + 4, y - 14, "Approvals", bold=True, size=12)
hline(left, right, y - 22)

checkbox("supervisor_approved", left + 20, y - 36)
label(left + 36, y - 34, "APPROVED", size=10)
checkbox("supervisor_disapproved", left + 130, y - 36)
label(left + 146, y - 34, "DISAPPROVED", size=10)
label(left + 250, y - 34, "Supervisor's signature", size=10)
text_field("supervisor_signature", left + 400, y - 37, right - (left + 400) - 4, h=14, font_size=9)

checkbox("director_approved", left + 20, y - 50)
label(left + 36, y - 48, "APPROVED", size=10)
checkbox("director_disapproved", left + 130, y - 50)
label(left + 146, y - 48, "DISAPPROVED", size=10)
label(left + 250, y - 48, "Director's signature", size=10)
text_field("director_signature", left + 400, y - 51, right - (left + 400) - 4, h=14, font_size=9)

c.showPage()
c.save()
print(f"Wrote {OUT}")
