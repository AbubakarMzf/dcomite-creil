"""
Formulaire de création d'année
Fenêtre modale pour créer une nouvelle année fiscale
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.annee import Annee
from models.adherent import Adherent
from services.contribution_service import ContributionService
from datetime import datetime
from config import CURRENCY_SYMBOL


class AnneeForm(tk.Toplevel):
    """Formulaire modal pour créer une nouvelle année"""

    def __init__(self, parent, title):
        super().__init__(parent)

        self.title(title)
        self.geometry("550x500")
        self.resizable(False, False)

        # Centrer la fenêtre
        self.transient(parent)
        self.grab_set()

        self.result = None  # Résultat du formulaire

        self.setup_ui()
        self.calculate_defaults()

        # Centrer la fenêtre
        self.center_window()

    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """Configure l'interface du formulaire"""
        # Frame principal avec padding
        main_frame = tk.Frame(self, bg='#ECF0F1')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Titre
        title_label = tk.Label(
            main_frame,
            text="Nouvelle année fiscale",
            font=("Arial", 16, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        title_label.pack(pady=(0, 20))

        # Frame pour les champs
        fields_frame = tk.Frame(main_frame, bg='#ECF0F1')
        fields_frame.pack(fill=tk.X, pady=(0, 20))

        # Année (obligatoire)
        self.create_field(
            fields_frame, 0,
            "Année *", "annee",
            hint="Ex: 2025"
        )

        # Balance cible (obligatoire)
        self.create_field(
            fields_frame, 1,
            f"Balance cible ({CURRENCY_SYMBOL}) *", "balance_cible",
            hint="Ex: 500000"
        )

        # Nombre d'adhérents (auto-calculé mais modifiable)
        self.create_field(
            fields_frame, 2,
            "Nombre d'adhérents", "nombre_adherents",
            hint="Auto-calculé (adhérents actifs)"
        )

        # Montant par adhérent (auto-calculé)
        self.montant_label = tk.Label(
            fields_frame,
            text=f"Montant par adhérent: 0 {CURRENCY_SYMBOL}",
            font=("Arial", 11, "bold"),
            bg='#ECF0F1',
            fg='#27AE60'
        )
        self.montant_label.grid(row=3, column=0, columnspan=2, pady=20)

        # Lier les changements pour le calcul automatique
        self.balance_cible_entry.bind('<KeyRelease>', self.calculate_montant)
        self.nombre_adherents_entry.bind('<KeyRelease>', self.calculate_montant)

        # Options
        options_frame = tk.LabelFrame(
            main_frame,
            text="Options",
            font=("Arial", 11, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50',
            padx=15,
            pady=10
        )
        options_frame.pack(fill=tk.X, pady=(0, 20))

        # Activer l'année
        self.activer_var = tk.BooleanVar(value=True)
        activer_check = tk.Checkbutton(
            options_frame,
            text="Activer cette année (désactive les autres années)",
            variable=self.activer_var,
            font=("Arial", 10),
            bg='#ECF0F1'
        )
        activer_check.pack(anchor='w', pady=5)

        # Créer les contributions
        self.creer_contrib_var = tk.BooleanVar(value=True)
        creer_contrib_check = tk.Checkbutton(
            options_frame,
            text="Créer automatiquement les contributions pour les adhérents actifs",
            variable=self.creer_contrib_var,
            font=("Arial", 10),
            bg='#ECF0F1'
        )
        creer_contrib_check.pack(anchor='w', pady=5)

        # Frame pour les boutons
        buttons_frame = tk.Frame(main_frame, bg='#ECF0F1')
        buttons_frame.pack(fill=tk.X, pady=(20, 0))

        # Bouton Créer
        btn_save = tk.Button(
            buttons_frame,
            text="✓ Créer l'année",
            font=("Arial", 11, "bold"),
            bg='#27AE60',
            fg='white',
            padx=20,
            pady=10,
            command=self.on_save
        )
        btn_save.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        # Bouton Annuler
        btn_cancel = tk.Button(
            buttons_frame,
            text="✖ Annuler",
            font=("Arial", 11),
            bg='#95A5A6',
            fg='white',
            padx=20,
            pady=10,
            command=self.on_cancel
        )
        btn_cancel.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))

        # Champs obligatoires
        required_label = tk.Label(
            main_frame,
            text="* Champs obligatoires",
            font=("Arial", 9, "italic"),
            bg='#ECF0F1',
            fg='#7F8C8D'
        )
        required_label.pack(pady=(10, 0))

    def create_field(self, parent, row, label_text, field_name, hint=""):
        """Crée un champ de formulaire"""
        label = tk.Label(
            parent,
            text=label_text,
            font=("Arial", 10, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50',
            anchor='w'
        )
        label.grid(row=row*2, column=0, sticky='w', pady=(10, 5))

        entry = tk.Entry(
            parent,
            font=("Arial", 11),
            width=40
        )
        entry.grid(row=row*2, column=1, sticky='ew', pady=(10, 5))

        if hint:
            hint_label = tk.Label(
                parent,
                text=hint,
                font=("Arial", 9, "italic"),
                bg='#ECF0F1',
                fg='#7F8C8D',
                anchor='w'
            )
            hint_label.grid(row=row*2+1, column=1, sticky='w')

        # Sauvegarder la référence à l'entry
        setattr(self, f"{field_name}_entry", entry)

        parent.grid_columnconfigure(1, weight=1)

    def calculate_defaults(self):
        """Calcule les valeurs par défaut"""
        # Année courante
        current_year = datetime.now().year
        self.annee_entry.insert(0, str(current_year + 1))

        # Nombre d'adhérents actifs
        adherents_actifs = Adherent.get_all(actif_only=True)
        self.nombre_adherents_entry.insert(0, str(len(adherents_actifs)))

    def calculate_montant(self, event=None):
        """Calcule le montant par adhérent"""
        try:
            balance = float(self.balance_cible_entry.get().strip() or 0)
            nombre = int(self.nombre_adherents_entry.get().strip() or 0)

            if nombre > 0:
                montant = balance / nombre
                self.montant_label.config(
                    text=f"Montant par adhérent: {montant:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')
                )
            else:
                self.montant_label.config(text=f"Montant par adhérent: 0 {CURRENCY_SYMBOL}")

        except ValueError:
            self.montant_label.config(text=f"Montant par adhérent: - {CURRENCY_SYMBOL}")

    def validate_fields(self):
        """Valide les champs du formulaire"""
        # Année obligatoire
        annee_str = self.annee_entry.get().strip()
        if not annee_str:
            messagebox.showerror("Erreur", "L'année est obligatoire")
            self.annee_entry.focus()
            return False

        # Année doit être un nombre
        try:
            annee = int(annee_str)
            if annee < 2000 or annee > 2100:
                messagebox.showerror("Erreur", "L'année doit être entre 2000 et 2100")
                self.annee_entry.focus()
                return False
        except ValueError:
            messagebox.showerror("Erreur", "L'année doit être un nombre")
            self.annee_entry.focus()
            return False

        # Vérifier si l'année existe déjà
        existing = Annee.get_by_year(annee)
        if existing:
            messagebox.showerror(
                "Erreur",
                f"L'année {annee} existe déjà dans la base de données"
            )
            self.annee_entry.focus()
            return False

        # Balance cible obligatoire
        balance_str = self.balance_cible_entry.get().strip()
        if not balance_str:
            messagebox.showerror("Erreur", "La balance cible est obligatoire")
            self.balance_cible_entry.focus()
            return False

        # Balance doit être un nombre positif
        try:
            balance = float(balance_str)
            if balance <= 0:
                messagebox.showerror("Erreur", "La balance cible doit être positive")
                self.balance_cible_entry.focus()
                return False
        except ValueError:
            messagebox.showerror("Erreur", "La balance cible doit être un nombre")
            self.balance_cible_entry.focus()
            return False

        # Nombre d'adhérents
        nombre_str = self.nombre_adherents_entry.get().strip()
        try:
            nombre = int(nombre_str) if nombre_str else 0
            if nombre < 0:
                messagebox.showerror("Erreur", "Le nombre d'adhérents doit être positif")
                self.nombre_adherents_entry.focus()
                return False
        except ValueError:
            messagebox.showerror("Erreur", "Le nombre d'adhérents doit être un nombre")
            self.nombre_adherents_entry.focus()
            return False

        return True

    def on_save(self):
        """Enregistre la nouvelle année"""
        if not self.validate_fields():
            return

        try:
            # Récupérer les valeurs
            annee = int(self.annee_entry.get().strip())
            balance_cible = float(self.balance_cible_entry.get().strip())
            nombre_adherents = int(self.nombre_adherents_entry.get().strip() or 0)

            # Créer l'année
            nouvelle_annee = Annee.create(
                annee=annee,
                balance_cible=balance_cible,
                nombre_adherents=nombre_adherents
            )

            # Activer si demandé
            if self.activer_var.get():
                nouvelle_annee.set_active()

            # Créer les contributions si demandé
            if self.creer_contrib_var.get() and nombre_adherents > 0:
                count = ContributionService.creer_contributions_annee(nouvelle_annee.id)
                messagebox.showinfo(
                    "Contributions créées",
                    f"{count} contribution(s) créée(s) pour l'année {annee}"
                )

            self.result = nouvelle_annee
            self.destroy()

        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Erreur lors de la création de l'année:\n{str(e)}"
            )

    def on_cancel(self):
        """Annule et ferme le formulaire"""
        self.result = None
        self.destroy()
