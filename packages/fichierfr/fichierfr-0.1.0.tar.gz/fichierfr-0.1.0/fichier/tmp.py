import os

def delete_tmp(directory="."):
    """Supprime tous les fichiers temporaires (*.tmp) dans le répertoire donné et ses sous-dossiers"""
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".tmp"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Supprimé: {file_path}")
                    count += 1
                except Exception as e:
                    print(f"Erreur lors de la suppression de {file_path}: {e}")
    print(f"\nTotal fichiers supprimés: {count}")
