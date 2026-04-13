from .helpers.exporters import export_all

from helper.progressTracker import send_progress
import asyncio

async def module_9_catalog(state):
    print("📦 Module 9: Exporting catalog")
    await send_progress("MOD_009", "in_progress", "CATALOG_GENERATION", 10.0, "Aggregating outputs for catalog...")
    await asyncio.sleep(1)

    data = {
        "extracted_data": state.get("extracted_data", {}),
        "suppliers": state.get("suppliers", []),
        "tco": state.get("tco", {}),
        "business_plan": state.get("business_plan", {}),
        "ml_features": state.get("ml_features", {})
    }

    await send_progress("MOD_009", "in_progress", "CATALOG_GENERATION", 60.0, "Exporting to JSON, HTML, PDF, EXCEL, XML...")
    state["catalog_files"] = export_all(data)
    await asyncio.sleep(1)

    print("✅ Catalog generated in all formats")
    await send_progress("MOD_009", "completed", "CATALOG_GENERATION", 100.0, "Catalog packaging complete.", state["catalog_files"])

    return state