import openpyxl
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import json
try:
    from .ai_generator import generate_ai_business_plan
except (ImportError, ValueError):
    from ai_generator import generate_ai_business_plan

def calculate_business_plan(state: dict) -> dict:
    product_name = state.get("product_name", "Produit Inconnu")
    tco_data = state.get("tco", {})

    if not tco_data:
        raise ValueError("Les données du TCO sont manquantes.")

    initial_cost = tco_data.get("initial_cost", 0.0)
    total_10y = tco_data.get("total_10y", 0.0)
    yearly_costs = tco_data.get("yearly_costs", [])

    # Financial Analysis (Purely Revenue & Profit based on TCO inputs)
    # We DO NOT calculate costs here; we consume them from state['tco'] 
    discount_rate = 0.10 
    
    # Revenue logic (Assumption: 1.5x TCO over 10 years)
    total_revenue_target = total_10y * 1.5 
    base_annual_revenue = total_revenue_target / 10
    
    projections = []
    total_actual_revenue = 0
    total_actual_profit = 0
    cumulative_profit = 0 
    npv = 0 
    break_even_year = None

    for i, cost in enumerate(yearly_costs):
        year = i + 1
        # Revenue grows slightly (5%) to outpace costs
        annual_revenue = base_annual_revenue * (1.05 ** i)
        yearly_profit = annual_revenue - cost
        
        # NPV Calculation
        discount_factor = 1 / ((1 + discount_rate) ** year)
        npv += yearly_profit * discount_factor
        
        cumulative_profit += yearly_profit
        if break_even_year is None and cumulative_profit >= 0:
            break_even_year = year

        projections.append({
            "year": year,
            "revenue": round(annual_revenue, 2),
            "cost": cost, # Using TCO value directly
            "profit": round(yearly_profit, 2),
            "cumulative": round(cumulative_profit, 2)
        })
        total_actual_revenue += annual_revenue
        total_actual_profit += yearly_profit

    roi = total_actual_profit / max(initial_cost, 1)

    # Pass everything to AI (including the specs you linked)
    ai_content = generate_ai_business_plan({
        "product_name": product_name,
        "specs": state.get("specs", {}),
        "initial_cost": initial_cost,
        "total_10y": total_10y,
        "revenue": round(total_actual_revenue, 2),
        "profit": round(total_actual_profit, 2)
    })

    # [DEBUG]: Affiche la réponse brute de l'IA
    print("\n--- AI GENERATOR RESPONSE ---")
    print(json.dumps(ai_content, indent=2))
   
    print("-----------------------------\n")

    business_plan = {
        "revenue": round(total_actual_revenue, 2),
        "profit": round(total_actual_profit, 2),
        "roi": round(roi, 4),
        "npv": round(npv, 2),
        "break_even_year": break_even_year,
        "projections": projections,
        "path_to_excel": "./output/business_plan.xlsx",
        "path_to_pdf": "./output/business_plan.pdf",
        **ai_content
    }

    state["business_plan"] = business_plan
    
    import os
    os.makedirs("./output", exist_ok=True)
    
    _generate_full_excel(business_plan, projections, break_even_year)
    _generate_full_pdf(product_name, initial_cost, business_plan, projections, break_even_year)

    return state

def _generate_full_excel(bp, projections, break_even):
    wb = openpyxl.Workbook()
    ws_kpi = wb.active
    ws_kpi.title = "Financial Summary"
    ws_kpi.append(["Metric", "Value"])
    ws_kpi.append(["Total Profit", bp["profit"]])
    ws_kpi.append(["ROI", f"{bp['roi']:.2%}"])
    ws_proj = wb.create_sheet("Projections")
    ws_proj.append(["Year", "Revenue", "Cost", "Profit", "Cumulative"])
    for p in projections:
        ws_proj.append([p["year"], p["revenue"], p["cost"], p["profit"], p["cumulative"]])
    wb.save("./output/business_plan.xlsx")

