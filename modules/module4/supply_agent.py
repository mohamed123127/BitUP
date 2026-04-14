import os
import json
import requests
from groq import Groq
from dotenv import load_dotenv, find_dotenv

# Permet de remonter lire le .env du dossier parent (pour la clé Groq)
load_dotenv(find_dotenv())

LLM_MAPPING_PROMPT = """
Tu es un expert en logistique internationale et en nomenclature douanière.
Ton travail est de traduire le nom brut d'un matériau obtenu depuis une fiche technique vers des standards internationaux.

On te donne un matériau en français (ex: "Acier Inoxydable 316L", "Laiton CW617N", "PTFE").
Retourne un JSON strict avec ce format :
{
  "hs_code": "Le code SH (Harmonized System) à 4 ou 6 chiffres correspondant au matériau (ex: 7219 pour l'inox, 7403 pour le laiton).",
  "wikidata_term": "Le nom générique COURT du matériau en anglais pour la requête Wikidata (ex: stainless steel, brass, polytetrafluoroethylene)"
}
"""

class SupplyChainAgent:
    def __init__(self, model="llama-3.3-70b-versatile"):
        self.groq_client = Groq()
        self.model = model
        self.comtrade_api_key = os.getenv("COMTRADE_API_KEY")

    def analyze_material(self, material_raw: str):
        print(f"🌍 Début de l'analyse Supply Chain pour : {material_raw}...")
        
        # 1. Étape d'Intelligence artificielle (Conversion)
        mapping = self._get_material_mapping(material_raw)
        hs_code = mapping.get("hs_code", "INCONNU")
        wiki_term = mapping.get("wikidata_term", "INCONNU")
        print(f"✔️  Classification par l'IA : Code Douane SH = {hs_code} | Recherche Wikidata = {wiki_term}")

        # 2. Interrogation SPARQL Wikidata
        wiki_results = self._query_wikidata(wiki_term)
        
        # 3. Interrogation Douane UN Comtrade
        comtrade_results = self._query_un_comtrade(hs_code)
        
        return {
            "materiau_origne": material_raw,
            "classification_standard": mapping,
            "fournisseurs_potentiels_wikidata": wiki_results,
            "donnees_comtrade": comtrade_results
        }
        
    def _get_material_mapping(self, material_raw: str) -> dict:
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                max_tokens=250,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": LLM_MAPPING_PROMPT},
                    {"role": "user", "content": f"Trouve le HS Code et le terme anglais pour : {material_raw}"}
                ]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"❌ Erreur LLM : {e}")
            return {"hs_code": "7403", "wikidata_term": "brass"} # Fallback

    def _query_wikidata(self, search_term: str):
        print(f"🔍 Interrogation Wikidata pour '{search_term}'...")
        
        # Utilise l'API MediaWiki Search au lieu de SPARQL → 10x plus rapide
        url = "https://www.wikidata.org/w/api.php"
        params = {
            "action":   "wbsearchentities",
            "search":   search_term,
            "language": "en",
            "type":     "item",
            "limit":    "10",
            "format":   "json",
        }
        
        try:
            headers = {"User-Agent": "SupplyChainBot/1.0 (contact@example.com)"}
            r = requests.get(url, params=params, headers=headers, timeout=(10, 20))
            r.raise_for_status()
            results = r.json().get("search", [])
            
            if not results:
                return f"Aucun résultat Wikidata pour '{search_term}'."
            
            # Retourne les entités trouvées avec description
            return [
                {
                    "id":          item.get("id"),
                    "label":       item.get("label", "?"),
                    "description": item.get("description", "Non décrit"),
                    "url":         item.get("url", ""),
                }
                for item in results[:5]
            ]
        
        except requests.exceptions.Timeout:
            return "Timeout Wikidata — réessayez."
        except Exception as e:
            return f"Erreur Wikidata : {e}"

    def _query_un_comtrade(self, hs_code: str):
        print(f"🚢 Interrogation de UN Comtrade (Code SH: {hs_code})...")

        if not self.comtrade_api_key or self.comtrade_api_key == "votre_cle_un_comtrade_ici":
            return {"status": "Non exécuté", "raison": "Clé API manquante."}

        # Il FAUT utiliser l'endpoint public/preview si on veut interroger le monde entier ('all') d'un coup
        url = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
        params = {
            "period":           "2022",
            "reporterCode":     "all",      # 0 donnait un résultat vide "[]", il faut "all"
            "cmdCode":          hs_code,
            "flowCode":         "X",
            "includeDesc":      "true",
            "subscription-key": self.comtrade_api_key,  # clé en query param
        }

        try:
            r = requests.get(url, params=params, timeout=(15, 60),)
            if r.status_code == 200:
                data = r.json().get("data", [])
                top = sorted(data, key=lambda x: x.get("primaryValue", 0), reverse=True)[:5]
                return {
                    "top_exportateurs": [
                        {
                            "pays":   d.get("reporterDesc", "?"),
                            "valeur_usd": d.get("primaryValue", 0),
                            "annee":  d.get("period", "?"),
                        }
                        for d in top
                    ]
                }
            elif r.status_code == 401:
                return {"error": "Clé API invalide ou expirée."}
            elif r.status_code == 429:
                return {"error": "Quota API dépassé (rate limit)."}
            else:
                return {"error": f"HTTP {r.status_code}", "detail": r.text[:200]}
        except Exception as e:
            return {"error": f"Échec connexion: {e}"}


if __name__ == "__main__":
    # Fix d'encodage pour Terminal Windows
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    agent4 = SupplyChainAgent()
    
    # Simulation de la donnée sortant de l'Agent 1 (Pdf Extraction)
    material_from_agent1 = "Acier inoxydable 316L"
    
    print("="*60)
    print(f"AGENT 4 INFO : MATÉRIAU REÇU DE L'AGENT 1 => '{material_from_agent1}'")
    print("="*60)
    
    result = agent4.analyze_material(material_from_agent1)
    
    print("\n📋 REPORTING FINAL DES FOURNISSEURS :")
    print(json.dumps(result, indent=2, ensure_ascii=False))
