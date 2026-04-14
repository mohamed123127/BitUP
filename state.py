from typing import TypedDict, List, Optional, Dict, Literal

latest_progress = {}

# =========================
# SUPPLIER MODEL
# =========================
class Supplier(TypedDict):
    name: str
    country: str
    material: str
    price_per_unit: float
    reliability_score: float


# =========================
# TCO MODEL
# =========================
class TCO(TypedDict):
    initial_cost: float
    maintenance_cost_annual: float
    energy_cost_annual: float
    inflation_rate: float
    total_10_year_cost: float
    currency: str


# =========================
# BUSINESS PLAN MODEL
# =========================
class BusinessPlan(TypedDict):
    roi: float
    van: float
    payback_period_years: float
    risk_level: Literal["low", "medium", "high"]
    swot: Dict[str, List[str]]
    revenue_projection_3y: List[float]


# =========================
# ML / DIGITAL TWIN MODEL
# =========================
class MLFeatures(TypedDict):
    sensors_used: List[str]
    feature_vector_size: int
    model_type: str
    accuracy: Optional[float]


# =========================
# ANOMALY MODEL
# =========================
class Anomaly(TypedDict):
    timestamp: str
    sensor: str
    value: float
    anomaly_score: float
    severity: Literal["low", "medium", "high"]


# =========================
# CATALOG OUTPUT MODEL
# =========================
class CatalogFiles(TypedDict):
    json: str
    html: str
    pdf: str
    excel: str
    xml: str


# =========================
# MAIN LANGGRAPH STATE
# =========================
class IndustryState(TypedDict):
    # INPUT
    pdf_path: str

    # MODULE 1 - EXTRACTION
    extracted_data: Dict[str, str]

    # MODULE 2 / 3 - CAD + VIDEO
    dxf_path: Optional[str]
    video_path: Optional[str]

    # MODULE 4 - SOURCING
    suppliers: List[Supplier]

    # MODULE 5 - NEGOTIATION
    negotiation_result: Dict[str, str]

    # MODULE 6 - TCO
    tco: TCO

    # MODULE 7 - BUSINESS PLAN
    business_plan: BusinessPlan

    # MODULE 8 - DIGITAL TWIN / ML
    ml_features: MLFeatures
    anomalies: List[Anomaly]

    # MODULE 9 - FINAL CATALOG
    catalog_files: CatalogFiles