import json
import math
import ezdxf
from ezdxf.math import Vec3
import os

def generate_cad(pieces, output_filename="piece_mecanique_2D.dxf"):
    # ================== CONFIGURATION ==================
    doc = ezdxf.new(dxfversion="R2018")
    msp = doc.modelspace()

    # Calques utiles pour la mécanique
    if "Pieces" not in doc.layers:
        doc.layers.add("Pieces", color=1)      # Rouge - Contour des pièces
    if "Axes" not in doc.layers:
        doc.layers.add("Axes", color=5)        # Bleu - Axe central
    if "Text" not in doc.layers:
        doc.layers.add("Text", color=7)        # Blanc - Noms des pièces

    print(f"🔢 {len(pieces)} pièce(s) mécanique(s) à traiter")

    # ================== CRÉATION DES PIÈCES EN 2D ==================
    for piece in pieces:
        name = piece.get('name', 'Piece')
        length = float(piece.get('length', 100))
        width = float(piece.get('width', 50))
        pos = piece.get('position', [0, 0])
        x = float(pos[0])
        y = float(pos[1])
        angle_deg = float(piece.get('angle', 0))
        angle_rad = math.radians(angle_deg)

        # Points du rectangle (vu de dessus)
        half_width = width / 2
        p1 = Vec3(x, y - half_width, 0)
        p2 = Vec3(x + length, y - half_width, 0)
        p3 = Vec3(x + length, y + half_width, 0)
        p4 = Vec3(x, y + half_width, 0)

        # Rotation autour du centre de la pièce
        if abs(angle_rad) > 0.0001:   # évite les erreurs de flottant
            center = Vec3(x + length/2, y, 0)
            m = ezdxf.math.Matrix44.z_rotate(angle_rad)
            p1 = m.transform(p1 - center) + center
            p2 = m.transform(p2 - center) + center
            p3 = m.transform(p3 - center) + center
            p4 = m.transform(p4 - center) + center

        # Conversion en tuple (x, y) obligatoire pour add_lwpolyline
        points = [(p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y), (p4.x, p4.y)]

        # Ajout du contour de la pièce
        msp.add_lwpolyline(
            points,
            close=True,
            dxfattribs={
                'layer': 'Pieces',
                'lineweight': 30   # trait un peu épais
            }
        )

        # Ajout du nom de la pièce (texte)
        text_pos = Vec3(x + length/2, y + width/2 + 10, 0)
        if abs(angle_rad) > 0.0001:
            text_pos = m.transform(text_pos - center) + center

        msp.add_text(
            name,
            dxfattribs={
                'layer': 'Text',
                'height': 15,
                'rotation': angle_deg,
                'insert': (text_pos.x, text_pos.y)
            }
        )

        print(f"Pièce créée : {name} | L={length}mm | W={width}mm | Angle={angle_deg}°")

    # ================== SAUVEGARDE ==================
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    doc.saveas(output_filename)
    return output_filename

if __name__ == "__main__":
    # Fallback/Test mode
    print("Lecture du fichier specs.json en cours...")
    try:
        with open('specs.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        pieces = data.get('pieces', [])
        generate_cad(pieces)
        print("\nFichier DXF 2D sauvegardé : piece_mecanique_2D.dxf")
    except FileNotFoundError:
        print("specs.json non trouvé, passage en mode test.")
        test_pieces = [{"name": "Test Plate", "length": 100, "width": 50, "position": [0,0], "angle": 0}]
        generate_cad(test_pieces)