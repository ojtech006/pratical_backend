import os
import uuid
import random
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import F
from django.http import FileResponse
from django.utils import timezone
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from .models import PracticalReport, PaymentOrder, DailyDownload

SUBSCRIPTION_PLANS = {
    "FOUR_DOCS": {"amount": 450, "documents": 4, "label": "4 Documents"},
}


DOCUMENT_DESIGNS = {
"CLASSIC_BLUE":{"name":"Classic Blue","navy":"17365D","teal":"168C8C","light":"F3F7FA","mid":"D6E2EA","ink":"243447","muted":"637487","strap":""},
"MODERN_TEAL":{"name":"Modern Teal","navy":"124B50","teal":"20A39E","light":"F2FAF9","mid":"C9E6E2","ink":"203B3B","muted":"607B78","strap":"LEARNING • PRACTICE • PROGRESS"},
"BURGUNDY_EDITORIAL":{"name":"Burgundy Editorial","navy":"54243A","teal":"B56B52","light":"FBF6F7","mid":"E8D5DC","ink":"392C32","muted":"806D75","strap":"ACADEMIC WORKBOOK"},
"CHARCOAL_GOLD":{"name":"Charcoal & Gold","navy":"252B33","teal":"B68A3A","light":"FAF8F2","mid":"E6DDC9","ink":"30343A","muted":"77736A","strap":"STUDENT ACADEMIC PORTFOLIO"},
}
def choose_document_design():
    key = random.SystemRandom().choice(tuple(DOCUMENT_DESIGNS))
    return key, DOCUMENT_DESIGNS[key]

def clean(data, key, default="", limit=None):
    value = str(data.get(key, default) or "").strip()
    return value[:limit] if limit else value


# PracticalDesk document design system
NAVY = "17365D"
BLUE = "1F4E79"
TEAL = "168C8C"
PALE = "EAF2F8"
LIGHT = "F3F7FA"
MID = "D6E2EA"
INK = "243447"
MUTED = "637487"
WHITE = "FFFFFF"


def _shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def _set_cell_border(cell, **kwargs):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        if edge in kwargs:
            tag = "w:" + edge
            element = borders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                borders.append(element)
            for key, value in kwargs[edge].items():
                element.set(qn("w:" + key), str(value))


def _set_cell_margins(cell, top=100, start=140, bottom=100, end=140):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, v in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn("w:" + m))
        if node is None:
            node = OxmlElement("w:" + m)
            tc_mar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def _set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def _add_page_field(paragraph):
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr)
    run._r.append(fld_char2)


def _add_rule(paragraph, color=TEAL, size="18"):
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), size)
    bottom.set(qn("w:space"), "5")
    bottom.set(qn("w:color"), color)
    p_bdr.append(bottom)
    p_pr.append(p_bdr)


def setup_doc(document_label="PRACTICAL REPORT", design=None):
    design = design or DOCUMENT_DESIGNS["CLASSIC_BLUE"]
    navy, teal, mid, ink, muted = (design[k] for k in ("navy","teal","mid","ink","muted"))
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(.72)
    sec.bottom_margin = Inches(.72)
    sec.left_margin = Inches(.82)
    sec.right_margin = Inches(.82)
    sec.header_distance = Inches(.32)
    sec.footer_distance = Inches(.35)

    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor.from_string(ink)
    normal.paragraph_format.space_after = Pt(7)
    normal.paragraph_format.line_spacing = 1.15

    for style_name, size, color in (
        ("Title", 25, navy), ("Heading 1", 15, navy), ("Heading 2", 12, teal)
    ):
        style = doc.styles[style_name]
        style.font.name = "Aptos Display" if style_name == "Title" else "Aptos"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.space_before = Pt(12 if style_name != "Title" else 0)
        style.paragraph_format.space_after = Pt(6)

    header = sec.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    header.paragraph_format.space_after = Pt(2)
    run = header.add_run("PRACTICAL")
    run.bold = True
    run.font.name = "Aptos"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor.from_string(navy)
    run = header.add_run("DESK")
    run.bold = True
    run.font.name = "Aptos"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor.from_string(teal)
    run = header.add_run("   /   " + document_label.upper())
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor.from_string(muted)
    _add_rule(header, mid, "6")

    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.paragraph_format.space_before = Pt(4)
    fr = footer.add_run("PRACTICALDESK  •  STUDENT COPY     |     PAGE ")
    fr.font.name = "Aptos"
    fr.font.size = Pt(8)
    fr.font.color.rgb = RGBColor.from_string(muted)
    _add_page_field(footer)
    return doc


