import state
import asyncio
from graph import build_graph
from helper.progressTracker import send_progress

async def run_pipeline(file_path: str):
    app = build_graph()

    await send_progress("MOD_INIT", "in_progress", "INITIALIZATION", 0.0, "Starting pipeline...", {"file_path": file_path})

    initial_state = {"pdf_path": file_path}

    result = await app.ainvoke(initial_state)

    await send_progress("MOD_INIT", "completed", "FINAL", 100.0, "Pipeline finished successfully.", result)

    print("\n✅ FINAL RESULT:")
    print(result)

if __name__ == "__main__":
    asyncio.run(run_pipeline("./input/TP_WAMS_AOS_5.pdf"))