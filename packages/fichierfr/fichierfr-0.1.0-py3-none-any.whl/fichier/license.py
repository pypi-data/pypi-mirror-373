import os
from pathlib import Path

def afficher_licence():
    """Affiche le contenu du fichier LICENSE depuis la racine du package"""
    try:
        # Chercher le fichier LICENSE dans le dossier parent
        license_path = Path(__file__).parent.parent / "LICENSE"
        
        if license_path.exists():
            with open(license_path, "r", encoding="utf-8") as f:
                contenu = f.read()
            print(contenu)
        else:
            print("❌ Fichier LICENSE introuvable dans le package")
            print("ℹ️  Placez un fichier LICENSE à la racine du projet")
            
    except Exception as e:
        print(f"❌ Erreur lecture licence: {e}")

def afficher_licence_courte():
    """Affiche une version courte et stylée de la licence"""
    licence_courte = """
╔══════════════════════════════════════════════════════════════╗
║                 LICENCE PROPRIÉTAIRE                        ║
║                 TOUS DROITS RÉSERVÉS                        ║
╠══════════════════════════════════════════════════════════════╣
║ 🚫 COMMERCIALISATION INTERDITE                              ║
║ 🚫 MODIFICATION INTERDITE                                   ║
║ 🚫 DISTRIBUTION COMMERCIALE INTERDITE                       ║
║                                                              ║
║ ✅ Usage personnel autorisé                                 ║
║ ✅ Partage non-commercial autorisé                          ║
║ ✅ Étude éducative autorisée                                ║
║                                                              ║
║ 📧 Contact: [VOTRE@EMAIL.COM]                               ║
║ ⚖️ Violation: Poursuites judiciaires                        ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(licence_courte)