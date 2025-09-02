import os
import hashlib
from pathlib import Path
import time

def remove_empty_files(directory):
    """Supprime les fichiers vides"""
    print("🗑️  Suppression des fichiers vides...")
    empty_count = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            if os.path.getsize(filepath) == 0:
                try:
                    os.remove(filepath)
                    empty_count += 1
                    print(f"  Supprimé: {filepath}")
                except Exception as e:
                    print(f"  ❌ Erreur avec {filepath}: {e}")
    
    print(f"✅ {empty_count} fichiers vides supprimés")
    return empty_count

def remove_empty_dirs(directory):
    """Supprime les répertoires vides"""
    print("🗑️  Suppression des répertoires vides...")
    empty_dirs = 0
    
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir in dirs:
            dirpath = os.path.join(root, dir)
            try:
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
                    empty_dirs += 1
                    print(f"  Supprimé: {dirpath}")
            except Exception as e:
                print(f"  ❌ Erreur avec {dirpath}: {e}")
    
    print(f"✅ {empty_dirs} répertoires vides supprimés")
    return empty_dirs

def find_duplicates(directory):
    """Trouve les fichiers dupliqués"""
    print("🔍 Recherche des fichiers dupliqués...")
    hashes = {}
    duplicates = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                # Ignorer les fichiers vides
                if os.path.getsize(filepath) == 0:
                    continue
                    
                with open(filepath, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                if file_hash in hashes:
                    # Déterminer quel fichier est l'original (le plus ancien)
                    existing_file = hashes[file_hash]
                    existing_mtime = os.path.getmtime(existing_file)
                    current_mtime = os.path.getmtime(filepath)
                    
                    if current_mtime < existing_mtime:
                        # Le fichier courant est plus ancien, c'est l'original
                        duplicates.append({
                            'file1': filepath,          # Original (plus ancien)
                            'file2': existing_file,     # Doublon (plus récent)
                            'original': filepath,
                            'duplicate': existing_file
                        })
                        hashes[file_hash] = filepath  # Mettre à jour l'original
                    else:
                        # Le fichier existant est plus ancien, c'est l'original
                        duplicates.append({
                            'file1': existing_file,     # Original (plus ancien)
                            'file2': filepath,          # Doublon (plus récent)
                            'original': existing_file,
                            'duplicate': filepath
                        })
                else:
                    hashes[file_hash] = filepath
            except Exception as e:
                print(f"  ❌ Erreur avec {filepath}: {e}")
    
    return duplicates

def format_file_time(timestamp):
    """Formate un timestamp en date lisible"""
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

def format_file_size(size):
    """Formate la taille d'un fichier de manière lisible"""
    for unit in ['o', 'Ko', 'Mo', 'Go']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} To"

