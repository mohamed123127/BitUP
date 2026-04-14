from modules.module1.agent import SpecExtractionAgent
from state import IndustryState

from helper.progressTracker import send_progress
import asyncio
import re
from dataclasses import asdict


def _parse_number(raw):
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str):
        match = re.search(r"[-+]?[0-9]*[\.,]?[0-9]+", raw)
        if match:
            return float(match.group(0).replace(",", "."))
    return None


def _normalize_entry(raw, default_unit, default_confidence=0):
    if isinstance(raw, dict):
        value = _parse_number(raw.get("value"))
        unit = raw.get("unit", default_unit)
        confidence = raw.get("confidence", default_confidence) or default_confidence
    else:
        value = _parse_number(raw)
        unit = default_unit
        confidence = default_confidence

    return {
        "value": value,
        "unit": unit,
        "confidence": confidence,
    }


def _normalize_material(raw):
    if isinstance(raw, dict):
        return {
            "value": raw.get("value"),
            "norme": raw.get("norme"),
            "confidence": raw.get("confidence", 0),
        }

    return {
        "value": str(raw) if raw is not None else None,
        "norme": None,
        "confidence": 0,
    }


def _normalize_confidence(raw):
    if isinstance(raw, (int, float)):
        return int(raw * 100) if 0 <= raw <= 1 else int(raw)
    return 0


def _build_default_pieces(dimensions, material_name):
    length = dimensions.get("longueur_totale", {}).get("value") or 100.0
    width = (
        dimensions.get("hauteur", {}).get("value")
        or dimensions.get("DN", {}).get("value")
        or 50.0
    )
    try:
        length = float(length)
    except (TypeError, ValueError):
        length = 100.0
    try:
        width = float(width)
    except (TypeError, ValueError):
        width = 50.0

    if length <= 0:
        length = 100.0
    if width <= 0:
        width = 50.0

    return [
        {
            "name": f"Pièce {material_name}",
            "length": length,
            "width": width,
            "position": [0.0, 0.0],
            "angle": 0.0,
        }
    ]


import ast


def _normalize_materials(raw):
    if isinstance(raw, str):
        try:
            raw = ast.literal_eval(raw)
        except Exception:
            return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        # Accept either a list-style dict or a dict with material slots
        return [
            raw.get("corps"),
            raw.get("joint_siege"),
            raw.get("fixations"),
        ]
    return []


def _first_material(raw):
    if isinstance(raw, str):
        try:
            raw = ast.literal_eval(raw)
        except Exception:
            return raw
    if isinstance(raw, list) and raw:
        first = raw[0]
        if isinstance(first, dict):
            return first.get("value") or first.get("name") or "unknown"
        return str(first) if first is not None else "unknown"
    if isinstance(raw, dict):
        for key in ("corps", "joint_siege", "fixations"):
            item = raw.get(key)
            if item:
                if isinstance(item, dict):
                    return item.get("value") or item.get("name") or str(item)
                return str(item)
        first = next(iter(raw.values()), None)
        if isinstance(first, dict):
            return first.get("value") or first.get("name") or str(first)
        return str(first) if first is not None else "unknown"
    return "unknown"


async def module_1_extraction(state: IndustryState):
    print("🔵 Module 1: Extracting PDF data")
    await send_progress(
        "MOD_001", "in_progress", "EXTRACTION", 15.0, "Parsing PDF structural layout..."
    )
    await asyncio.sleep(1.5)

    await send_progress(
        "MOD_001", "in_progress", "EXTRACTION", 65.0, "Extracting technical tensors..."
    )
    extractor = SpecExtractionAgent()
    specs = extractor.extract_from_pdf(state.get("pdf_path"))

    materials = _normalize_materials(specs.materials)
    material_name = _first_material(specs.materials)

    state["extracted_data"] = {
        "type": "valve DN100",
        "material": material_name,
        "tensors": [
            "temperature" if specs.temperature else "",
            "pressure" if specs.pressure else "",
        ],
        "dimensions": {
            "DN": _normalize_entry(specs.dimensions.get("DN"), "mm"),
            "longueur_totale": _normalize_entry(
                specs.dimensions.get("longueur_totale"), "mm"
            ),
            "hauteur": _normalize_entry(specs.dimensions.get("hauteur"), "mm"),
            "epaisseur_paroi": _normalize_entry(
                specs.dimensions.get("epaisseur_paroi"), "mm"
            ),
            "poids": _normalize_entry(specs.dimensions.get("poids"), "kg"),
        },
        "materials": {
            "corps": _normalize_material(materials[0] if len(materials) > 0 else None),
            "joint_siege": _normalize_material(
                materials[1] if len(materials) > 1 else None
            ),
            "fixations": _normalize_material(
                materials[2] if len(materials) > 2 else None
            ),
        },
        "tolerances": {
            "generale": _normalize_entry(specs.tolerances.get("generale"), "", 0),
            "surface_Ra": _normalize_entry(specs.tolerances.get("surface_Ra"), "μm"),
            "planeite": _normalize_entry(specs.tolerances.get("planeite"), "mm"),
        },
        "pressure": {
            "PN_nominal": _normalize_entry(specs.pressure.get("PN_nominal"), "bar"),
            "PS_service": _normalize_entry(specs.pressure.get("PS_service"), "bar"),
            "pression_test": _normalize_entry(
                specs.pressure.get("pression_test"), "bar"
            ),
        },
        "temperature": {
            "T_min": _normalize_entry(specs.temperature.get("T_min"), "°C"),
            "T_max": _normalize_entry(specs.temperature.get("T_max"), "°C"),
        },
        "confidence": {
            "dimensions": _normalize_confidence(specs.confidence.get("dimensions")),
            "materials": _normalize_confidence(specs.confidence.get("materials")),
            "tolerances": _normalize_confidence(specs.confidence.get("tolerances")),
            "pressure": _normalize_confidence(specs.confidence.get("pressure")),
            "temperature": _normalize_confidence(specs.confidence.get("temperature")),
        },
        "specs": asdict(specs),
        "pieces": specs.__dict__.get("pieces") or _build_default_pieces(
            {
                "DN": _normalize_entry(specs.dimensions.get("DN"), "mm"),
                "longueur_totale": _normalize_entry(specs.dimensions.get("longueur_totale"), "mm"),
                "hauteur": _normalize_entry(specs.dimensions.get("hauteur"), "mm"),
            },
            material_name,
        ),
    }

    state["extracted_data"]["tensors"] = [
        t for t in state["extracted_data"]["tensors"] if t
    ]

    await send_progress(
        "MOD_001",
        "completed",
        "EXTRACTION",
        100.0,
        "Data extracted successfully.",
        state["extracted_data"],
    )

    print("✅ Module 1 output:")
    print(state["extracted_data"])
    return state
