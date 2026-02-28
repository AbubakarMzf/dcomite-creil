"""
Formulaire de paiement
Enregistrement d'un paiement : cotisation ou frais d'entree
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from config import PAYMENT_MODES, CURRENCY_SYMBOL, ADMIN_IDS
from models.contribution import Contribution
from models.cotisation import Cotisation
from models.historique import Historique

MOTIFS = ["Cotisation", "Frais d'entree"]


class PaiementForm(tk.Toplevel):
    """Formulaire d'enregistrement de paiement"""

    def __init__(self, parent, adherent):
        super().__init__(parent)

        self.title(f"Paiement - {adherent.get_nom_complet()}")
        self.geometry("480x780")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.adherent = adherent
        self.result = None
        self._cotisations_impayees = []

        self.setup_ui()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ui(self):
        main_frame = tk.Frame(self, bg='#ECF0F1')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Titre
        tk.Label(
            main_frame,
            text=self.adherent.get_nom_complet(),
            font=("Arial", 14, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        ).pack(pady=(0, 10))

        # Bloc info adherent
        info_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, borderwidth=1)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        info_content = tk.Frame(info_frame, bg='white')
        info_content.pack(padx=15, pady=10)

        annee_courante = datetime.now().year
        total_paye = Contribution.get_total_by_adherent(self.adherent.id, annee_courante)
        infos = [
            ("Total paye en " + str(annee_courante),
             f"{total_paye:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')),
        ]
        if self.adherent.frais_entree > 0:
            statut_frais = "Paye" if self.adherent.frais_entree_paye else "Non paye"
            infos.append((
                "Frais d'entree",
                f"{self.adherent.frais_entree:,.0f} {CURRENCY_SYMBOL} ({statut_frais})".replace(',', ' ')
            ))

        for label, value in infos:
            row = tk.Frame(info_content, bg='white')
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"{label}:", font=("Arial", 10, "bold"),
                     bg='white', fg='#7F8C8D', anchor='w', width=25).pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Arial", 10),
                     bg='white', fg='#2C3E50', anchor='w').pack(side=tk.LEFT)

        # Formulaire
        form_frame = tk.Frame(main_frame, bg='#ECF0F1')
        form_frame.pack(fill=tk.X)

        # --- Motif ---
        tk.Label(form_frame, text="Motif *", font=("Arial", 10, "bold"),
                 bg='#ECF0F1', fg='#2C3E50').pack(anchor='w', pady=(0, 5))

        self.motif_var = tk.StringVar(value=MOTIFS[0])
        motif_combo = ttk.Combobox(
            form_frame, textvariable=self.motif_var,
            values=MOTIFS, font=("Arial", 12), state='readonly'
        )
        motif_combo.pack(fill=tk.X, pady=(0, 10))
        motif_combo.bind('<<ComboboxSelected>>', self._on_motif_change)

        # --- Section cotisation (conteneur fixe dans l'ordre de pack) ---
        self._cotisation_container = tk.Frame(form_frame, bg='#ECF0F1')
        self._cotisation_container.pack(fill=tk.X)

        self._cotisation_inner = tk.Frame(self._cotisation_container, bg='#ECF0F1')
        self._cotisation_inner.pack(fill=tk.X)

        tk.Label(self._cotisation_inner, text="Appel de fonds concerne",
                 font=("Arial", 10, "bold"), bg='#ECF0F1', fg='#2C3E50').pack(anchor='w', pady=(0, 5))

        self.cotisation_var = tk.StringVar()
        self.cotisation_combo = ttk.Combobox(
            self._cotisation_inner, textvariable=self.cotisation_var,
            font=("Arial", 11), state='readonly'
        )
        self.cotisation_combo.pack(fill=tk.X, pady=(0, 5))
        self.cotisation_combo.bind('<<ComboboxSelected>>', self._on_cotisation_change)

        self.reste_label = tk.Label(
            self._cotisation_inner, text="", font=("Arial", 10),
            bg='#ECF0F1', fg='#E74C3C'
        )
        self.reste_label.pack(anchor='w', pady=(0, 8))

        self._load_cotisations()

        # --- Montant ---
        tk.Label(form_frame, text=f"Montant ({CURRENCY_SYMBOL}) *",
                 font=("Arial", 10, "bold"), bg='#ECF0F1', fg='#2C3E50').pack(anchor='w', pady=(0, 5))

        self.montant_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.montant_entry.pack(fill=tk.X, pady=(0, 10))
        self.montant_entry.focus()

        # --- Date ---
        tk.Label(form_frame, text="Date de paiement *",
                 font=("Arial", 10, "bold"), bg='#ECF0F1', fg='#2C3E50').pack(anchor='w', pady=(0, 5))

        self.date_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.date_entry.pack(fill=tk.X, pady=(0, 10))
        self.date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))

        # --- Mode de paiement ---
        tk.Label(form_frame, text="Mode de paiement",
                 font=("Arial", 10, "bold"), bg='#ECF0F1', fg='#2C3E50').pack(anchor='w', pady=(0, 5))

        self.mode_var = tk.StringVar(value=PAYMENT_MODES[0])
        ttk.Combobox(form_frame, textvariable=self.mode_var,
                     values=PAYMENT_MODES, font=("Arial", 12),
                     state='readonly').pack(fill=tk.X, pady=(0, 10))

        # --- Admin ---
        tk.Label(form_frame, text="Enregistre par *",
                 font=("Arial", 10, "bold"), bg='#ECF0F1', fg='#2C3E50').pack(anchor='w', pady=(0, 5))

        admin_values = [f"{id} - {name}" for id, name in ADMIN_IDS.items()]
        self.admin_var = tk.StringVar(value=admin_values[0])
        ttk.Combobox(form_frame, textvariable=self.admin_var,
                     values=admin_values, font=("Arial", 12),
                     state='readonly').pack(fill=tk.X, pady=(0, 10))

        # --- Reference ---
        tk.Label(form_frame, text="Reference (n cheque, transaction, etc.)",
                 font=("Arial", 10), bg='#ECF0F1', fg='#2C3E50').pack(anchor='w', pady=(0, 5))

        self.reference_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.reference_entry.pack(fill=tk.X, pady=(0, 10))

        # --- Notes ---
        tk.Label(form_frame, text="Notes",
                 font=("Arial", 10), bg='#ECF0F1', fg='#2C3E50').pack(anchor='w', pady=(0, 5))

        self.notes_text = tk.Text(form_frame, font=("Arial", 10), height=3)
        self.notes_text.pack(fill=tk.X, pady=(0, 10))

        # --- Boutons ---
        buttons_frame = tk.Frame(main_frame, bg='#ECF0F1')
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            buttons_frame, text="Enregistrer",
            font=("Arial", 11, "bold"), bg='#27AE60', fg='white',
            padx=20, pady=10, command=self.on_save
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        tk.Button(
            buttons_frame, text="Annuler",
            font=("Arial", 11), bg='#95A5A6', fg='white',
            padx=20, pady=10, command=self.on_cancel
        ).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))

    # ------------------------------------------------------------------
    # Helpers UI
    # ------------------------------------------------------------------

    def _load_cotisations(self):
        """Charge les cotisations impayees de l'adherent"""
        self._cotisations_impayees = Cotisation.get_impayees_adherent(self.adherent.id)

        values = []
        for cot in self._cotisations_impayees:
            annee = getattr(cot, 'appel_annee', '?')
            reste = cot.get_reste_a_payer()
            desc = getattr(cot, 'appel_description', '') or ''
            label = f"Appel {annee} - Reste: {reste:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')
            if desc:
                label += f" ({desc})"
            values.append(label)

        self.cotisation_combo['values'] = values
        if values:
            self.cotisation_combo.current(0)
            self._update_reste_label()
        else:
            self.reste_label.config(text="Aucune cotisation impayee pour cet adherent")

    def _on_motif_change(self, event=None):
        """Affiche ou masque la section cotisation selon le motif choisi"""
        if self.motif_var.get() == "Cotisation":
            self._cotisation_inner.pack(fill=tk.X)
        else:
            self._cotisation_inner.pack_forget()

    def _on_cotisation_change(self, event=None):
        self._update_reste_label()

    def _update_reste_label(self):
        idx = self.cotisation_combo.current()
        if 0 <= idx < len(self._cotisations_impayees):
            cot = self._cotisations_impayees[idx]
            reste = cot.get_reste_a_payer()
            self.reste_label.config(
                text=f"Reste a payer: {reste:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')
            )
            self.montant_entry.delete(0, tk.END)
            self.montant_entry.insert(0, str(int(reste)))

    # ------------------------------------------------------------------
    # Validation et sauvegarde
    # ------------------------------------------------------------------

    def _extraire_champs_communs(self):
        """Valide et retourne les champs communs, ou None si invalide"""
        montant_str = self.montant_entry.get().strip()
        if not montant_str:
            messagebox.showerror("Erreur", "Le montant est obligatoire")
            self.montant_entry.focus()
            return None
        try:
            montant = float(montant_str)
            if montant <= 0:
                messagebox.showerror("Erreur", "Le montant doit etre positif")
                self.montant_entry.focus()
                return None
        except ValueError:
            messagebox.showerror("Erreur", "Le montant doit etre un nombre")
            self.montant_entry.focus()
            return None

        date_str = self.date_entry.get().strip()
        if not date_str:
            messagebox.showerror("Erreur", "La date est obligatoire")
            self.date_entry.focus()
            return None
        try:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        except ValueError:
            messagebox.showerror("Erreur", "Format de date invalide (JJ/MM/AAAA)")
            self.date_entry.focus()
            return None

        admin_str = self.admin_var.get()
        admin_id = int(admin_str.split(' - ')[0])

        return {
            'montant': montant,
            'date_paiement': date_obj.strftime('%Y-%m-%d'),
            'mode_paiement': self.mode_var.get(),
            'admin_id': admin_id,
            'reference': self.reference_entry.get().strip() or None,
            'notes': self.notes_text.get('1.0', tk.END).strip() or None,
        }

    def on_save(self):
        """Enregistre le paiement selon le motif choisi"""
        fields = self._extraire_champs_communs()
        if not fields:
            return

        try:
            motif = self.motif_var.get()
            if motif == "Cotisation":
                contribution = self._sauvegarder_cotisation(fields)
            else:
                contribution = self._sauvegarder_frais_entree(fields)

            self._generer_pdf(contribution)
            self.result = True
            self.destroy()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement:\n{str(e)}")

    def _sauvegarder_cotisation(self, fields):
        """Cree un paiement de cotisation et met a jour la cotisation liee"""
        idx = self.cotisation_combo.current()
        if 0 <= idx < len(self._cotisations_impayees):
            # Lier le paiement a la cotisation impayee selectionnee
            cotisation = self._cotisations_impayees[idx]
            return cotisation.enregistrer_paiement(
                montant=fields['montant'],
                date_paiement=fields['date_paiement'],
                mode_paiement=fields['mode_paiement'],
                reference_paiement=fields['reference'],
                admin_id=fields['admin_id'],
                notes=fields['notes']
            )
        else:
            # Pas de cotisation impayee : paiement direct avec log historique
            contribution = Contribution.create(
                adherent_id=self.adherent.id,
                montant=fields['montant'],
                date_paiement=fields['date_paiement'],
                mode_paiement=fields['mode_paiement'],
                reference_paiement=fields['reference'],
                admin_id=fields['admin_id'],
                type_paiement='cotisation',
                notes=fields['notes']
            )
            Historique.log(
                self.adherent.id, 'paiement_cotisation',
                f"Paiement cotisation: {fields['montant']} {CURRENCY_SYMBOL}",
                montant=fields['montant'], admin_id=fields['admin_id']
            )
            return contribution

    def _sauvegarder_frais_entree(self, fields):
        """Cree un paiement de frais d'entree et met a jour l'adherent"""
        contribution = Contribution.create(
            adherent_id=self.adherent.id,
            montant=fields['montant'],
            date_paiement=fields['date_paiement'],
            mode_paiement=fields['mode_paiement'],
            reference_paiement=fields['reference'],
            admin_id=fields['admin_id'],
            type_paiement='frais_entree',
            notes=fields['notes']
        )
        self.adherent.update(frais_entree_paye=1)
        Historique.log(
            self.adherent.id, 'frais_entree',
            f"Paiement frais d'entree: {fields['montant']} {CURRENCY_SYMBOL}",
            montant=fields['montant'], admin_id=fields['admin_id']
        )
        return contribution

    def _generer_pdf(self, contribution):
        """Genere le recu PDF apres enregistrement"""
        try:
            from services.pdf_service import PdfService
            PdfService.generer_pdf_paiement(contribution)
        except Exception as pdf_err:
            messagebox.showwarning(
                "PDF",
                f"Le paiement a ete enregistre mais le PDF n'a pas pu etre genere:\n{str(pdf_err)}"
            )

    def on_cancel(self):
        self.result = None
        self.destroy()