def confirm_delete_duplicates(duplicates):
    """Demande confirmation pour chaque doublon avec choix de quel fichier supprimer"""
    deleted_count = 0
    
    for i, dup_info in enumerate(duplicates, 1):
        file1 = dup_info['file1']
        file2 = dup_info['file2']
        original = dup_info['original']
        duplicate = dup_info['duplicate']
        
        print(f"\n{'='*60}")
        print(f"📋 DOUBLON {i}/{len(duplicates)}")
        print(f"{'='*60}")
        
        # Informations sur le fichier 1
        file1_size = os.path.getsize(file1)
        file1_mtime = os.path.getmtime(file1)
        print(f"📄 FICHIER 1:")
        print(f"   📁 {file1}")
        print(f"   📊 Taille: {format_file_size(file1_size)}")
        print(f"   📅 Modifié: {format_file_time(file1_mtime)}")
        if file1 == original:
            print(f"   🏷️  CONSIDÉRÉ COMME ORIGINAL (plus ancien)")
        
        # Informations sur le fichier 2
        file2_size = os.path.getsize(file2)
        file2_mtime = os.path.getmtime(file2)
        print(f"\n📄 FICHIER 2:")
        print(f"   📁 {file2}")
        print(f"   📊 Taille: {format_file_size(file2_size)}")
        print(f"   📅 Modifié: {format_file_time(file2_mtime)}")
        if file2 == duplicate:
            print(f"   🏷️  CONSIDÉRÉ COMME DOUBLON (plus récent)")
        
        # Différences
        print(f"\n📊 DIFFÉRENCES:")
        if file1_mtime != file2_mtime:
            if file1_mtime < file2_mtime:
                print(f"   ⏰ Fichier 1 est plus ancien de {(file2_mtime - file1_mtime)/86400:.1f} jours")
            else:
                print(f"   ⏰ Fichier 2 est plus ancien de {(file1_mtime - file2_mtime)/86400:.1f} jours")
        else:
            print(f"   ⏰ Même date de modification")
        
        if file1_size != file2_size:
            print(f"   ❌ Incohérence de taille détectée!")
        else:
            print(f"   ✅ Même taille")
        
        print(f"\n🔧 OPTIONS DE SUPPRESSION:")
        print(f"   1. Supprimer le FICHIER 1 (considéré comme {'ORIGINAL' if file1 == original else 'DOUBLON'})")
        print(f"   2. Supprimer le FICHIER 2 (considéré comme {'ORIGINAL' if file2 == original else 'DOUBLON'})")
        print(f"   3. Conserver les DEUX fichiers")
        print(f"   4. Arrêter le processus")
        
        while True:
            try:
                choice = input("\nVotre choix (1-4): ").strip()
                if choice == '1':
                    file_to_delete = file1
                    file_to_keep = file2
                    break
                elif choice == '2':
                    file_to_delete = file2
                    file_to_keep = file1
                    break
                elif choice == '3':
                    print(f"➖ Les deux fichiers conservés: {file1} et {file2}")
                    file_to_delete = None
                    break
                elif choice == '4':
                    print("⏹️  Arrêt de la suppression...")
                    return deleted_count
                else:
                    print("❌ Choix invalide. Veuillez choisir 1, 2, 3 ou 4.")
            except (ValueError, KeyboardInterrupt):
                print("❌ Choix invalide. Veuillez choisir 1, 2, 3 ou 4.")
        
        if file_to_delete:
            # Confirmation finale
            confirm = input(f"Êtes-vous sûr de vouloir supprimer '{os.path.basename(file_to_delete)}'? (o/n): ").lower()
            if confirm == 'o':
                try:
                    os.remove(file_to_delete)
                    deleted_count += 1
                    print(f"✅ SUPPRIMÉ: {file_to_delete}")
                    print(f"✅ CONSERVÉ: {file_to_keep}")
                except Exception as e:
                    print(f"❌ ERREUR lors de la suppression: {e}")
            else:
                print(f"➖ Fichier conservé: {file_to_delete}")
    
    return deleted_count

def clean_directory(directory):
    """Nettoie le répertoire des fichiers vides et doublons"""
    print(f"🧹 NETTOYAGE DU RÉPERTOIRE: {directory}")
    print("=" * 60)
    
    # Supprimer les fichiers vides (automatique)
    print("\n" + "=" * 30)
    print("PHASE 1: FICHIERS VIDES")
    print("=" * 30)
    empty_files = remove_empty_files(directory)
    
    # Supprimer les répertoires vides (automatique)
    print("\n" + "=" * 30)
    print("PHASE 2: RÉPERTOIRES VIDES")
    print("=" * 30)
    empty_dirs = remove_empty_dirs(directory)
    
    # Trouver et gérer les doublons
    print("\n" + "=" * 30)
    print("PHASE 3: DOUBLONS")
    print("=" * 30)
    duplicates = find_duplicates(directory)
    
    deleted_duplicates = 0
    if duplicates:
        print(f"🔍 {len(duplicates)} paires de doublons trouvées")
        
        # Aperçu des doublons
        print("\n📋 APERÇU DES DOUBLONS:")
        for i, dup_info in enumerate(duplicates[:3], 1):
            file1 = dup_info['file1']
            file2 = dup_info['file2']
            print(f"  {i}. {os.path.basename(file1)} ↔ {os.path.basename(file2)}")
        if len(duplicates) > 3:
            print(f"  ... et {len(duplicates) - 3} autres paires")
        
        # Demander confirmation globale
        global_confirm = input("\nVoulez-vous examiner chaque paire de doublons? (o/n): ").lower()
        
        if global_confirm == 'o':
            deleted_duplicates = confirm_delete_duplicates(duplicates)
            print(f"\n✅ {deleted_duplicates} fichiers supprimés sur {len(duplicates)} paires")
        else:
            print("➖ Aucun doublon supprimé")
    else:
        print("✅ Aucun doublon trouvé")
    
    # Résumé final
    print("\n" + "=" * 60)
    print("🎯 RÉSUMÉ DU NETTOYAGE")
    print("=" * 60)
    print(f"📊 Fichiers vides supprimés:    {empty_files}")
    print(f"📊 Répertoires vides supprimés: {empty_dirs}")
    print(f"📊 Doublons supprimés:          {deleted_duplicates}")
    print(f"📊 Paires de doublons:          {len(duplicates)}")
    print("=" * 60)
    
    total_freed = empty_files + empty_dirs + deleted_duplicates
    print(f"🚀 TOTAL: {total_freed} éléments nettoyés")