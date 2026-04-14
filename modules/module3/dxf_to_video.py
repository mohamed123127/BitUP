"""
Nom du fichier : dxf_to_video_manim.py
Description : Importation d'un fichier DXF et production d'une vidéo HD avec Manim
Utilisation : manim -pqh dxf_to_video_manim.py PieceMecanique
"""

import ezdxf
from manim import *
import numpy as np

# ==============================================
# Paramètres que vous pouvez modifier facilement
# ==============================================

DXF_INPUT = "piece.dxf"  # Chemin de votre fichier DXF
DURATION_SECONDS = 5
RESOLUTION_X = 1920
RESOLUTION_Y = 1080
FPS = 30

# ==============================================
# Classe principale Manim
# ==============================================

class PieceMecanique(ThreeDScene):
    def construct(self):
        # Titre
        titre = Text("Pièce Mécanique 2D", font_size=48, color=BLUE)
        self.play(Write(titre))
        self.wait(0.5)
        self.play(FadeOut(titre))
        
        # Lire le fichier DXF
        print("📂 Lecture du fichier DXF...")
        try:
            doc = ezdxf.readfile(DXF_INPUT)
            msp = doc.modelspace()
        except Exception as e:
            error_text = Text(f"Erreur: {e}", color=RED, font_size=24)
            self.add(error_text)
            self.wait(2)
            return
        
        # Créer un groupe pour tous les éléments
        dessin = VGroup()
        
        # Variables pour normalisation
        all_points = []
        
        # Première passe : collecter tous les points
        for entity in msp:
            if entity.dxftype() == 'LWPOLYLINE':
                points = list(entity.get_points())
                for x, y, *_ in points:
                    all_points.append([x, y])
            elif entity.dxftype() == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
                all_points.append([start.x, start.y])
                all_points.append([end.x, end.y])
            elif entity.dxftype() == 'CIRCLE':
                center = entity.dxf.center
                radius = entity.dxf.radius
                all_points.append([center.x, center.y])
                all_points.append([center.x + radius, center.y + radius])
            elif entity.dxftype() == 'ARC':
                center = entity.dxf.center
                radius = entity.dxf.radius
                all_points.append([center.x, center.y])
                all_points.append([center.x + radius, center.y + radius])
        
        if not all_points:
            error_text = Text("Aucune entité trouvée dans le DXF", color=RED)
            self.add(error_text)
            self.wait(2)
            return
        
        # Normaliser les coordonnées
        all_points = np.array(all_points)
        min_x, min_y = all_points.min(axis=0)
        max_x, max_y = all_points.max(axis=0)
        
        width = max_x - min_x
        height = max_y - min_y
        
        if width == 0:
            width = 1
        if height == 0:
            height = 1
        
        scale_factor = min(6 / width, 4 / height) if width > 0 and height > 0 else 1
        
        def normaliser(x, y):
            nx = (x - min_x - width/2) * scale_factor
            ny = (y - min_y - height/2) * scale_factor
            return np.array([nx, ny, 0])
        
        # Deuxième passe : créer les objets Manim
        for entity in msp:
            if entity.dxftype() == 'LWPOLYLINE':
                points = list(entity.get_points())
                if len(points) >= 2:
                    pts = [normaliser(x, y) for x, y, *_ in points]
                    
                    # Vérifier si c'est fermé
                    if entity.closed:
                        pts.append(pts[0])
                    
                    for i in range(len(pts) - 1):
                        ligne = Line(pts[i], pts[i+1], color=BLUE, stroke_width=4)
                        dessin.add(ligne)
            
            elif entity.dxftype() == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
                p1 = normaliser(start.x, start.y)
                p2 = normaliser(end.x, end.y)
                ligne = Line(p1, p2, color=BLUE, stroke_width=4)
                dessin.add(ligne)
            
            elif entity.dxftype() == 'CIRCLE':
                center = entity.dxf.center
                radius = entity.dxf.radius
                c = normaliser(center.x, center.y)
                r = radius * scale_factor
                cercle = Circle(radius=r, color=RED, stroke_width=4)
                cercle.move_to(c)
                dessin.add(cercle)
            
            elif entity.dxftype() == 'ARC':
                center = entity.dxf.center
                radius = entity.dxf.radius
                start_angle = entity.dxf.start_angle * np.pi / 180
                end_angle = entity.dxf.end_angle * np.pi / 180
                
                c = normaliser(center.x, center.y)
                r = radius * scale_factor
                
                arc = Arc(
                    radius=r,
                    start_angle=start_angle,
                    angle=end_angle - start_angle,
                    color=GREEN,
                    stroke_width=4
                )
                arc.move_to(c)
                dessin.add(arc)
        
        # Ajouter le dessin à la scène
        self.play(Create(dessin), run_time=2)
        self.wait(0.5)
        
        # Animation de rotation 3D
        print("🎬 Ajout d'une rotation 3D...")
        self.move_camera(
            phi=60 * DEGREES,
            theta=-45 * DEGREES,
            run_time=2
        )
        self.wait(0.5)
        
        # Rotation complète
        self.begin_ambient_camera_rotation(rate=0.3)
        self.wait(DURATION_SECONDS)
        self.stop_ambient_camera_rotation()
        
        # Zoom final
        self.move_camera(
            zoom=1.5,
            run_time=1
        )
        self.wait(0.5)


# ==============================================
# Configuration de la qualité vidéo
# ==============================================
config.pixel_height = RESOLUTION_Y
config.pixel_width = RESOLUTION_X
config.frame_rate = FPS
config.output_file = "Piece_Mecanique"
config.quality = "high_quality"