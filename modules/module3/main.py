from state import IndustryState, VideoResult
from helper.progressTracker import send_progress
import asyncio
import os

async def module_3_video(state: IndustryState):
    print("🎬 Module 3: Video Generation")
    
    # Get DXF path from Module 2
    cad_result = state.get("cad_result", {})
    dxf_path = cad_result.get("dxf_path")

    if not dxf_path:
        print("⚠️ No DXF path found in state. Module 3 requires output from Module 2.")
        await send_progress("MOD_003", "failed", "VIDEO_GENERATION", 0.0, "Missing DXF input from Module 2")
        return state

    await send_progress("MOD_003", "in_progress", "VIDEO_GENERATION", 20.0, f"Loading DXF from: {dxf_path}...")
    await asyncio.sleep(1)

    # Manim rendering simulation (since full rendering is resources intensive)
    await send_progress("MOD_003", "in_progress", "VIDEO_GENERATION", 60.0, "Rendering 3D scene with Manim engine...")
    await asyncio.sleep(2)

    # In a real scenario, this would be the output path from Manim
    video_output = dxf_path.replace(".dxf", ".mp4")
    
    # Mocking video creation
    state["video_result"] = VideoResult(
        video_path=video_output,
        duration=5.0,
        resolution="1920x1080",
        fps=30
    )
    state["video_path"] = video_output
    
    await asyncio.sleep(1)
    await send_progress("MOD_003", "completed", "VIDEO_GENERATION", 100.0, "Video rotation rendered successfully.", state["video_result"])
    
    return state
