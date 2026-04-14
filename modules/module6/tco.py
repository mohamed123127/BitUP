import openpyxl
import json
import requests

def get_inflation_rate(country="DZA"):
    try:
        url = f"https://api.worldbank.org/v2/country/{country}/indicator/FP.CPI.TOTL.ZG?format=json"
        response = requests.get(url, timeout=5)
        data = response.json()
        values = [entry for entry in data[1] if entry["value"] is not None]
        if values:
            return float(values[0]["value"]) / 100
    except:
        pass
    return 0.05

def calculate_tco(state: dict) -> dict:
    specs = state.get("specs", {})
    deal = state.get("deal", {})
    suppliers = state.get("suppliers", [])

    quantity = specs.get("quantity", 0)
    price_per_unit = deal.get("price_per_unit", 0.0)

    initial_cost = quantity * price_per_unit
    inflation_rate = get_inflation_rate()

    yearly_costs = []
    current_cost = initial_cost

    for year in range(10):
        if year > 0:
            current_cost *= (1 + inflation_rate)
        yearly_costs.append(round(current_cost, 2))

    total_10y = round(sum(yearly_costs), 2)

    # state.py updates
    state["tco"] = {
        "initial_cost": round(initial_cost, 2),
        "yearly_costs": yearly_costs,
        "total_10y": total_10y,
        "path_to_excel": "./output/tco.xlsx"
    }

    # Excel Export
    import os
    os.makedirs("./output", exist_ok=True)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "TCO Simulation"
    ws.append(["Year", "Cost"])
    for i, cost in enumerate(yearly_costs, 1):
        ws.append([i, cost])
    wb.save("./output/tco.xlsx")
    
    return state
