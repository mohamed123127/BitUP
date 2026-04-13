import state

async def send_progress(id:int,status: str, module: str, progress: float, message: str = "", data: dict = None):
    state.latest_progress = {
        "id": id,
        "status": status,
        "module": module,
        "progress": progress,
        "message": message,
        "data": data or {}
    }