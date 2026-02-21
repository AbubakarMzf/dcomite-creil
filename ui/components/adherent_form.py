"""
Formulaire d'adhérent (ajout/édition)
Fenêtre modale pour gérer les informations d'un adhérent
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.adherent import Adherent
from datetime import datetime


class AdherentForm(tk.Toplevel):
    """Formulaire modal pour créer/éditer un adhérent"""

    def __init__(self, parent, title, adherent=None):
        super().__init__(parent)

        self.title(title)
        self.geometry("500x600")
        self.resizable(False, False)

        # Centrer la fenêtre
        self.transient(parent)
        self.grab_set()

        self.adherent = adherent  # None pour création, objet Adherent pour édition
        self.result = None  # Résultat du formulaire

        self.setup_ui()
        self.populate_fields()

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
            text="Informations de l'adhérent",
            font=("Arial", 14, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        title_label.pack(pady=(0, 20))

        # Frame pour les champs
        fields_frame = tk.Frame(main_frame, bg='#ECF0F1')
        fields_frame.pack(fill=tk.BOTH, expand=True)

        # Nom (obligatoire)
        self.create_field(
            fields_frame, 0,
            "Nom *", "nom",
            required=True
        )

        # Prénom (obligatoire)
        self.create_field(
            fields_frame, 1,
            "Prénom *", "prenom",
            required=True
        )

        # Téléphone
        self.create_field(
            fields_frame, 2,
            "Téléphone", "telephone"
        )

        # Email
        self.create_field(
            fields_frame, 3,
            "Email", "email"
        )

        # Adresse
        self.create_field(
            fields_frame, 4,
            "Adresse", "adresse"
        )

        # Date d'entrée
        date_frame = tk.Frame(fields_frame, bg='#ECF0F1')
        date_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=10)

        date_label = tk.Label(
            date_frame,
            text="Date d'entrée",
            font=("Arial", 10),
            bg='#ECF0F1',
            fg='#2C3E50',
            anchor='w'
        )
        date_label.pack(anchor='w')

        self.date_entree_entry = tk.Entry(
            date_frame,
            font=("Arial", 10),
            width=30
        )
        self.date_entree_entry.pack(fill=tk.X, pady=(5, 0))
        self.date_entree_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))

        # Statut actif
        self.actif_var = tk.BooleanVar(value=True)
        actif_check = tk.Checkbutton(
            fields_frame,
            text="Adhérent actif",
            variable=self.actif_var,
            font=("Arial", 10),
            bg='#ECF0F1'
        )
        actif_check.grid(row=6, column=0, columnspan=2, sticky='w', pady=10)

        # Notes
        notes_label = tk.Label(
            fields_frame,
            text="Notes",
            font=("Arial", 10),
            bg='#ECF0F1',
            fg='#2C3E50',
            anchor='w'
        )
        notes_label.grid(row=7, column=0, columnspan=2, sticky='w', pady=(10, 5))

        self.notes_text = tk.Text(
            fields_frame,
            font=("Arial", 10),
            height=4,
            width=40
        )
        self.notes_text.grid(row=8, column=0, columnspan=2, sticky='ew', pady=(0, 10))

        # Frame pour les boutons
        buttons_frame = tk.Frame(main_frame, bg='#ECF0F1')
        buttons_frame.pack(fill=tk.X, pady=(20, 0))

        # Bouton Enregistrer
        btn_save = tk.Button(
            buttons_frame,
            text="💾 Enregistrer",
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

    def create_field(self, parent, row, label_text, field_name, required=False):
        """Crée un champ de formulaire"""
        label = tk.Label(
            parent,
            text=label_text,
            font=("Arial", 10),
            bg='#ECF0F1',
            fg='#2C3E50',
            anchor='w'
        )
        label.grid(row=row, column=0, sticky='w', pady=(10, 5))

        entry = tk.Entry(
            parent,
            font=("Arial", 10),
            width=40
        )
        entry.grid(row=row, column=1, sticky='ew', pady=(10, 5))

        # Sauvegarder la référence à l'entry
        setattr(self, f"{field_name}_entry", entry)

    def populate_fields(self):
        """Remplit les champs si on édite un adhérent existant"""
        if not self.adherent:
            return

        # Remplir les champs avec les données de l'adhérent
        self.nom_entry.insert(0, self.adherent.nom)
        self.prenom_entry.insert(0, self.adherent.prenom)

        if self.adherent.telephone:
            self.telephone_entry.insert(0, self.adherent.telephone)

        if self.adherent.email:
            self.email_entry.insert(0, self.adherent.email)

        if self.adherent.adresse:
            self.adresse_entry.insert(0, self.adherent.adresse)

        if self.adherent.date_entree:
            self.date_entree_entry.delete(0, tk.END)
            # Convertir la date si nécessaire
            try:
                date_obj = datetime.strptime(self.adherent.date_entree, '%Y-%m-%d')
                self.date_entree_entry.insert(0, date_obj.strftime('%d/%m/%Y'))
            except:
                self.date_entree_entry.insert(0, self.adherent.date_entree)

        self.actif_var.set(bool(self.adherent.actif))

        if self.adherent.notes:
            self.notes_text.insert('1.0', self.adherent.notes)

    def validate_fields(self):
        """Valide les champs du formulaire"""
        # Nom obligatoire
        nom = self.nom_entry.get().strip()
        if not nom:
            messagebox.showerror("Erreur", "Le nom est obligatoire")
            self.nom_entry.focus()
            return False

        # Prénom obligatoire
        prenom = self.prenom_entry.get().strip()
        if not prenom:
            messagebox.showerror("Erreur", "Le prénom est obligatoire")
            self.prenom_entry.focus()
            return False

        # Valider l'email si présent
        email = self.email_entry.get().strip()
        if email and '@' not in email:
            messagebox.showerror("Erreur", "L'email n'est pas valide")
            self.email_entry.focus()
            return False

        # Valider la date d'entrée
        date_str = self.date_entree_entry.get().strip()
        if date_str:
            try:
                datetime.strptime(date_str, '%d/%m/%Y')
            except ValueError:
                messagebox.showerror(
                    "Erreur",
                    "Le format de la date doit être JJ/MM/AAAA"
                )
                self.date_entree_entry.focus()
                return False

        return True

    def on_save(self):
        """Enregistre l'adhérent"""
        if not self.validate_fields():
            return

        try:
            # Récupérer les valeurs
            nom = self.nom_entry.get().strip()
            prenom = self.prenom_entry.get().strip()
            telephone = self.telephone_entry.get().strip() or None
            email = self.email_entry.get().strip() or None
            adresse = self.adresse_entry.get().strip() or None
            actif = 1 if self.actif_var.get() else 0
            notes = self.notes_text.get('1.0', tk.END).strip() or None

            # Convertir la date d'entrée
            date_str = self.date_entree_entry.get().strip()
            date_entree = None
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
                    date_entree = date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    date_entree = None

            # Créer ou modifier l'adhérent
            if self.adherent:
                # Modification
                self.adherent.update(
                    nom=nom,
                    prenom=prenom,
                    telephone=telephone,
                    email=email,
                    adresse=adresse,
                    date_entree=date_entree,
                    actif=actif,
                    notes=notes
                )
                self.result = self.adherent
            else:
                # Création
                self.result = Adherent.create(
                    nom=nom,
                    prenom=prenom,
                    telephone=telephone,
                    email=email,
                    adresse=adresse,
                    date_entree=date_entree,
                    actif=actif,
                    notes=notes
                )

            self.destroy()

        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Erreur lors de l'enregistrement:\n{str(e)}"
            )

    def on_cancel(self):
        """Annule et ferme le formulaire"""
        self.result = None
        self.destroy()
