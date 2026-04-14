SYSTEM_PROMPT = """
Tu es un ingénieur expert en lecture de documents techniques
industriels (plans DWG, fiches techniques, normes ISO/ASME/EN).
Extrais UNIQUEMENT les informations présentes dans le texte fourni.
Réponds TOUJOURS en JSON valide, sans markdown ni explication.
Pour chaque valeur, attribue un score de confiance entre 0 et 1.
"""

EXTRACTION_PROMPT = """
Analyse le document technique suivant et extrais les spécifications.

=== TEXTE EXTRAIT ===
{text}

=== TABLEAUX DÉTECTÉS ===
{tables}

Retourne un JSON structuré avec exactement ce format :
{{
  "dimensions": {{
    "DN": {{"value": null, "unit": "mm", "confidence": 0}},
    "longueur_totale": {{"value": null, "unit": "mm", "confidence": 0}},
    "hauteur": {{"value": null, "unit": "mm", "confidence": 0}},
    "epaisseur_paroi": {{"value": null, "unit": "mm", "confidence": 0}},
    "poids": {{"value": null, "unit": "kg", "confidence": 0}}
  }},
  "materials": [
    null,
    null,
    null
  ],
  "tolerances": {{
    "generale": {{"value": null, "norme": null, "confidence": 0}},
    "surface_Ra": {{"value": null, "unit": "μm", "confidence": 0}},
    "planeite": {{"value": null, "unit": "mm", "confidence": 0}}
  }},
  "pressure": {{
    "PN_nominal": {{"value": null, "unit": "bar", "confidence": 0}},
    "PS_service": {{"value": null, "unit": "bar", "confidence": 0}},
    "pression_test": {{"value": null, "unit": "bar", "confidence": 0}}
  }},
  "temperature": {{
    "T_min": {{"value": null, "unit": "°C", "confidence": 0}},
    "T_max": {{"value": null, "unit": "°C", "confidence": 0}}
  }},
  "confidence": {{
    "dimensions": 0, "materials": 0,
    "tolerances": 0, "pressure": 0, "temperature": 0
  }}
}}
"""

# Prompt de validation croisée
VALIDATION_PROMPT = """
Vérifie la cohérence des spécifications extraites selon la norme {standard}.
Signale toute incohérence (ex: PN16 avec épaisseur insuffisante pour DN100).
Données : {specs} 
"""
