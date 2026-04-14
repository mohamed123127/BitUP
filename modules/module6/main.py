from .tco import calculate_tco
from helper.progressTracker import send_progress
import asyncio

async def module_6_tco(state):
    print("💰 Module 6: Calculating TCO")
    await send_progress("MOD_006", "in_progress", "TCO_CALCULATION", 10.0, "Starting TCO calculation...")
    await asyncio.sleep(1)

    # Perform the TCO calculation
    state = calculate_tco(state)

    await send_progress("MOD_006", "in_progress", "TCO_CALCULATION", 80.0, "TCO calculated, exporting to Excel...")
    await asyncio.sleep(1)

    print("✅ TCO Calculation complete")
    await send_progress("MOD_006", "completed", "TCO_CALCULATION", 100.0, "TCO analysis finished.")

    return state
