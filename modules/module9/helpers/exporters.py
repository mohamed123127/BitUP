import os
import json

from jinja2 import Template
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook
from lxml import etree


# =========================
# HTML TEMPLATE (Modernized)
# =========================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>BitUP Industrial Catalog</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1000px; margin: 0 auto; padding: 20px; background: #f4f6f9; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
        h1 { color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #2980b9; border-left: 5px solid #3498db; padding-left: 10px; margin-top: 30px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #3498db; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .kpi-box { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px; }
        .kpi { background: #e8f4fd; padding: 15px; border-radius: 8px; flex: 1; min-width: 150px; text-align: center; border: 1px solid #d1e9f9; }
        .kpi b { display: block; font-size: 1.2em; color: #2c3e50; }
        .swot-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .swot-item { padding: 15px; border-radius: 8px; }
        .strengths { background: #e8f5e9; } .weaknesses { background: #ffebee; }
        .opportunities { background: #e3f2fd; } .threats { background: #fff3e0; }
    </style>
</head>
<body>
    <div class="card">
        <h1>BITUP - CATALOGUE INDUSTRIEL</h1>
        <p>Généré pour : <strong>{{ product_name or "Produit Industriel" }}</strong></p>
    </div>

    <div class="card">
        <h2>🛠️ Spécifications techniques</h2>
        <table>
            {% for k, v in specs.items() %}
            <tr><th>{{ k }}</th><td>{{ v }}</td></tr>
            {% endfor %}
        </table>
    </div>

    <div class="card">
        <h2>💰 Analyse TCO (10 ans)</h2>
        <div class="kpi-box">
            <div class="kpi">Coût Initial<b>{{ tco.initial_cost|default(0)|round(2) }} USD</b></div>
            <div class="kpi">Coût Total<b>{{ tco.total_10y|default(0)|round(2) }} USD</b></div>
        </div>
        <h3>Détails annuels :</h3>
        <table>
            <tr><th>Année</th><th>Coût (USD)</th></tr>
            {% for cost in tco.yearly_costs %}
            <tr><td>Year {{ loop.index }}</td><td>{{ cost|round(2) }}</td></tr>
            {% endfor %}
        </table>
    </div>

    <div class="card">
        <h2>📈 Business Plan & ROI</h2>
        <div class="kpi-box">
            <div class="kpi">Profit Total<b>{{ business_plan.profit|default(0)|round(2) }} USD</b></div>
            <div class="kpi">ROI<b>{{ (business_plan.roi|default(0)*100)|round(2) }}%</b></div>
            <div class="kpi">NPV<b>{{ business_plan.npv|default(0)|round(2) }} USD</b></div>
            <div class="kpi">Break-even<b>An {{ business_plan.break_even_year or "N/A" }}</b></div>
        </div>

        <h3>Analyse SWOT (IA Generated)</h3>
        <div class="swot-grid">
            <div class="swot-item strengths"><strong>Forces</strong><ul>{% for item in business_plan.swot.Strengths %}<li>{{ item }}</li>{% endfor %}</ul></div>
            <div class="swot-item weaknesses"><strong>Faiblesses</strong><ul>{% for item in business_plan.swot.Weaknesses %}<li>{{ item }}</li>{% endfor %}</ul></div>
            <div class="swot-item opportunities"><strong>Opportunités</strong><ul>{% for item in business_plan.swot.Opportunities %}<li>{{ item }}</li>{% endfor %}</ul></div>
            <div class="swot-item threats"><strong>Menaces</strong><ul>{% for item in business_plan.swot.Threats %}<li>{{ item }}</li>{% endfor %}</ul></div>
        </div>
    </div>

    <div class="card">
        <h2>🤖 Digital Twin & ML</h2>
        <table>
            <tr><th>Accuracy</th><td>{{ (ml_features.accuracy|default(0)*100)|round(2) }}%</td></tr>
            <tr><th>Model Type</th><td>{{ ml_features.model_type }}</td></tr>
            <tr><th>Sensors</th><td>{{ ml_features.sensors_used|join(', ') }}</td></tr>
        </table>
    </div>
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
    # Inject flat keys for template
    render_data = {
        **data,
        "product_name": data.get("extracted_data", {}).get("product_name", ""),
        "specs": data.get("extracted_data", {}).get("specs", {}),
    }
    html_content = template.render(**render_data)
    with open(output, "w", encoding="utf-8") as f:
        f.write(html_content)
    return output, html_content

# =========================
# 3. PDF EXPORT (Enhanced with Tables)
# =========================
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

def export_pdf(data, output="output/catalog.pdf"):
    os.makedirs(os.path.dirname(output), exist_ok=True)
    doc = SimpleDocTemplate(output)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("BITUP - RAPPORT INDUSTRIEL", styles["Title"]))
    story.append(Spacer(1, 20))

    # Financial Summary Table
    story.append(Paragraph("Résumé Financier", styles["Heading2"]))
    tco = data.get("tco", {})
    bp = data.get("business_plan", {})
    fin_data = [
        ["Indicateur", "Valeur"],
        ["Investissement Initial", f"{tco.get('initial_cost', 0):,.2f} USD"],
        ["Coût Total (10 ans)", f"{tco.get('total_10y', 0):,.2f} USD"],
        ["Profit Prévu", f"{bp.get('profit', 0):,.2f} USD"],
        ["ROI estimé", f"{bp.get('roi', 0)*100:.2f}%"]
    ]
    t = Table(fin_data, colWidths=[200, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.navy),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    # SWOT Table
    story.append(Paragraph("Analyse Stratégique (SWOT)", styles["Heading2"]))
    swot = bp.get("swot", {})
    swot_data = [
        ["Forces", "Faiblesses"],
        ["\n".join(swot.get("Strengths", [])), "\n".join(swot.get("Weaknesses", []))],
        ["Opportunités", "Menaces"],
        ["\n".join(swot.get("Opportunities", [])), "\n".join(swot.get("Threats", []))]
    ]
    sw_t = Table(swot_data, colWidths=[220, 220])
    sw_t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (1,0), colors.whitesmoke),
        ('BACKGROUND', (0,2), (1,2), colors.whitesmoke),
        ('FONTSIZE', (0,0), (-1,-1), 8),
    ]))
    story.append(sw_t)

    doc.build(story)
    return output

# =========================
# 4. EXCEL EXPORT (Refined)
# =========================
def export_excel(data, output="output/catalog.xlsx"):
    os.makedirs(os.path.dirname(output), exist_ok=True)
    wb = Workbook()
    
    # Financial KPI Sheet
    ws = wb.active
    ws.title = "Summary"
    ws.append(["Category", "Metric", "Value"])
    tco = data.get("tco", {})
    bp = data.get("business_plan", {})
    ws.append(["TCO", "Initial Cost", tco.get("initial_cost")])
    ws.append(["TCO", "Total 10y", tco.get("total_10y")])
    ws.append(["Business Plan", "Profit", bp.get("profit")])
    ws.append(["Business Plan", "ROI", bp.get("roi")])
    ws.append(["Business Plan", "NPV", bp.get("npv")])

    # Yearly Costs
    ws2 = wb.create_sheet("Yearly Projections")
    ws2.append(["Year", "TCO Cost", "BP Revenue", "BP Profit"])
    yearly_costs = tco.get("yearly_costs", [])
    bp_proj = bp.get("projections", [])
    for i in range(len(yearly_costs)):
        rev = bp_proj[i].get("revenue") if i < len(bp_proj) else 0
        profit = bp_proj[i].get("profit") if i < len(bp_proj) else 0
        ws2.append([i+1, yearly_costs[i], rev, profit])

    wb.save(output)
    return output

# =========================
# 5. XML EXPORT (Structured)
# =========================
def export_xml(data, output="output/catalog.xml"):
    os.makedirs(os.path.dirname(output), exist_ok=True)
    root = etree.Element("catalog")
    
    financials = etree.SubElement(root, "financials")
    tco_node = etree.SubElement(financials, "tco")
    for k, v in data.get("tco", {}).items():
        if isinstance(v, list):
            node = etree.SubElement(tco_node, k)
            for item in v:
                etree.SubElement(node, "value").text = str(item)
        else:
            etree.SubElement(tco_node, k).text = str(v)
            
    bp_node = etree.SubElement(financials, "business_plan")
    for k, v in data.get("business_plan", {}).items():
        if k != "projections" and k != "swot":
            etree.SubElement(bp_node, k).text = str(v)

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