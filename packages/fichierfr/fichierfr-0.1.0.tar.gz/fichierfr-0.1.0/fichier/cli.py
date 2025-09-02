import argparse
from fichier import structure, tmp, license
from fichier import perm, clean, dependencies, chmod

def main():
    parser = argparse.ArgumentParser(
        description="Outils pour fichiers",
        epilog="""Exemple mobile : fichier -structure /storage/emulated/0 
        Exemple PC : fichier -structure """
    )
    parser.add_argument(
        "-structure", action="store_true", help="Afficher la structure des fichiers"
    )
    parser.add_argument(
        "-tmp", action="store_true", help="Supprimer tous les fichiers temporaires (*.tmp)"
    )
    parser.add_argument(
        "-license", action="store_true", help="Affiche la LICENSE"
    )
    parser.add_argument(
        "-perm", action="store_true", help="Vérifier les permissions des fichiers"
    )
    parser.add_argument(
        "-clean", action="store_true", help="Supprimer fichiers vides et doublons"
    )
    parser.add_argument(
        "-dependencies", action="store_true", help="Analyser les dépendances"
    )
    parser.add_argument(
        "-chmod", type=str, help="Modifier les permissions (ex: 755, u+x)"
    )
    parser.add_argument(
        "-interactive", action="store_true", help="Mode interactif pour chmod"
    )
    parser.add_argument(
        "directory", nargs="?", default=".", help="Répertoire à traiter (défaut: répertoire courant)"
    )
    args = parser.parse_args()

    # Exécution des fonctions selon les arguments
    if args.structure:
        structure.run(args.directory)
    if args.license:
        license.afficher_licence()
    if args.tmp:
        tmp.delete_tmp(args.directory)
    if args.perm:
        perm.check_permissions(args.directory)
        perm.analyze_permission_issues(args.directory)
    if args.clean:
        clean.clean_directory(args.directory)
    if args.dependencies:
        dependencies.analyze_dependencies(args.directory)
    if args.chmod:
        chmod.change_permissions(args.directory, args.chmod)
    if args.interactive:
        chmod.interactive_chmod(args.directory)

if __name__ == "__main__":
    main()