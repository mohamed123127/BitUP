from dotenv import load_dotenv

load_dotenv()

import pdfplumber
from groq import Groq
import json, re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

from modules.module1.prompt import SYSTEM_PROMPT, EXTRACTION_PROMPT


@dataclass
class TechnicalSpec:
    dimensions: dict  # DN, L, H, D, épaisseur…
    materials: list[str]  # corps, joints, fixations
    tolerances: dict  # IT, Ra, planéité…
    pressure: dict  # PN, PS, test
    temperature: dict  # Tmin, Tmax
    confidence: dict  # score par champ 0-1
    source_pages: list[int]  # pages source


class SpecExtractionAgent:
    def __init__(self, model="llama-3.3-70b-versatile"):
        self.client = Groq()
        self.model = model

    def extract_from_pdf(self, pdf_path: str) -> TechnicalSpec:
        # 1. Extraction du texte brut + tableaux avec pdfplumber
        raw_text, tables, pages_used = self._parse_pdf(pdf_path)

        # 2. Appel LLM avec prompt structuré
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=2048,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": EXTRACTION_PROMPT.format(
                        text=raw_text[:8000],
                        tables=json.dumps(tables, ensure_ascii=False),
                    ),
                },
            ],
        )

        # 3. Parse la réponse JSON structurée
        data = json.loads(response.choices[0].message.content)
        return TechnicalSpec(**data, source_pages=pages_used)

    def _parse_pdf(self, path: str):
        text_parts, all_tables, pages = [], [], []
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages):
                t = page.extract_text(x_tolerance=3, y_tolerance=3)
                if t:
                    text_parts.append(t)
                    pages.append(i + 1)
                tbls = page.extract_tables()
                if tbls:
                    all_tables.extend(tbls)
        return "\n".join(text_parts), all_tables, pages


# Utilisation
if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    agent = SpecExtractionAgent()
    specs = agent.extract_from_pdf("pdf_test.pdf")
    print(json.dumps(asdict(specs), indent=2, ensure_ascii=False))
