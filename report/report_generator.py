from pathlib import Path
from datetime import datetime
import sys

from reportlab.lib import colors
from reportlab.lib import styles
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)

# Allow importing the existing database module when this file is run directly.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.sqlite import get_logs_by_date


REPORT_DIR = PROJECT_ROOT / "reports"
CHECKINS_DIR = PROJECT_ROOT / "checkins"

PAGE_SIZE = landscape(A4)


def classify_logs(logs):
    """Split logs according to the existing admin_result field."""
    approved = []
    rejected = []
    pending = []

    for log in logs:
        status = log["admin_result"]

        if status == "APPROVED":
            approved.append(log)
        elif status == "REJECTED":
            rejected.append(log)
        else:
            pending.append(log)

    return approved, rejected, pending


def calculate_summary(logs):
    """Calculate daily statistics from the current log records."""
    total = len(logs)
    approved = sum(1 for log in logs if log["admin_result"] == "APPROVED")
    rejected = sum(1 for log in logs if log["admin_result"] == "REJECTED")
    pending = sum(1 for log in logs if log["admin_result"] == "PENDING")

    similarities = [
        float(log["similarity"])
        for log in logs
        if log["similarity"] is not None
        and log["similarity"] > 0
    ]

    average_similarity = (
        sum(similarities) / len(similarities)
        if similarities
        else 0.0
    )

    processed = approved + rejected
    processing_rate = (processed / total * 100) if total else 0.0
    approval_rate = (approved / processed * 100) if processed else 0.0

    return {
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "pending": pending,
        "average_similarity": average_similarity,
        "processing_rate": processing_rate,
        "approval_rate": approval_rate,
    }


def make_image(image_path, max_width=30 * mm, max_height=30 * mm):
    """Create a larger thumbnail while preserving the original aspect ratio."""
    if not image_path:
        return Paragraph("-", get_styles()["cell"])

    path = Path(image_path)

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    if not path.exists():
        return Paragraph("No image", get_styles()["small"])

    try:
        from PIL import Image as PILImage

        with PILImage.open(path) as img:
            img_width, img_height = img.size

        if img_width <= 0 or img_height <= 0:
            return Paragraph("No image", get_styles()["small"])

        ratio = min(
            max_width / img_width,
            max_height / img_height
        )

        width = img_width * ratio
        height = img_height * ratio

        return Image(
            str(path),
            width=width,
            height=height
        )

    except Exception:
        return Paragraph("No image", get_styles()["small"])

_STYLES = None

def get_styles():
    global _STYLES

    if _STYLES is not None:
        return _STYLES

    styles = getSampleStyleSheet()

    _STYLES = {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=21,
            alignment=TA_CENTER,
            spaceAfter=3 * mm,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#555555"),
            spaceAfter=5 * mm,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            spaceBefore=3 * mm,
            spaceAfter=2 * mm,
        ),
        "cell": ParagraphStyle(
            "Cell",
            parent=styles["Normal"],
            fontSize=7.5,
            leading=9,
            alignment=TA_LEFT,
        ),
        "cell_center": ParagraphStyle(
            "CellCenter",
            parent=styles["Normal"],
            fontSize=7.5,
            leading=9,
            alignment=TA_CENTER,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=styles["Normal"],
            fontSize=6.5,
            leading=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#777777"),
        ),
        "summary": ParagraphStyle(
            "Summary",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
        ),
    }

    return _STYLES


def conclusion_for(log):
    status = log["admin_result"]
    similarity = float(log["similarity"] or 0)

    if status == "APPROVED":
        return f"Identity verified ({similarity * 100:.1f}%)."

    if status == "REJECTED":
        return f"Identity verification failed ({similarity * 100:.1f}%)."

    return "Awaiting verification."


def build_log_table(logs, section_title):
    styles = get_styles()

    header = [
        Paragraph("Image", styles["cell_center"]),
        Paragraph("Employee", styles["cell_center"]),
        Paragraph("RFID", styles["cell_center"]),
        Paragraph("Time", styles["cell_center"]),
        Paragraph("AI Score", styles["cell_center"]),
        Paragraph("Attempts", styles["cell_center"]),
        Paragraph("Result", styles["cell_center"]),
        Paragraph("Conclusion", styles["cell_center"]),
]

    rows = [header]

    for log in logs:
        similarity = float(log["similarity"] or 0)
        score_text = f"{similarity * 100:.1f}%"

        time_value = log["time"]
        if hasattr(time_value, "strftime"):
            time_text = time_value.strftime("%H:%M:%S")
        else:
            time_text = str(time_value)[11:19] or str(time_value)

        status = log["admin_result"]

        if status == "APPROVED":
            result_text = "APPROVED"
        elif status == "REJECTED":
            result_text = "REJECTED"
        else:
            result_text = "PENDING"

        rows.append([
            make_image(log["image_path"]),
            Paragraph(str(log["name"] or "-"), styles["cell"]),
            Paragraph(str(log["uid"] or "-"), styles["cell"]),
            Paragraph(time_text, styles["cell_center"]),
            Paragraph(score_text, styles["cell_center"]),
            Paragraph(
                f"{log['attempt_count'] or 1}/3",
                styles["cell_center"],
            ),
            Paragraph(result_text, styles["cell_center"]),
            Paragraph(conclusion_for(log), styles["cell"]),
        ])

    if len(rows) == 1:
        rows.append([
            Paragraph("No data available", styles["cell_center"]),
            "", "", "", "", "", "", ""
        ])

    table = Table(
        rows,
        colWidths=[
            34 * mm,
            32 * mm,
            24 * mm,
            22 * mm,
            20 * mm,
            18 * mm,
            27 * mm,
            45 * mm,
        ],
        repeatRows=1,
        hAlign="LEFT",
    )

    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9EEF5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17202A")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B8C0CC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]

    if section_title == "APPROVED":
        result_bg = colors.HexColor("#E8F5E9")
    elif section_title == "REJECTED":
        result_bg = colors.HexColor("#FDECEC")
    else:
        result_bg = colors.HexColor("#FFF8E1")

    table_style.extend([
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("BACKGROUND", (6, 1), (6, -1), result_bg),
    ])

    table.setStyle(TableStyle(table_style))

    return table