def _add_cover_heading(doc, title, subtitle, data, design=None):
    design = design or DOCUMENT_DESIGNS["CLASSIC_BLUE"]
    navy, teal, light, mid, ink = (design[k] for k in ("navy","teal","light","mid","ink"))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(22)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(title.upper())
    r.bold = True
    r.font.name = "Aptos Display"
    r.font.size = Pt(24)
    r.font.color.rgb = RGBColor.from_string(navy)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(15)
    r = p.add_run(subtitle)
    r.font.name = "Aptos"
    r.font.size = Pt(11)
    r.font.color.rgb = RGBColor.from_string(teal)
    _add_rule(p, teal, "18")

    if design.get("strap"):
        strap = doc.add_paragraph()
        strap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sr = strap.add_run(design["strap"])
        sr.bold = True
        sr.font.size = Pt(8)
        sr.font.color.rgb = RGBColor.from_string(teal)
    # Compact, polished metadata panel
    table = doc.add_table(rows=0, cols=2)
    table.autofit = False
    table.columns[0].width = Inches(2.15)
    table.columns[1].width = Inches(4.65)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    details = [
        ("STUDENT NAME", data.get("student_name", "")),
        ("MATRIC NUMBER", data.get("matric_number", "")),
        ("DEPARTMENT", data.get("department", "")),
        ("COURSE", " — ".join(x for x in (data.get("course_code", ""), data.get("course_title", "")) if x)),
        ("LEVEL", data.get("level", "")),
        ("LECTURER", data.get("lecturer", "")),
    ]
    for index, (label, value) in enumerate(details):
        if not value:
            continue
        cells = table.add_row().cells
        cells[0].width = Inches(2.15)
        cells[1].width = Inches(4.65)
        _shade(cells[0], navy)
        _shade(cells[1], light if index % 2 == 0 else WHITE)
        for cell in cells:
            _set_cell_margins(cell)
            _set_cell_border(cell, bottom={"val": "single", "sz": "4", "color": mid})
        lp = cells[0].paragraphs[0]
        lp.paragraph_format.space_after = Pt(0)
        lr = lp.add_run(label)
        lr.bold = True
        lr.font.size = Pt(8)
        lr.font.color.rgb = RGBColor.from_string(WHITE)
        vp = cells[1].paragraphs[0]
        vp.paragraph_format.space_after = Pt(0)
        vr = vp.add_run(value)
        vr.font.size = Pt(9.5)
        vr.font.color.rgb = RGBColor.from_string(ink)

    doc.add_paragraph().paragraph_format.space_after = Pt(1)


def _add_section(doc, number, heading, content, design=None):
    design = design or DOCUMENT_DESIGNS["CLASSIC_BLUE"]
    navy, teal, mid = (design[k] for k in ("navy","teal","mid"))
    if not content or not str(content).strip():
        return
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(13)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(f"{number:02d}   ")
    r.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor.from_string(teal)
    r = p.add_run(heading.upper())
    r.bold = True
    r.font.name = "Aptos"
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor.from_string(navy)
    _add_rule(p, mid, "5")
    add_multiline(doc, content)


def add_multiline(doc, text):
    # Preserve paragraph breaks, but do not turn empty lines into large blank gaps.
    for line in (text or "").splitlines():
        cleaned = line.strip()
        if cleaned:
            p = doc.add_paragraph(cleaned)
            p.paragraph_format.widow_control = True


def add_student_details(doc, data):
    # Kept as a compatibility helper for any other generator callers.
    _add_cover_heading(doc, "PracticalDesk", data.get("practical_title", ""), data)


