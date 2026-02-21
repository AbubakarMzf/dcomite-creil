"""
Point d'entrée de l'application
Gestion de Tontine - DComité
"""
import sys
import os
import tkinter as tk
from tkinter import messagebox

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DATABASE_PATH, APP_NAME, APP_VERSION
from database.db_manager import DatabaseManager


def main():
    """Point d'entrée de l'application"""
    try:
        print(f"Démarrage de {APP_NAME} v{APP_VERSION}")
        print(f"Base de données: {DATABASE_PATH}")

        # Initialiser la base de données
        db = DatabaseManager(DATABASE_PATH)
        print("Connexion à la base de données établie")

        # Créer les tables si elles n'existent pas
        db.create_tables()
        print("Tables vérifiées/créées")

        # Importer et lancer l'interface (après initialisation DB)
        from ui.main_window import MainWindow

        print("Lancement de l'interface graphique...")

        # Créer et lancer l'interface
        app = MainWindow()
        app.mainloop()

        print("Application fermée")

    except Exception as e:
        error_msg = f"Impossible de démarrer l'application:\n\n{str(e)}"
        print(f"ERREUR: {error_msg}")

        # Afficher un message d'erreur à l'utilisateur
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erreur Critique", error_msg)
        except:
            pass

        sys.exit(1)

    finally:
        # Fermer la connexion DB proprement
        try:
            if 'db' in locals():
                db.close()
                print("Connexion à la base de données fermée")
        except:
            pass


if __name__ == "__main__":
    main()