def build_summary(summary):
    styles = get_styles()

    data = [
    [
        Paragraph("<b>Total Check-ins</b>", styles["summary"]),
        Paragraph(f"<b>{summary['total']}</b>", styles["summary"]),
        Paragraph("<b>Approved</b>", styles["summary"]),
        Paragraph(f"<b>{summary['approved']}</b>", styles["summary"]),
        Paragraph("<b>Rejected</b>", styles["summary"]),
        Paragraph(f"<b>{summary['rejected']}</b>", styles["summary"]),
        Paragraph("<b>Pending</b>", styles["summary"]),
        Paragraph(f"<b>{summary['pending']}</b>", styles["summary"]),
    ],
    [
        Paragraph("Average AI Similarity", styles["summary"]),
        Paragraph(
            f"{summary['average_similarity'] * 100:.1f}%",
            styles["summary"],
        ),
        Paragraph("AI Processing Rate", styles["summary"]),
        Paragraph(
            f"{summary['processing_rate']:.1f}%",
            styles["summary"],
        ),
        Paragraph("Approval Rate", styles["summary"]),
        Paragraph(
            f"{summary['approval_rate']:.1f}%",
            styles["summary"],
        ),
        "",
        "",
    ],
]

    table = Table(
        data,
        colWidths=[
            31 * mm, 18 * mm,
            20 * mm, 15 * mm,
            25 * mm, 18 * mm,
            25 * mm, 18 * mm,
        ],
        hAlign="LEFT",
    )

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C0CC")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F9FB")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    return table


def build_conclusion(summary):
    styles = get_styles()

    if summary["total"] == 0:
        text = (
            "No check-in records found for the reporting day. "
            "No AI data available for evaluation."
        )
    else:
        text = (
            f"On the reporting day, the system recorded {summary['total']} check-ins. "
            f"There were {summary['approved']} approved cases, "
            f"{summary['rejected']} rejected cases, and "
            f"{summary['pending']} pending cases. "
            f"The AI processing rate was {summary['processing_rate']:.1f}%, "
            f"with an average similarity of "
            f"{summary['average_similarity'] * 100:.1f}%. "
            "Pending cases were separated and not included in the rejected category."
        )

    table = Table(
        [[Paragraph(f"<b>Conclusion:</b> {text}", styles["summary"])]],
        colWidths=[170 * mm],
    )

    table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C0CC")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F9FB")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    return table


def generate_daily_report(date=None):
    """Generate one daily PDF with one page/section for each status."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    logs = get_logs_by_date(date)

    approved, rejected, pending = classify_logs(logs)
    summary = calculate_summary(logs)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = REPORT_DIR / f"daily_report_{date}.pdf"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=PAGE_SIZE,
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=9 * mm,
        bottomMargin=9 * mm,
        title=f"SIC IoT Daily Access Report - {date}",
        author="SIC IoT Smart Access Control",
    )

    styles = get_styles()
    story = []

    # ============================================================
    # PAGE 1 — APPROVED
    # ============================================================

    story.append(
        Paragraph(
            "SIC IoT SMART ACCESS CONTROL",
            styles["title"],
        )
    )

    story.append(
        Paragraph(
            f"DAILY ACCESS REPORT — {date}",
            styles["subtitle"],
        )
    )

    # Daily summary only appears on the first page
    story.append(
        Paragraph(
            "DAILY SUMMARY",
            styles["section"],
        )
    )

    story.append(build_summary(summary))

    story.append(Spacer(1, 5 * mm))

    story.append(
        Paragraph(
            "APPROVED",
            styles["section"],
        )
    )

    story.append(
        build_log_table(
            approved,
            "APPROVED"
        )
    )

    # ============================================================
    # PAGE 2 — REJECTED
    # ============================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "SIC IoT SMART ACCESS CONTROL",
            styles["title"],
        )
    )

    story.append(
        Paragraph(
            f"DAILY ACCESS REPORT — {date}",
            styles["subtitle"],
        )
    )

    story.append(
        Paragraph(
            "REJECTED",
            styles["section"],
        )
    )

    story.append(
        build_log_table(
            rejected,
            "REJECTED"
        )
    )

    # ============================================================
    # PAGE 3 — PENDING
    # ============================================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "SIC IoT SMART ACCESS CONTROL",
            styles["title"],
        )
    )

    story.append(
        Paragraph(
            f"DAILY ACCESS REPORT — {date}",
            styles["subtitle"],
        )
    )

    story.append(
        Paragraph(
            "PENDING",
            styles["section"],
        )
    )

    story.append(
        build_log_table(
            pending,
            "PENDING"
        )
    )

    story.append(Spacer(1, 6 * mm))

    story.append(
        Paragraph(
            "CONCLUSION",
            styles["section"],
        )
    )

    story.append(
        build_conclusion(summary)
    )

    # Generate PDF
    doc.build(story)

    return output_path


if __name__ == "__main__":
    report_date = (
        sys.argv[1]
        if len(sys.argv) > 1
        else datetime.now().strftime("%Y-%m-%d")
    )

    path = generate_daily_report(report_date)
    print(f"Report generated: {path}")