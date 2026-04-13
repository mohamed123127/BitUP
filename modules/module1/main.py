from state import IndustryState

from helper.progressTracker import send_progress
import asyncio

async def module_1_extraction(state: IndustryState):
    print("🔵 Module 1: Extracting PDF data")
    await send_progress("MOD_001", "in_progress", "EXTRACTION", 15.0, "Parsing PDF structural layout...")
    await asyncio.sleep(1.5)

    await send_progress("MOD_001", "in_progress", "EXTRACTION", 65.0, "Extracting technical tensors...")
    state["extracted_data"] = {
        "type": "valve DN100",
        "pressure": "40 bar",
        "material": "steel",
        "tensors": ["temperature"],
    }
    await asyncio.sleep(1)

    await send_progress("MOD_001", "completed", "EXTRACTION", 100.0, "Data extracted successfully.", state["extracted_data"])
    return state