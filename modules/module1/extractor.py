import pdfplumber, camelot, pytesseract
from pdf2image import convert_from_path
from PIL import Image
import numpy as np
import cv2

class AdvancedPDFExtractor:
    """Extraction multi-stratégie : texte natif, OCR, tableaux."""

    def extract(self, pdf_path: str) -> dict:
        native  = self._native_text(pdf_path)
        tables  = self._extract_tables(pdf_path)
        
        # Détecte si le PDF est scanné (peu de texte natif)
        if len(native.strip()) < 200:
            native = self._ocr_fallback(pdf_path)
        
        return {"text": native, "tables": tables}

    def _native_text(self, path: str) -> str:
        chunks = []
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                # Filtre les zones de texte techniques (exclut les cartouches)
                words = p.extract_words(
                    extra_attrs=["fontname", "size"],
                    x_tolerance=3
                )
                chunks.append(" ".join(w["text"] for w in words))
        return "\n".join(chunks)

    def _extract_tables(self, path: str) -> list:
        try:
            # camelot pour les tableaux avec bordures (plans DWG)
            tables = camelot.read_pdf(path, pages="all", flavor="lattice")
            return [t.df.to_dict() for t in tables]
        except:
            return []

    def _ocr_fallback(self, path: str) -> str:
        images = convert_from_path(path, dpi=300)
        results = []
        for img in images:
            # Prétraitement : contraste + binarisation
            arr = np.array(img.convert("L"))
            _, bw = cv2.threshold(arr, 0, 255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            text = pytesseract.image_to_string(
                Image.fromarray(bw),
                lang="fra+eng",
                config="--psm 6"
            )
            results.append(text)
        return "\n".join(results)