def build_summary_docx(data, design=None):
    """Create a polished learning summary; never includes the separate exercises."""
    design = design or DOCUMENT_DESIGNS["CLASSIC_BLUE"]
    doc = setup_doc("PRACTICAL CLASS SUMMARY", design)
    subtitle = " | ".join(x for x in (data.get("course_code", ""), data.get("practical_title", "")) if x)
    _add_cover_heading(doc, "Practical Class Summary", subtitle, data, design)
    sections = [
        ("Introduction", data.get("summary", "")),
        ("Practical Activities", data.get("c_exercises", "")),
        ("Important Concepts and Lessons Learnt", data.get("manual_topics", "")),
        ("Conclusion", data.get("conclusion", "")),
    ]
    for number, (heading, content) in enumerate(sections, start=1):
        _add_section(doc, number, heading, content, design)
    return doc



EXERCISE_TEMPLATES = {
    "CLASSIC_SAMPLE": {
        "name": "Classic Student Template",
        "description": "Student details panel, formal application letter, separate CV page, and numbered PC instructions.",
    },
    "SIMPLE_SAMPLE": {
        "name": "Simple COS 101 Template",
        "description": "Compact COS 101 heading, straightforward application letter and CV sections, and numbered saving/printing instructions.",
    },
}


def _add_template_heading(doc, text, design, centered=False, level=1):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if centered else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(12 if level == 1 else 8)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text.upper())
    r.bold = True
    r.font.name = "Aptos"
    r.font.size = Pt(15 if level == 1 else 11)
    r.font.color.rgb = RGBColor.from_string(design["navy"] if level == 1 else design["teal"])
    if not centered:
        _add_rule(p, design["mid"], "6")
    return p


def _add_template_body(doc, content):
    for line in (content or "").splitlines():
        line = line.strip()
        if not line:
            continue
        p = doc.add_paragraph()
        p.paragraph_format.widow_control = True
        p.paragraph_format.space_after = Pt(7)
        p.add_run(line)


def _add_template_steps(doc, content):
    lines = [line.strip() for line in (content or "").splitlines() if line.strip()]
    for line in lines:
        # Preserve supplied numbering when present; use a numbered list otherwise.
        p = doc.add_paragraph(style="List Number")
        p.paragraph_format.space_after = Pt(5)
        p.add_run(re.sub(r"^\s*\d+[\.\)]\s*", "", line))


def build_exercises_docx(data, design=None, template_key="CLASSIC_SAMPLE"):
    """Build one of the two COS 101 practical-exercise layouts using supplied student content."""
    design = design or DOCUMENT_DESIGNS["CLASSIC_BLUE"]
    template_key = template_key if template_key in EXERCISE_TEMPLATES else "CLASSIC_SAMPLE"
    doc = setup_doc("COS 101 PRACTICAL EXERCISE", design)

    if template_key == "CLASSIC_SAMPLE":
        _add_cover_heading(
            doc,
            "Practical Exercise",
            " | ".join(x for x in (data.get("course_code") or "COS 101", data.get("practical_title") or "Computer Studies") if x),
            data,
            design,
        )
        _add_template_heading(doc, "1. Application Letter", design)
        _add_template_body(doc, data.get("application_letter", ""))

        doc.add_page_break()
        _add_template_heading(doc, "2. Curriculum Vitae (CV)", design)
        _add_template_body(doc, data.get("cv_content", ""))

        doc.add_page_break()
        _add_template_heading(doc, "3. Steps for Saving the Documents on a PC", design)
        _add_template_steps(doc, data.get("saving_steps", ""))

        if data.get("extra_notes"):
            _add_template_heading(doc, "4. Additional Instructions", design)
            _add_template_body(doc, data["extra_notes"])
    else:
        # The second uploaded sample places course/matric/name details in a compact heading.
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(18)
        r = p.add_run("PRACTICAL EXERCISE")
        r.bold = True
        r.font.size = Pt(21)
        r.font.color.rgb = RGBColor.from_string(design["navy"])

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(14)
        meta = "   |   ".join(x for x in (
            f"Course: {data.get('course_code') or 'COS 101'}",
            f"MATRIC NUMBER: {data.get('matric_number', '')}",
            f"Name: {data.get('student_name', '')}",
        ) if x and not x.endswith(": "))
        rr = p.add_run(meta)
        rr.font.size = Pt(9)
        rr.font.color.rgb = RGBColor.from_string(design["muted"])
        _add_rule(p, design["teal"], "12")

        _add_template_heading(doc, "1. Application Letter", design)
        _add_template_body(doc, data.get("application_letter", ""))

        _add_template_heading(doc, "2. Curriculum Vitae (CV)", design)
        _add_template_body(doc, data.get("cv_content", ""))

        _add_template_heading(doc, "3. Steps for Saving the Documents on a PC", design)
        _add_template_steps(doc, data.get("saving_steps", ""))

        _add_template_heading(doc, "4. Renaming and Printing the Document", design)
        _add_template_body(doc, data.get("extra_notes", "") or (
            "Open File Explorer and locate the saved document. Rename it using your matric number, "
            "keep the .docx extension, review the document in Microsoft Word, then print and submit "
            "the hard copy as instructed by your lecturer."
        ))
    return doc

