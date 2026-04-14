import os
from dotenv import load_dotenv, find_dotenv
import requests
from state import IndustryState
from helper.progressTracker import send_progress
import asyncio

load_dotenv(find_dotenv())

HUNTER_SEARCH_URL = "https://api.hunter.io/v2/search"
WIKIDATA_SEARCH_URL = "https://www.wikidata.org/w/api.php"
COMTRADE_PREVIEW_URL = "https://comtradeapi.un.org/public/v1/preview"


def _hunter_search_contacts(query: str):
    api_key = os.getenv("HUNTER_API_KEY")
    if not api_key:
        return []

    params = {
        "company": query,
        "api_key": api_key,
        "limit": 5,
    }

    try:
        response = requests.get(HUNTER_SEARCH_URL, params=params, timeout=(5, 20))
        response.raise_for_status()
        payload = response.json()
        emails = payload.get("data", {}).get("emails", [])

        contacts = []
        for email in emails[:5]:
            contacts.append(
                {
                    "first_name": email.get("first_name", ""),
                    "last_name": email.get("last_name", ""),
                    "email": email.get("value", ""),
                    "position": email.get("position", ""),
                    "confidence": str(email.get("confidence", "")),
                    "source": email.get("source", {}).get("domain", ""),
                }
            )

        return contacts
    except requests.exceptions.RequestException as exc:
        print(f"Hunter API error: {exc}")
        return []


def _wikidata_search_suppliers(material: str):
    if not material or material == "unknown":
        return []

    params = {
        "action": "query",
        "list": "search",
        "srsearch": f"{material} supplier",
        "format": "json",
        "srlimit": 3,
    }

    try:
        response = requests.get(WIKIDATA_SEARCH_URL, params=params, timeout=(5, 20))
        response.raise_for_status()
        payload = response.json()
        search_results = payload.get("query", {}).get("search", [])

        suppliers = []
        for result in search_results:
            suppliers.append(
                _build_supplier(
                    name=f"Wikidata: {result.get('title', 'Supplier')}",
                    country="International",
                    material=material,
                    contacts=_fallback_contacts(),
                    source="wikidata",
                    trade_metrics={
                        "wikidata_score": result.get("size", 0),
                        "wikidata_snippet": result.get("snippet", ""),
                    },
                )
            )

        return suppliers
    except requests.exceptions.RequestException as exc:
        print(f"Wikidata API error: {exc}")
        return []


def _comtrade_trade_summary(material: str):
    api_key = os.getenv("COMTRADE_API_KEY")
    if not api_key:
        return {}

    params = {
        "reporter": "all",
        "partner": "all",
        "freq": "A",
        "type": "C",
        "clCode": "TOTAL",
        "token": api_key,
    }

    try:
        response = requests.get(COMTRADE_PREVIEW_URL, params=params, timeout=(5, 20))
        response.raise_for_status()
        payload = response.json()
        dataset = payload.get("dataset", [])
        total_trade = 0.0
        for item in dataset[:3]:
            value = item.get("TradeValue") or item.get("tradeValue") or 0
            try:
                total_trade += float(value)
            except (TypeError, ValueError):
                continue

        return {
            "material": material,
            "total_trade_usd": total_trade,
            "record_count": len(dataset),
        }
    except requests.exceptions.RequestException as exc:
        print(f"Comtrade API error: {exc}")
        return {}


def _normalize_material_field(raw):
    if isinstance(raw, dict):
        return raw.get("value") or raw.get("material") or str(raw)
    if isinstance(raw, str):
        return raw
    return "unknown"


def _fallback_contacts():
    return [
        {
            "first_name": "Service",
            "last_name": "Commercial",
            "email": "contact@supplier-example.com",
            "position": "Responsable de compte",
            "confidence": "0",
            "source": "fallback",
        }
    ]


def _build_supplier(
    name: str,
    country: str,
    material: str,
    contacts: list,
    source: str = "internal",
    trade_metrics: dict | None = None,
):
    return {
        "name": name,
        "country": country,
        "material": material,
        "price_per_unit": 12.5 if country == "France" else 10.0,
        "reliability_score": 85.0 if country == "France" else 75.0,
        "contacts": contacts or _fallback_contacts(),
        "source": source,
        "trade_metrics": trade_metrics or {},
    }


async def module_4_sourcing(state: IndustryState):
    print("🟢 Module 4: Sourcing supplier information")
    await send_progress(
        "MOD_004", "in_progress", "SOURCING", 10.0, "Collecting supplier candidates..."
    )
    await asyncio.sleep(1)

    material = _normalize_material_field(
        state.get("extracted_data", {}).get("material", "unknown")
    )
    query = f"{material} supplier"

    hunter_contacts = _hunter_search_contacts(query)
    wikidata_suppliers = _wikidata_search_suppliers(material)
    comtrade_data = _comtrade_trade_summary(material)

    suppliers = [
        _build_supplier(
            name=f"Hunter supplier for {material}",
            country="France",
            material=material,
            contacts=hunter_contacts,
            source="hunter",
            trade_metrics={"contact_count": len(hunter_contacts)},
        )
    ]
    suppliers.extend(wikidata_suppliers)

    state["suppliers"] = suppliers
    state["comtrade_data"] = comtrade_data

    print(f"🔎 Module 4 query: {query}")
    print(f"📌 Contacts trouvés par Hunter: {len(hunter_contacts)}")
    print(f"✅ Suppliers count: {len(suppliers)}")
    print("✅ Module 4 output:")
    print(state["suppliers"])
    print("📊 Comtrade summary:")
    print(comtrade_data)

    await send_progress(
        "MOD_004",
        "completed",
        "SOURCING",
        100.0,
        "Sourcing completed.",
        state["suppliers"],
    )

    return state
