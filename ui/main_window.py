"""
Fenêtre principale de l'application
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT
from models.annee import Annee


class MainWindow(tk.Tk):
    """Fenêtre principale de l'application"""

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # Centrer la fenêtre
        self.center_window()

        # Configuration du style
        self.configure(bg='#ECF0F1')

        # Variables
        self.current_view = None
        self.annee_active = None

        # Récupérer l'année active
        self.load_annee_active()

        # Configurer l'interface
        self.setup_menu()
        self.setup_header()
        self.setup_main_area()
        self.setup_status_bar()

        # Afficher le dashboard au démarrage
        self.show_dashboard()

        # Gérer la fermeture
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def load_annee_active(self):
        """Charge l'année active"""
        try:
            self.annee_active = Annee.get_active()
            if not self.annee_active:
                # Créer une année par défaut si aucune n'existe
                from datetime import datetime
                annee_courante = datetime.now().year
                messagebox.showwarning(
                    "Aucune année active",
                    f"Aucune année active trouvée.\n"
                    f"Veuillez créer une nouvelle année via le menu Année."
                )
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement de l'année active:\n{str(e)}")

    def setup_menu(self):
        """Configure la barre de menu"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Menu Fichier
        menu_fichier = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=menu_fichier)
        menu_fichier.add_command(label="Backup Base de données", command=self.backup_database)
        menu_fichier.add_separator()
        menu_fichier.add_command(label="Quitter", command=self.on_closing)

        # Menu Adhérents
        menu_adherents = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Adhérents", menu=menu_adherents)
        menu_adherents.add_command(label="Gérer les adhérents", command=self.show_adherents)
        menu_adherents.add_command(label="Ajouter un adhérent", command=self.add_adherent)

        # Menu Année
        menu_annee = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Année", menu=menu_annee)
        menu_annee.add_command(label="Nouvelle année", command=self.new_annee)
        menu_annee.add_command(label="Gérer les années", command=self.show_annees)

        # Menu Contributions
        menu_contributions = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Contributions", menu=menu_contributions)
        menu_contributions.add_command(label="Enregistrer un paiement", command=self.show_contributions)

        # Menu Dépenses
        menu_depenses = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dépenses", menu=menu_depenses)
        menu_depenses.add_command(label="Enregistrer une dépense", command=self.show_depenses)

        # Menu Rapports
        menu_rapports = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Rapports", menu=menu_rapports)
        menu_rapports.add_command(label="Rapport annuel", command=self.show_rapport_annuel)
        menu_rapports.add_command(label="Rapport par adhérent", command=self.show_rapport_adherent)
        menu_rapports.add_separator()
        menu_rapports.add_command(label="Adhérents non payés", command=self.show_rapport_non_payes)

        # Menu Aide
        menu_aide = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=menu_aide)
        menu_aide.add_command(label="À propos", command=self.show_about)

    def setup_header(self):
        """Configure l'en-tête avec informations de l'année active"""
        header_frame = tk.Frame(self, bg='#2C3E50', height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        # Titre
        title_label = tk.Label(
            header_frame,
            text=APP_NAME,
            font=("Arial", 16, "bold"),
            bg='#2C3E50',
            fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)

        # Année active
        self.annee_label = tk.Label(
            header_frame,
            text="",
            font=("Arial", 12),
            bg='#2C3E50',
            fg='#3498DB'
        )
        self.annee_label.pack(side=tk.RIGHT, padx=20, pady=10)
        self.update_annee_label()

    def update_annee_label(self):
        """Met à jour l'affichage de l'année active"""
        if self.annee_active:
            self.annee_label.config(
                text=f"Année active: {self.annee_active.annee}"
            )
        else:
            self.annee_label.config(
                text="Aucune année active"
            )

    def setup_main_area(self):
        """Configure la zone principale de contenu"""
        self.main_container = tk.Frame(self, bg='#ECF0F1')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def setup_status_bar(self):
        """Configure la barre de statut"""
        status_frame = tk.Frame(self, bg='#BDC3C7', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(
            status_frame,
            text="Prêt",
            bg='#BDC3C7',
            fg='#2C3E50',
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)

    def update_status(self, message):
        """Met à jour le message de la barre de statut"""
        self.status_label.config(text=message)

    def clear_main_area(self):
        """Efface le contenu de la zone principale"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
        self.current_view = None

    def show_dashboard(self):
        """Affiche le tableau de bord"""
        self.clear_main_area()
        from ui.components.dashboard import Dashboard
        self.current_view = Dashboard(self.main_container, self)
        self.current_view.pack(fill=tk.BOTH, expand=True)
        self.update_status("Tableau de bord")

    def show_adherents(self):
        """Affiche la vue de gestion des adhérents"""
        self.clear_main_area()
        from ui.views.adherents_view import AdherentsView
        self.current_view = AdherentsView(self.main_container, self)
        self.current_view.pack(fill=tk.BOTH, expand=True)
        self.update_status("Gestion des adhérents")

    def add_adherent(self):
        """Ouvre le formulaire d'ajout d'adhérent"""
        from ui.components.adherent_form import AdherentForm
        form = AdherentForm(self, "Ajouter un adhérent")
        self.wait_window(form)

        if form.result:
            messagebox.showinfo("Succès", "Adhérent ajouté avec succès")
            # Rafraîchir la vue si on est sur la page adhérents
            if hasattr(self.current_view, '__class__') and \
               self.current_view.__class__.__name__ == 'AdherentsView':
                self.current_view.load_adherents()

    def show_annees(self):
        """Affiche la vue de gestion des années"""
        self.clear_main_area()
        from ui.views.annees_view import AnneesView
        self.current_view = AnneesView(self.main_container, self)
        self.current_view.pack(fill=tk.BOTH, expand=True)
        self.update_status("Gestion des années")

    def new_annee(self):
        """Ouvre le formulaire de nouvelle année"""
        from ui.components.annee_form import AnneeForm
        form = AnneeForm(self, "Nouvelle année")
        self.wait_window(form)

        if form.result:
            self.refresh_annee_active()
            messagebox.showinfo("Succès", "Année créée avec succès")
            # Rafraîchir la vue si on est sur la page années
            if hasattr(self.current_view, '__class__') and \
               self.current_view.__class__.__name__ == 'AnneesView':
                self.current_view.load_annees()

    def show_contributions(self):
        """Affiche la vue d'enregistrement des contributions"""
        self.clear_main_area()
        from ui.views.contributions_view import ContributionsView
        self.current_view = ContributionsView(self.main_container, self)
        self.current_view.pack(fill=tk.BOTH, expand=True)
        self.update_status("Enregistrement des contributions")

    def show_depenses(self):
        """Affiche la vue d'enregistrement des dépenses"""
        self.clear_main_area()
        from ui.views.depenses_view import DepensesView
        self.current_view = DepensesView(self.main_container, self)
        self.current_view.pack(fill=tk.BOTH, expand=True)
        self.update_status("Enregistrement des dépenses")

    def show_rapport_annuel(self):
        """Affiche le rapport annuel"""
        messagebox.showinfo("Info", "Fonctionnalité à venir: Rapport annuel")

    def show_rapport_adherent(self):
        """Affiche le rapport par adhérent"""
        messagebox.showinfo("Info", "Fonctionnalité à venir: Rapport par adhérent")

    def show_rapport_non_payes(self):
        """Affiche le rapport des adhérents non payés"""
        messagebox.showinfo("Info", "Fonctionnalité à venir: Rapport non payés")

    def show_about(self):
        """Affiche la fenêtre À propos"""
        from config import APP_VERSION
        messagebox.showinfo(
            "À propos",
            f"{APP_NAME}\n"
            f"Version {APP_VERSION}\n\n"
            f"Death Comitee\n"
            f"pour les décès et solidarité familiale."
        )

    def backup_database(self):
        """Crée une sauvegarde de la base de données"""
        try:
            from database.db_manager import DatabaseManager
            db = DatabaseManager()
            backup_path = db.backup_database()
            messagebox.showinfo(
                "Backup réussi",
                f"Sauvegarde créée avec succès:\n{backup_path}"
            )
            self.update_status(f"Backup créé: {backup_path}")
        except Exception as e:
            messagebox.showerror(
                "Erreur de backup",
                f"Impossible de créer la sauvegarde:\n{str(e)}"
            )

    def refresh_annee_active(self):
        """Recharge l'année active"""
        self.load_annee_active()
        self.update_annee_label()

        # Rafraîchir la vue actuelle si c'est le dashboard
        if isinstance(self.current_view, type(None)) or \
           hasattr(self.current_view, '__class__') and \
           self.current_view.__class__.__name__ == 'Dashboard':
            self.show_dashboard()

    def on_closing(self):
        """Gère la fermeture de l'application"""
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application?"):
            self.destroy()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
