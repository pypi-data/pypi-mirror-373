import os
import re
from pathlib import Path

def analyze_imports(filepath):
    """Analyse les imports d'un fichier Python"""
    imports = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Recherche des imports
        import_patterns = [
            r'^import\s+(\w+)',
            r'^from\s+(\w+)\s+import',
            r'^import\s+(\w+\.\w+)',
            r'^from\s+(\w+\.\w+)\s+import'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            imports.update(matches)
            
    except Exception as e:
        print(f"  ❌ Erreur avec {filepath}: {e}")
    
    return imports

def analyze_dependencies(directory):
    """Analyse les dépendances du projet"""
    print(f"📦 Analyse des dépendances dans: {directory}")
    print("-" * 60)
    
    all_imports = set()
    python_files = []
    
    # Trouver tous les fichiers Python
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"📁 {len(python_files)} fichiers Python trouvés")
    
    # Analyser chaque fichier
    for filepath in python_files:
        imports = analyze_imports(filepath)
        all_imports.update(imports)
        if imports:
            print(f"\n📄 {filepath}:")
            for imp in sorted(imports):
                print(f"  import {imp}")
    
    # Dépendances externes probables (non standards)
    stdlib_modules = [
        'os', 'sys', 're', 'json', 'math', 'datetime', 'collections',
        'pathlib', 'argparse', 'stat', 'hashlib', 'itertools', 'functools'
    ]
    
    external_deps = [imp for imp in all_imports if imp.split('.')[0] not in stdlib_modules]
    
    print(f"\n🔍 Dépendances externes probables:")
    for dep in sorted(external_deps):
        print(f"  📦 {dep}")
    
    # Vérifier les requirements.txt
    requirements_path = os.path.join(directory, 'requirements.txt')
    if os.path.exists(requirements_path):
        print(f"\n📋 Contenu de requirements.txt:")
        with open(requirements_path, 'r') as f:
            print(f.read())
    else:
        print(f"\n❌ requirements.txt non trouvé")

def generate_requirements(directory):
    """Génère un fichier requirements.txt basé sur les imports"""
    print("🛠️  Génération du fichier requirements.txt...")
    
    all_imports = set()
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                imports = analyze_imports(filepath)
                all_imports.update(imports)
    
    # Filtrer les modules standards
    stdlib_modules = [
        'os', 'sys', 're', 'json', 'math', 'datetime', 'collections',
        'pathlib', 'argparse', 'stat', 'hashlib', 'itertools', 'functools'
    ]
    
    external_deps = [imp.split('.')[0] for imp in all_imports 
                    if imp.split('.')[0] not in stdlib_modules]
    
    # Écrire le fichier requirements.txt
    requirements_path = os.path.join(directory, 'requirements.txt')
    with open(requirements_path, 'w') as f:
        for dep in sorted(set(external_deps)):
            f.write(f"{dep}>=1.0.0\n")
    
    print(f"✅ requirements.txt généré avec {len(set(external_deps))} dépendances")