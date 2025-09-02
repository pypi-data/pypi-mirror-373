import os
import stat
import argparse

def parse_mode(mode_str):
    """Parse le mode chmod (ex: 755, u+x, etc.)"""
    if mode_str.isdigit():
        # Mode octal (ex: 755)
        return int(mode_str, 8)
    else:
        # Mode symbolique (ex: u+x, go-w)
        # Implémentation basique - pour une implémentation complète,
        # il faudrait parser les symboles comme le fait chmod
        print("⚠️  Mode symbolique détecté, utilisation basique")
        if '+' in mode_str:
            return 0o755  # Par défaut
        elif '-' in mode_str:
            return 0o644  # Par défaut
        return 0o644

def change_permissions(directory, mode_str, recursive=False, filter_pattern=None):
    """Change les permissions des fichiers"""
    print(f"🔧 Modification des permissions dans: {directory}")
    print(f"📝 Mode: {mode_str}")
    print("-" * 60)
    
    mode = parse_mode(mode_str)
    changed_count = 0
    
    for root, dirs, files in os.walk(directory):
        for name in files + dirs:
            path = os.path.join(root, name)
            
            # Filtrer par pattern si spécifié
            if filter_pattern and filter_pattern not in name:
                continue
                
            try:
                current_mode = os.stat(path).st_mode
                os.chmod(path, mode)
                new_mode = os.stat(path).st_mode
                
                print(f"✅ {stat.filemode(current_mode)} → {stat.filemode(new_mode)} {path}")
                changed_count += 1
                
            except Exception as e:
                print(f"❌ Erreur avec {path}: {e}")
    
    print(f"\n✅ {changed_count} permissions modifiées")

def interactive_chmod(directory):
    """Mode interactif pour changer les permissions"""
    print("🔧 Mode interactif de modification des permissions")
    
    while True:
        print("\nOptions:")
        print("1. Changer permissions fichiers")
        print("2. Changer permissions répertoires")
        print("3. Quitter")
        
        choice = input("Votre choix: ")
        
        if choice == '3':
            break
        elif choice in ['1', '2']:
            mode_str = input("Mode (ex: 755, 644, u+x): ")
            pattern = input("Filtre par motif (enter pour tous): ") or None
            
            if choice == '1':
                # Fichiers seulement
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if pattern and pattern not in file:
                            continue
                        filepath = os.path.join(root, file)
                        try:
                            os.chmod(filepath, parse_mode(mode_str))
                            print(f"✅ {filepath}")
                        except Exception as e:
                            print(f"❌ {filepath}: {e}")
            else:
                # Répertoires seulement
                for root, dirs, files in os.walk(directory):
                    for dir in dirs:
                        if pattern and pattern not in dir:
                            continue
                        dirpath = os.path.join(root, dir)
                        try:
                            os.chmod(dirpath, parse_mode(mode_str))
                            print(f"✅ {dirpath}")
                        except Exception as e:
                            print(f"❌ {dirpath}: {e}")