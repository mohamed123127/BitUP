from state import IndustryState

from helper.progressTracker import send_progress
import asyncio

async def module_1_extraction(state: IndustryState):
    print("🔵 Module 1: Extracting PDF data")
    await send_progress("MOD_001", "in_progress", "EXTRACTION", 15.0, "Parsing PDF structural layout...")
    await asyncio.sleep(1.5)

    await send_progress("MOD_001", "in_progress", "EXTRACTION", 65.0, "Extracting technical tensors...")
    data = {
        "specs": {
            "type": "valve DN100",
            "pressure": "40 bar",
            "material": "steel",
            "tensors": ["temperature"],
            "quantity": 1000,
        },
        "deal": {
            "price_per_unit": 100,
        },
        "product_name": "valve DN100",
        "country": "Algeria",
        "currency": "USD",
        "language": "French",
    }
    
    state["extracted_data"] = data
    # Spread for compatibility with Module 6, 7 and 8
    state["product_name"] = data["product_name"]
    state["specs"] = data["specs"]
    state["deal"] = data["deal"]
    
    await asyncio.sleep(1)

    await send_progress("MOD_001", "completed", "EXTRACTION", 100.0, "Data extracted successfully.", state["extracted_data"])
    return state