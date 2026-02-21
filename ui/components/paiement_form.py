"""
Formulaire de paiement
Enregistrement d'un paiement de contribution
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from config import PAYMENT_MODES, CURRENCY_SYMBOL, ADMIN_IDS
from models.contribution import Contribution


class PaiementForm(tk.Toplevel):
    """Formulaire d'enregistrement de paiement"""

    def __init__(self, parent, adherent):
        super().__init__(parent)

        self.title(f"Paiement - {adherent.get_nom_complet()}")
        self.geometry("450x650")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.adherent = adherent
        self.result = None

        self.setup_ui()
        self.center_window()

    def center_window(self):
        """Centre la fenetre"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        """Configure l'interface"""
        main_frame = tk.Frame(self, bg='#ECF0F1')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Titre
        title_label = tk.Label(
            main_frame,
            text=f"{self.adherent.get_nom_complet()}",
            font=("Arial", 14, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        title_label.pack(pady=(0, 20))

        # Informations adherent
        info_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, borderwidth=1)
        info_frame.pack(fill=tk.X, pady=(0, 20))

        info_content = tk.Frame(info_frame, bg='white')
        info_content.pack(padx=15, pady=15)

        # Calculer le total deja paye cette annee
        annee_courante = datetime.now().year
        total_paye = Contribution.get_total_by_adherent(self.adherent.id, annee_courante)

        infos = [
            ("Adherent", self.adherent.get_nom_complet()),
            ("Total paye en " + str(annee_courante), f"{total_paye:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')),
        ]

        for label, value in infos:
            row = tk.Frame(info_content, bg='white')
            row.pack(fill=tk.X, pady=2)

            label_widget = tk.Label(
                row,
                text=f"{label}:",
                font=("Arial", 10, "bold"),
                bg='white',
                fg='#7F8C8D',
                anchor='w',
                width=20
            )
            label_widget.pack(side=tk.LEFT)

            value_widget = tk.Label(
                row,
                text=value,
                font=("Arial", 10),
                bg='white',
                fg='#2C3E50',
                anchor='w'
            )
            value_widget.pack(side=tk.LEFT)

        # Formulaire
        form_frame = tk.Frame(main_frame, bg='#ECF0F1')
        form_frame.pack(fill=tk.X)

        # Montant
        tk.Label(
            form_frame,
            text=f"Montant du paiement ({CURRENCY_SYMBOL}) *",
            font=("Arial", 10, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 5))

        self.montant_entry = tk.Entry(
            form_frame,
            font=("Arial", 12),
            width=20
        )
        self.montant_entry.pack(fill=tk.X, pady=(0, 10))
        self.montant_entry.focus()

        # Date
        tk.Label(
            form_frame,
            text="Date de paiement *",
            font=("Arial", 10, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 5))

        self.date_entry = tk.Entry(
            form_frame,
            font=("Arial", 12)
        )
        self.date_entry.pack(fill=tk.X, pady=(0, 10))
        self.date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))

        # Mode de paiement
        tk.Label(
            form_frame,
            text="Mode de paiement",
            font=("Arial", 10, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 5))

        self.mode_var = tk.StringVar(value=PAYMENT_MODES[0])
        mode_combo = ttk.Combobox(
            form_frame,
            textvariable=self.mode_var,
            values=PAYMENT_MODES,
            font=("Arial", 12),
            state='readonly'
        )
        mode_combo.pack(fill=tk.X, pady=(0, 10))

        # Admin
        tk.Label(
            form_frame,
            text="Enregistre par *",
            font=("Arial", 10, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 5))

        # Liste des admins pour le combobox
        admin_values = [f"{id} - {name}" for id, name in ADMIN_IDS.items()]
        self.admin_var = tk.StringVar(value=admin_values[0])
        admin_combo = ttk.Combobox(
            form_frame,
            textvariable=self.admin_var,
            values=admin_values,
            font=("Arial", 12),
            state='readonly'
        )
        admin_combo.pack(fill=tk.X, pady=(0, 10))

        # Reference
        tk.Label(
            form_frame,
            text="Reference (n cheque, transaction, etc.)",
            font=("Arial", 10),
            bg='#ECF0F1',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 5))

        self.reference_entry = tk.Entry(
            form_frame,
            font=("Arial", 12)
        )
        self.reference_entry.pack(fill=tk.X, pady=(0, 10))

        # Notes
        tk.Label(
            form_frame,
            text="Notes",
            font=("Arial", 10),
            bg='#ECF0F1',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 5))

        self.notes_text = tk.Text(
            form_frame,
            font=("Arial", 10),
            height=3
        )
        self.notes_text.pack(fill=tk.X, pady=(0, 10))

        # Boutons
        buttons_frame = tk.Frame(main_frame, bg='#ECF0F1')
        buttons_frame.pack(fill=tk.X, pady=(20, 0))

        btn_save = tk.Button(
            buttons_frame,
            text="Enregistrer",
            font=("Arial", 11, "bold"),
            bg='#27AE60',
            fg='white',
            padx=20,
            pady=10,
            command=self.on_save
        )
        btn_save.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        btn_cancel = tk.Button(
            buttons_frame,
            text="Annuler",
            font=("Arial", 11),
            bg='#95A5A6',
            fg='white',
            padx=20,
            pady=10,
            command=self.on_cancel
        )
        btn_cancel.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))

    def validate_fields(self):
        """Valide les champs"""
        # Montant
        montant_str = self.montant_entry.get().strip()
        if not montant_str:
            messagebox.showerror("Erreur", "Le montant est obligatoire")
            self.montant_entry.focus()
            return False

        try:
            montant = float(montant_str)
            if montant <= 0:
                messagebox.showerror("Erreur", "Le montant doit etre positif")
                self.montant_entry.focus()
                return False
        except ValueError:
            messagebox.showerror("Erreur", "Le montant doit etre un nombre")
            self.montant_entry.focus()
            return False

        # Date
        date_str = self.date_entry.get().strip()
        if not date_str:
            messagebox.showerror("Erreur", "La date est obligatoire")
            self.date_entry.focus()
            return False

        try:
            datetime.strptime(date_str, '%d/%m/%Y')
        except ValueError:
            messagebox.showerror("Erreur", "Format de date invalide (JJ/MM/AAAA)")
            self.date_entry.focus()
            return False

        return True

    def on_save(self):
        """Enregistre le paiement"""
        if not self.validate_fields():
            return

        try:
            montant = float(self.montant_entry.get().strip())
            date_str = self.date_entry.get().strip()
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            date_paiement = date_obj.strftime('%Y-%m-%d')

            mode = self.mode_var.get()
            reference = self.reference_entry.get().strip() or None
            notes = self.notes_text.get('1.0', tk.END).strip() or None

            # Extraire l'ID admin (premier caractere avant le tiret)
            admin_str = self.admin_var.get()
            admin_id = int(admin_str.split(' - ')[0])

            # Creer la contribution (paiement)
            contribution = Contribution.create(
                adherent_id=self.adherent.id,
                montant=montant,
                date_paiement=date_paiement,
                mode_paiement=mode,
                reference_paiement=reference,
                admin_id=admin_id,
                notes=notes
            )

            # Generer le PDF
            try:
                from services.pdf_service import PdfService
                PdfService.generer_pdf_paiement(contribution)
            except Exception as pdf_err:
                messagebox.showwarning(
                    "PDF",
                    f"Le paiement a ete enregistre mais le PDF n'a pas pu etre genere:\n{str(pdf_err)}"
                )

            self.result = True
            self.destroy()

        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Erreur lors de l'enregistrement:\n{str(e)}"
            )

    def on_cancel(self):
        """Annule"""
        self.result = None
        self.destroy()
