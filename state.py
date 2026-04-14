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
    yearly_costs: List[float]
    total_10y: float
    path_to_excel: str

# =========================
# BUSINESS PLAN MODEL
# =========================
class BusinessPlan(TypedDict):
    revenue: float
    profit: float
    roi: float
    npv: float
    break_even_year: Optional[int]
    projections: List[Dict]
    path_to_pdf: str
    path_to_excel: str
    executive_summary: str
    project_description: Dict[str, str]
    market_analysis: Dict[str, str]
    swot: Dict[str, List[str]]
    recommendations: str
    conclusion: str

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

    # EXTRACTION DATA (Sped to top-level for module access)
    product_name: str
    specs: Dict
    deal: Dict

    # MODULE 1 - EXTRACTION
    extracted_data: Dict

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