@api_view(["GET"])
def health(request):
    return Response({
        "ok": True,
        "service": "PracticalDesk",
        "plans": SUBSCRIPTION_PLANS,
        "currency": "NGN",
        "openai_enabled": False,
        "exercise_templates": [{"key": key, **value} for key, value in EXERCISE_TEMPLATES.items()],
    })


@api_view(["POST"])
def create_payment(request):
    """Create a pending ₦450 OPay payment request. No payment is assumed."""
    order = PaymentOrder.objects.create(
        reference=f"PDSK{uuid.uuid4().hex[:16].upper()}",
        plan="FOUR_DOCS", amount_kobo=45000, max_documents=4,
        provider="OPAY", status="PENDING",
    )
    return Response({
        "reference": order.reference, "plan": order.plan, "amount": 450,
        "currency": "NGN", "max_documents": 4, "documents_remaining": 4,
        "provider": "OPAY", "status": order.status, "mode": "MANUAL_TRANSFER",
        "account_name": getattr(settings, "PRACTICALDESK_OPAY_ACCOUNT_NAME", ""),
        "account_number": getattr(settings, "PRACTICALDESK_OPAY_ACCOUNT_NUMBER", ""),
        "bank_name": "OPay",
        "message": "Transfer ₦450 and upload your OPay receipt. Credits activate only after administrator verification.",
    }, status=201)


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_payment_receipt(request, reference):
    """
    Save the student's OPay receipt and automatically approve the order.

    IMPORTANT: This is receipt-upload-based approval, not bank-transfer
    verification. Only use it if you intentionally accept that risk.
    """
    receipt = request.FILES.get("receipt")

    if not receipt:
        return Response(
            {"error": "Please select your OPay receipt image."},
            status=400
        )

    if receipt.size <= 0:
        return Response(
            {"error": "The selected receipt file is empty."},
            status=400
        )

    if receipt.size > 2 * 1024 * 1024:
        return Response(
            {"error": "Receipt must not be larger than 2 MB."},
            status=400
        )

    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if getattr(receipt, "content_type", "") not in allowed_types:
        return Response(
            {"error": "Upload a JPG, PNG or WEBP receipt image."},
            status=400
        )

    try:
        with transaction.atomic():
            order = PaymentOrder.objects.select_for_update().get(
                reference=reference
            )

            if order.status == "APPROVED":
                used = order.reports.count()
                return Response({
                    "reference": order.reference,
                    "status": "APPROVED",
                    "max_documents": order.max_documents,
                    "documents_used": used,
                    "documents_remaining": max(
                        order.max_documents - used, 0
                    ),
                    "message": "This payment has already been approved."
                }, status=200)

            if order.status == "UNDER_REVIEW":
                return Response(
                    {"error": "A receipt has already been submitted for this payment."},
                    status=400
                )

            order.receipt = receipt
            order.status = "APPROVED"
            order.reviewed_at = timezone.now()
            order.admin_note = (
                "Automatically approved after OPay receipt upload. "
                "Bank transfer was not independently verified."
            )
            order.save(update_fields=[
                "receipt",
                "status",
                "reviewed_at",
                "admin_note"
            ])

            used = order.reports.count()
            remaining = max(order.max_documents - used, 0)

    except PaymentOrder.DoesNotExist:
        return Response(
            {"error": "Payment request not found."},
            status=404
        )

    return Response({
        "reference": order.reference,
        "status": "APPROVED",
        "max_documents": order.max_documents,
        "documents_used": used,
        "documents_remaining": remaining,
        "message": (
            "Receipt uploaded. Your four document credits are now active."
        )
    }, status=200)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def review_payment(request, reference):
    decision = clean(request.data, "decision").upper()
    if decision not in ("APPROVE", "REJECT"):
        return Response({"error": "decision must be APPROVE or REJECT."}, status=400)
    try:
        with transaction.atomic():
            order = PaymentOrder.objects.select_for_update().get(reference=reference)
            if order.status == "APPROVED":
                return Response({"reference": order.reference, "status": order.status,
                    "documents_remaining": max(order.max_documents - order.reports.count(), 0)})
            if order.status != "UNDER_REVIEW" or not order.receipt:
                return Response({"error": "A receipt must be submitted before review."}, status=400)
            order.status = "APPROVED" if decision == "APPROVE" else "REJECTED"
            order.admin_note = clean(request.data, "admin_note", limit=500)
            order.reviewed_at = timezone.now()
            order.save(update_fields=["status", "admin_note", "reviewed_at"])
    except PaymentOrder.DoesNotExist:
        return Response({"error": "Payment request not found."}, status=404)
    return Response({"reference": order.reference, "status": order.status,
        "documents_remaining": 4 if order.status == "APPROVED" else 0,
        "message": "Payment approved; four credits are active." if order.status == "APPROVED" else "Payment receipt rejected."})


