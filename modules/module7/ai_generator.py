import json
import os
import requests

def generate_fallback_plan(data: dict) -> dict:
    """Génère un plan de secours structuré quand l'IA échoue."""
    product = data.get('product_name', 'Produit')
    profit = data.get('profit', 0)
    
    return {
        "executive_summary": f"Analyse stratégique pour {product}. Malgré les défis du marché, ce projet présente un potentiel de rentabilité de {profit:,.2f} USD sur 10 ans.",
        "project_description": {
            "product": product,
            "target_market": "Secteur industriel et technologique haut de gamme.",
            "value_proposition": f"Solution optimisée basée sur des spécifications de haute performance pour maximiser le ROI."
        },
        "market_analysis": {
            "market_trends": "Croissance annuelle stable dans le segment de luxe/industriel.",
            "competition": "Acteurs majeurs établis, mais opportunité de niche sur la qualité.",
            "opportunities": "Expansion vers des marchés émergents et optimisation des coûts."
        },
        "swot": {
            "Strengths": ["Performance technique", "Expertise reconnue", "Marge opérationnelle"],
            "Weaknesses": ["Coût initial élevé", "Dépendance fournisseurs"],
            "Opportunities": ["Digitalisation", "Nouveaux segments", "Économies d'échelle"],
            "Threats": ["Inflation", "Instabilité logistique", "Nouveaux entrants"]
        },
        "recommendations": "Poursuivre l'investissement avec un focus sur le contrôle de la qualité et la fidélisation client.",
        "conclusion": "Le projet est viable financièrement avec un seuil de rentabilité atteint dans les délais prévus."
    }

def generate_ai_business_plan(data: dict) -> dict:
    """
    Génère un business plan via Google Gemini (ou fallback) en français.
    """
    # Utilisation de la clé Gemini fournie par l'utilisateur
    api_key = "AIzaSyBcXARTaEQgAoND42Praf-4DdqcdvXHIZI"
    # Modèle mis à jour pour 2026 (Gemini 2.0 Flash)
    model_name = "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    product_name = data.get('product_name', 'Produit')
    profit = data.get('profit', 0)
    specs = data.get("specs", {})

    prompt = f"""
    Agis en tant qu'analyste McKinsey. Génère un business plan professionnel COMPLET en français pour {product_name}.
    Données financières attendues : Profit de {profit} USD.
    Spécifications techniques : {json.dumps(specs)}

    Tu DOIS renvoyer UNIQUEMENT un objet JSON valide avec cette structure exacte :
    {{
      "executive_summary": "...",
      "project_description": {{"product": "...", "target_market": "...", "value_proposition": "..."}},
      "market_analysis": {{"market_trends": "...", "competition": "...", "opportunities": "..."}},
      "swot": {{"Strengths": [], "Weaknesses": [], "Opportunities": [], "Threats": []}},
      "recommendations": "...",
      "conclusion": "..."
    }}
    L'objet JSON doit être prêt à être parsé par json.loads().
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 2048,
            "responseMimeType": "application/json"
        }
    }

    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"[-] Gemini API Error (Status {response.status_code}): {response.text}")
            return generate_fallback_plan(data)

        res_json = response.json()
        
        # Extraction du texte du candidat Gemini
        if "candidates" in res_json and len(res_json["candidates"]) > 0:
            text_response = res_json["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text_response)
        else:
            print("[-] No candidates found in Gemini response.")
            return generate_fallback_plan(data)

    except Exception as e:
        print(f"[-] Exception during Gemini generation: {e}")
        return generate_fallback_plan(data)