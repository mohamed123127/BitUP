from .business_plan import calculate_business_plan
from helper.progressTracker import send_progress
import asyncio

async def module_7_business_plan(state):
    print("📈 Module 7: Generating Business Plan")
    await send_progress("MOD_007", "in_progress", "BUSINESS_PLAN", 10.0, "Analyzing TCO and calculating profitability...")
    await asyncio.sleep(1)

    # Perform calculations and AI generation
    state = calculate_business_plan(state)

    await send_progress("MOD_007", "in_progress", "BUSINESS_PLAN", 80.0, "Business plan generated, finalizing reports...")
    await asyncio.sleep(1)

    print("✅ Business Plan complete")
    await send_progress("MOD_007", "completed", "BUSINESS_PLAN", 100.0, "Business strategy analysis complete.")

    return state