@api_view(["GET"])
def payment_status(request, reference):
    try:
        order = PaymentOrder.objects.get(reference=reference)
    except PaymentOrder.DoesNotExist:
        return Response({"error": "Payment order not found."}, status=404)
    used = order.reports.count()
    return Response({
        "reference": order.reference, "plan": order.plan, "amount": order.amount_kobo / 100,
        "currency": order.currency, "provider": order.provider, "status": order.status,
        "max_documents": order.max_documents, "documents_used": used,
        "documents_remaining": max(order.max_documents - used, 0) if order.status == "APPROVED" else 0,
        "mode": "MANUAL_TRANSFER", "receipt_submitted": bool(order.receipt),
        "admin_note": order.admin_note,
    })


@api_view(["POST"])
def create_report(request):
    assignment = clean(request.data, "assignment_type", "SUMMARY").upper()
    if assignment not in ("SUMMARY", "EXERCISES"):
        return Response({"error": "assignment_type must be SUMMARY or EXERCISES."}, status=400)

    exercise_template = clean(request.data, "exercise_template", "CLASSIC_SAMPLE").upper()
    if exercise_template not in EXERCISE_TEMPLATES:
        return Response({
            "error": "Choose a valid exercise_template.",
            "available_templates": list(EXERCISE_TEMPLATES.keys()),
        }, status=400)

    required = ["student_name", "matric_number", "course_code", "practical_title", "payment_reference"]
    missing = [key for key in required if not clean(request.data, key)]
    if missing:
        return Response({"error": "Complete the required student/course details.", "missing": missing}, status=400)

    reference = clean(request.data, "payment_reference")
    data = {
        "assignment_type": assignment,
        "student_name": clean(request.data, "student_name", limit=160),
        "matric_number": clean(request.data, "matric_number", limit=80),
        "department": clean(request.data, "department", limit=120),
        "course_code": clean(request.data, "course_code", limit=30),
        "course_title": clean(request.data, "course_title", limit=160),
        "level": clean(request.data, "level", limit=40),
        "lecturer": clean(request.data, "lecturer", limit=160),
        "practical_title": clean(request.data, "practical_title", limit=200),
        "summary": clean(request.data, "summary"),
        "c_exercises": clean(request.data, "c_exercises"),
        "manual_topics": clean(request.data, "manual_topics"),
        "conclusion": clean(request.data, "conclusion"),
        "application_letter": clean(request.data, "application_letter"),
        "cv_content": clean(request.data, "cv_content"),
        "saving_steps": clean(request.data, "saving_steps"),
        "extra_notes": clean(request.data, "extra_notes"),
    }
    if assignment == "SUMMARY" and not any(data[key] for key in ("summary", "c_exercises", "manual_topics", "conclusion")):
        return Response({"error": "Enter summary or practical-class learning details."}, status=400)
    if assignment == "EXERCISES" and not all(data[key] for key in ("application_letter", "cv_content", "saving_steps")):
        return Response({"error": "Complete the application letter, CV and saving steps."}, status=400)

    # Lock the subscription while checking and consuming one generation credit.
    try:
        with transaction.atomic():
            order = PaymentOrder.objects.select_for_update().get(reference=reference)
            if order.status != "APPROVED":
                return Response({"error": "Payment is awaiting administrator verification."}, status=402)
            used = order.reports.count()
            if used >= order.max_documents:
                return Response({
                    "error": "Your subscription generation limit has been reached. Subscribe again to generate more documents.",
                    "max_documents": order.max_documents,
                    "documents_used": used,
                    "documents_remaining": 0,
                    "subscription_required": True,
                }, status=402)

            design_key, selected_design = choose_document_design()
            doc = build_summary_docx(data, selected_design) if assignment == "SUMMARY" else build_exercises_docx(data, selected_design, exercise_template)
            stream = BytesIO()
            doc.save(stream)
            stream.seek(0)
            safe_matric = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in data["matric_number"])
            filename = f"{safe_matric}_{assignment.title()}_{design_key}_{uuid.uuid4().hex[:6]}.docx"
            report = PracticalReport(
                payment_order=order,
                assignment_type=assignment,
                exercise_template=exercise_template if assignment == "EXERCISES" else "CLASSIC_SAMPLE",
                plan=order.plan,
                student_name=data["student_name"],
                matric_number=data["matric_number"],
                department=data["department"],
                course_code=data["course_code"],
                course_title=data["course_title"],
                level=data["level"],
                lecturer=data["lecturer"],
                practical_title=data["practical_title"],
                summary=data["summary"],
                c_exercises=data["c_exercises"],
                manual_topics=data["manual_topics"],
                conclusion=data["conclusion"],
                application_letter=data["application_letter"],
                cv_content=data["cv_content"],
                saving_steps=data["saving_steps"],
                extra_notes=data["extra_notes"],
                ai_generated=False,
            )
            report.file.save(filename, ContentFile(stream.getvalue()), save=False)
            report.save()
            used += 1
            remaining = max(order.max_documents - used, 0)
    except PaymentOrder.DoesNotExist:
        return Response({"error": "Payment reference was not found."}, status=404)

    return Response({
        "message": "Word document generated.",
        "report_id": str(report.id),
        "assignment_type": assignment,
        "exercise_template": exercise_template if assignment == "EXERCISES" else None,
        "plan": order.plan,
        "ai_generated": False,
        "download_url": f"/api/reports/{report.id}/download/",
        "filename": filename,
        "design": selected_design["name"],
        "design_key": design_key,
        "max_documents": order.max_documents,
        "documents_used": used,
        "documents_remaining": remaining,
        "subscription_exhausted": remaining == 0,
    }, status=201)

@api_view(["GET"])
def download_report(request, report_id):
    """Downloads of an already generated report do not consume subscription credits."""
    try:
        report = PracticalReport.objects.get(id=report_id)
    except PracticalReport.DoesNotExist:
        return Response({"error": "Report not found."}, status=404)
    if not report.file:
        return Response({"error": "Document file is missing."}, status=404)
    return FileResponse(report.file.open("rb"), as_attachment=True, filename=os.path.basename(report.file.name))