def _generate_full_pdf(product_name, initial_cost, business_plan, projections, break_even_year):
    doc = SimpleDocTemplate("./output/business_plan.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading2'], spaceAfter=10, spaceBefore=20, color=colors.navy))
    
    story = []
    story.append(Paragraph(f"Business Plan: {product_name}", styles['Title']))
    story.append(Spacer(1, 20))

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary", styles['SectionHeader']))
    story.append(Paragraph(str(business_plan.get("executive_summary", "N/A")), styles['BodyText']))

    # 2. Project Description
    story.append(Paragraph("2. Project Description", styles['SectionHeader']))
    desc = business_plan.get("project_description", {})
    story.append(Paragraph(f"<b>Product:</b> {desc.get('product', 'N/A')}", styles['BodyText']))
    story.append(Paragraph(f"<b>Target Market:</b> {desc.get('target_market', 'N/A')}", styles['BodyText']))
    story.append(Paragraph(f"<b>Value Proposition:</b> {desc.get('value_proposition', 'N/A')}", styles['BodyText']))

    # 3. Market Analysis
    story.append(Paragraph("3. Market Analysis", styles['SectionHeader']))
    market = business_plan.get("market_analysis", {})
    story.append(Paragraph(f"<b>Trends:</b> {market.get('market_trends', 'N/A')}", styles['BodyText']))
    story.append(Paragraph(f"<b>Competition:</b> {market.get('competition', 'N/A')}", styles['BodyText']))
    story.append(Paragraph(f"<b>Opportunities:</b> {market.get('opportunities', 'N/A')}", styles['BodyText']))

    # 4. SWOT Analysis
    story.append(Paragraph("4. SWOT Analysis", styles['SectionHeader']))
    swot = business_plan.get("swot", {})
    swot_data = [
        [Paragraph("<b>Strengths</b>", styles['BodyText']), Paragraph("<b>Weaknesses</b>", styles['BodyText'])],
        [Paragraph("<br/>".join([f"• {x}" for x in swot.get("Strengths", [])]) or "N/A", styles['BodyText']),
         Paragraph("<br/>".join([f"• {x}" for x in swot.get("Weaknesses", [])]) or "N/A", styles['BodyText'])],
        [Paragraph("<b>Opportunities</b>", styles['BodyText']), Paragraph("<b>Threats</b>", styles['BodyText'])],
        [Paragraph("<br/>".join([f"• {x}" for x in swot.get("Opportunities", [])]) or "N/A", styles['BodyText']),
         Paragraph("<br/>".join([f"• {x}" for x in swot.get("Threats", [])]) or "N/A", styles['BodyText'])]
    ]
    swot_table = Table(swot_data, colWidths=[240, 240])
    swot_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (1, 0), colors.whitesmoke),
        ('BACKGROUND', (0, 2), (1, 2), colors.whitesmoke),
    ]))
    story.append(swot_table)

    # 5. Financial Highlights
    story.append(Paragraph("5. Financial Highlights", styles['SectionHeader']))
    financial_data = [
        ["Metric", "Value"],
        ["Initial Investment", f"{initial_cost:,.2f} USD"],
        ["Break-even Year", f"Year {break_even_year}" if break_even_year else "Not reached"],
        ["Return on Investment (ROI)", f"{business_plan['roi'] * 100:.2f}%"],
        ["Estimated NPV", f"{business_plan['npv']:,.2f} USD"]
    ]
    fin_table = Table(financial_data, colWidths=[200, 200])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(fin_table)

    # 6. Projections
    story.append(Paragraph("6. 10-Year Projections", styles['SectionHeader']))
    cashflow_data = [["Year", "Revenue", "Cost", "Profit", "Cumulative"]]
    for p in projections:
        cashflow_data.append([str(p["year"]), f"{p['revenue']:,.0f}", f"{p['cost']:,.0f}", f"{p['profit']:,.0f}", f"{p['cumulative']:,.0f}"])
    
    cf_table = Table(cashflow_data, colWidths=[50, 90, 90, 90, 90])
    cf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    story.append(cf_table)

    # 7. Recommendations
    story.append(Paragraph("7. Recommendations", styles['SectionHeader']))
    story.append(Paragraph(str(business_plan.get("recommendations", "No specific recommendations provided.")), styles['BodyText']))

    # 8. Conclusion
    story.append(Paragraph("8. Conclusion", styles['SectionHeader']))
    story.append(Paragraph(str(business_plan.get("conclusion", "Investment in this project is recommended based on current projections.")), styles['BodyText']))

    doc.build(story)
