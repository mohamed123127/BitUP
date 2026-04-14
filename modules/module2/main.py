from state import IndustryState, CADPiece, CADResult
from helper.progressTracker import send_progress
import asyncio
from .Module2 import generate_cad


def _parse_dimension(dimensions: dict, key: str, default: float) -> float:
    raw = dimensions.get(key, {})
    if isinstance(raw, dict):
        value = raw.get("value")
    else:
        value = raw
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _build_pieces_from_extracted(extracted: dict) -> list[dict]:
    dimensions = extracted.get("dimensions", {})
    material = extracted.get("material", "Piece")
    length = _parse_dimension(dimensions, "longueur_totale", 120.0)
    width = _parse_dimension(dimensions, "hauteur", 60.0)
    dn = _parse_dimension(dimensions, "DN", 0.0)

    if width <= 0:
        width = 60.0
    if length <= 0:
        length = 120.0

    piece_name = f"{material}"
    if dn > 0:
        piece_name = f"DN{int(dn)} {material}"

    return [
        {
            "name": piece_name,
            "length": length,
            "width": width,
            "position": [0.0, 0.0],
            "angle": 0.0,
        }
    ]


async def module_2_cad(state: IndustryState):
    print("🔴 Module 2: CAD Generation")
    await send_progress(
        "MOD_002",
        "in_progress",
        "CAD_GENERATION",
        10.0,
        "Initializing CAD workspace...",
    )
    await asyncio.sleep(1)

    extracted = state.get("extracted_data", {})
    pieces_data = _build_pieces_from_extracted(extracted)

    if not pieces_data:
        print(
            " No drawable CAD geometry could be built from module1 output. Skipping CAD generation."
        )
        state["cad_result"] = CADResult(pieces=[], dxf_path="")
        state["dxf_path"] = ""
        return state

    await send_progress(
        "MOD_002", "in_progress", "CAD_GENERATION", 50.0, "Generating DXF geometry..."
    )

    output_path = "output/module2_cad_output.dxf"
    generate_cad(pieces_data, output_path)

    cad_pieces = [CADPiece(**p) for p in pieces_data]
    state["cad_result"] = CADResult(
        pieces=cad_pieces,
        dxf_path=output_path,
    )
    state["dxf_path"] = output_path

    print(
        f"✅ Module 2 generated {len(pieces_data)} CAD piece(s) from module1 dimensions"
    )

    return state
