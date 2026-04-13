import os
import json

from jinja2 import Template
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook
from lxml import etree


# =========================
# HTML TEMPLATE
# =========================
HTML_TEMPLATE = """
<html>
<head>
    <title>Industrial Catalog</title>
</head>
<body>
    <h1>INDUSTRIE IA - CATALOGUE</h1>

    <h2>Product</h2>
    <pre>{{ extracted_data }}</pre>

    <h2>Suppliers</h2>
    <ul>
    {% for s in suppliers %}
        <li>{{ s.name }} - {{ s.country }}</li>
    {% endfor %}
    </ul>

    <h2>TCO</h2>
    <pre>{{ tco }}</pre>

    <h2>Business Plan</h2>
    <pre>{{ business_plan }}</pre>

    <h2>AI Monitoring</h2>
    <pre>{{ ml_features }}</pre>
</body>
</html>
"""


# =========================
# 1. JSON EXPORT
# =========================
def export_json(data, output="output/catalog.json"):
    os.makedirs(os.path.dirname(output), exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return output


# =========================
# 2. HTML EXPORT
# =========================
def export_html(data, output="output/catalog.html"):
    os.makedirs(os.path.dirname(output), exist_ok=True)

    template = Template(HTML_TEMPLATE)
    html_content = template.render(**data)

    with open(output, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output, html_content


# =========================
# 3. PDF EXPORT (REPORTLAB FIXED)
# =========================
def export_pdf(data, output="output/catalog.pdf"):
    os.makedirs(os.path.dirname(output), exist_ok=True)

    doc = SimpleDocTemplate(output)
    styles = getSampleStyleSheet()

    story = []

    # Title
    story.append(Paragraph("INDUSTRIE IA - CATALOGUE", styles["Title"]))
    story.append(Spacer(1, 12))

    # Product
    story.append(Paragraph("Product", styles["Heading2"]))
    story.append(Paragraph(str(data.get("extracted_data", {})), styles["BodyText"]))
    story.append(Spacer(1, 12))

    # Suppliers
    story.append(Paragraph("Suppliers", styles["Heading2"]))
    for s in data.get("suppliers", []):
        line = f"{s.get('name', '')} - {s.get('country', '')}"
        story.append(Paragraph(line, styles["BodyText"]))

    story.append(Spacer(1, 12))

    # TCO
    story.append(Paragraph("TCO", styles["Heading2"]))
    story.append(Paragraph(str(data.get("tco", {})), styles["BodyText"]))
    story.append(Spacer(1, 12))

    # Business Plan
    story.append(Paragraph("Business Plan", styles["Heading2"]))
    story.append(Paragraph(str(data.get("business_plan", {})), styles["BodyText"]))
    story.append(Spacer(1, 12))

    # ML Features
    story.append(Paragraph("AI Monitoring", styles["Heading2"]))
    story.append(Paragraph(str(data.get("ml_features", {})), styles["BodyText"]))

    doc.build(story)

    return output


# =========================
# 4. EXCEL EXPORT
# =========================
def export_excel(data, output="output/catalog.xlsx"):
    os.makedirs(os.path.dirname(output), exist_ok=True)

    wb = Workbook()

    # Suppliers sheet
    ws1 = wb.active
    ws1.title = "Suppliers"
    ws1.append(["Name", "Country"])

    for s in data.get("suppliers", []):
        ws1.append([
            s.get("name", ""),
            s.get("country", "")
        ])

    # TCO sheet
    ws2 = wb.create_sheet("TCO")
    for k, v in data.get("tco", {}).items():
        ws2.append([k, str(v)])

    # Business plan sheet
    ws3 = wb.create_sheet("BusinessPlan")
    for k, v in data.get("business_plan", {}).items():
        ws3.append([k, str(v)])

    wb.save(output)
    return output


# =========================
# 5. XML EXPORT
# =========================
def export_xml(data, output="output/catalog.xml"):
    os.makedirs(os.path.dirname(output), exist_ok=True)

    root = etree.Element("catalog")

    product = etree.SubElement(root, "product")
    product.text = str(data.get("extracted_data", {}))

    suppliers_node = etree.SubElement(root, "suppliers")

    for s in data.get("suppliers", []):
        sup = etree.SubElement(suppliers_node, "supplier")
        sup.text = f"{s.get('name', '')} - {s.get('country', '')}"

    tco_node = etree.SubElement(root, "tco")
    tco_node.text = str(data.get("tco", {}))

    business_node = etree.SubElement(root, "business_plan")
    business_node.text = str(data.get("business_plan", {}))

    tree = etree.ElementTree(root)
    tree.write(output, pretty_print=True, xml_declaration=True, encoding="utf-8")

    return output


# =========================
# 6. MASTER EXPORT FUNCTION
# =========================
def export_all(data):
    os.makedirs("output", exist_ok=True)

    return {
        "json": export_json(data),
        "html": export_html(data)[0],
        "pdf": export_pdf(data),
        "excel": export_excel(data),
        "xml": export_xml(data),
    }