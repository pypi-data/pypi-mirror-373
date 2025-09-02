import os
import stat
from pathlib import Path

def check_permissions(directory):
    """
    Vérifie et affiche les permissions des fichiers dans un répertoire
    """
    print(f"🔐 Vérification des permissions dans: {directory}")
    print("-" * 60)
    
    for root, dirs, files in os.walk(directory):
        for name in files + dirs:
            path = os.path.join(root, name)
            try:
                st = os.stat(path)
                perms = stat.filemode(st.st_mode)
                size = os.path.getsize(path) if os.path.isfile(path) else "-"
                print(f"{perms} {size:8} {path}")
            except Exception as e:
                print(f"❌ Erreur avec {path}: {e}")

def analyze_permission_issues(directory):
    """
    Analyse les problèmes de permissions courants
    """
    print(f"\n🔍 Analyse des problèmes de permissions dans: {directory}")
    issues = []
    
    for root, dirs, files in os.walk(directory):
        for name in files:
            path = os.path.join(root, name)
            try:
                st = os.stat(path)
                
                # Fichiers exécutables sans droit de lecture
                if st.st_mode & stat.S_IEXEC and not st.st_mode & stat.S_IREAD:
                    issues.append(f"Fichier exécutable sans lecture: {path}")
                
                # Fichiers avec permissions trop ouvertes
                if st.st_mode & stat.S_IROTH and st.st_mode & stat.S_IWOTH:
                    issues.append(f"Permissions trop ouvertes (rw pour tous): {path}")
                    
            except Exception as e:
                issues.append(f"Erreur d'accès: {path} - {e}")
    
    if issues:
        print("Problèmes détectés:")
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("✅ Aucun problème de permission détecté")