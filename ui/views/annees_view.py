"""
Vue de gestion des années
Liste et gestion des années fiscales
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.annee import Annee
from ui.components.annee_form import AnneeForm
from config import CURRENCY_SYMBOL


class AnneesView(tk.Frame):
    """Vue de gestion des années"""

    def __init__(self, parent, main_window):
        super().__init__(parent, bg='#ECF0F1')
        self.main_window = main_window

        self.setup_ui()
        self.load_annees()

    def setup_ui(self):
        """Configure l'interface"""
        # En-tête
        header_frame = tk.Frame(self, bg='#ECF0F1')
        header_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = tk.Label(
            header_frame,
            text="Gestion des années",
            font=("Arial", 18, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        title_label.pack(side=tk.LEFT)

        # Bouton Nouvelle année
        btn_add = tk.Button(
            header_frame,
            text="+ Nouvelle année",
            font=("Arial", 10, "bold"),
            bg='#27AE60',
            fg='white',
            padx=15,
            pady=8,
            command=self.on_new_annee
        )
        btn_add.pack(side=tk.RIGHT, padx=(5, 0))

        # Bouton rafraîchir
        btn_refresh = tk.Button(
            header_frame,
            text="⟳ Rafraîchir",
            font=("Arial", 10),
            bg='#3498DB',
            fg='white',
            padx=10,
            pady=8,
            command=self.load_annees
        )
        btn_refresh.pack(side=tk.RIGHT)

        # Tableau des années
        self.setup_treeview()

        # Boutons d'action
        self.setup_buttons()

    def setup_treeview(self):
        """Configure le tableau (Treeview)"""
        # Frame pour le tableau
        table_frame = tk.Frame(self, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")

        # Treeview
        columns = ('id', 'annee', 'balance_cible', 'balance_actuelle',
                   'nombre_adherents', 'montant_par_adherent', 'active')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set
        )

        vsb.config(command=self.tree.yview)

        # Définir les colonnes
        self.tree.heading('id', text='ID')
        self.tree.heading('annee', text='Année')
        self.tree.heading('balance_cible', text='Balance cible')
        self.tree.heading('balance_actuelle', text='Balance actuelle')
        self.tree.heading('nombre_adherents', text='Adhérents')
        self.tree.heading('montant_par_adherent', text='Montant/Adhérent')
        self.tree.heading('active', text='Statut')

        # Largeur des colonnes
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('annee', width=80, anchor=tk.CENTER)
        self.tree.column('balance_cible', width=120, anchor=tk.E)
        self.tree.column('balance_actuelle', width=120, anchor=tk.E)
        self.tree.column('nombre_adherents', width=80, anchor=tk.CENTER)
        self.tree.column('montant_par_adherent', width=120, anchor=tk.E)
        self.tree.column('active', width=80, anchor=tk.CENTER)

        # Style des lignes
        self.tree.tag_configure('oddrow', background='#F8F9FA')
        self.tree.tag_configure('evenrow', background='white')
        self.tree.tag_configure('active', background='#D4EDDA')

        # Double-clic pour voir les détails
        self.tree.bind('<Double-1>', lambda e: self.on_view_details())

        # Grid
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def setup_buttons(self):
        """Configure les boutons d'action"""
        buttons_frame = tk.Frame(self, bg='#ECF0F1')
        buttons_frame.pack(fill=tk.X)

        btn_activate = tk.Button(
            buttons_frame,
            text="✓ Activer",
            font=("Arial", 10),
            bg='#27AE60',
            fg='white',
            padx=15,
            pady=8,
            command=self.on_activate_annee
        )
        btn_activate.pack(side=tk.LEFT, padx=(0, 5))

        btn_details = tk.Button(
            buttons_frame,
            text="📊 Voir détails",
            font=("Arial", 10),
            bg='#3498DB',
            fg='white',
            padx=15,
            pady=8,
            command=self.on_view_details
        )
        btn_details.pack(side=tk.LEFT, padx=5)

        btn_create_contrib = tk.Button(
            buttons_frame,
            text="➕ Créer contributions",
            font=("Arial", 10),
            bg='#9B59B6',
            fg='white',
            padx=15,
            pady=8,
            command=self.on_create_contributions
        )
        btn_create_contrib.pack(side=tk.LEFT, padx=5)

        # Label compteur
        self.count_label = tk.Label(
            buttons_frame,
            text="0 année(s)",
            font=("Arial", 10),
            bg='#ECF0F1',
            fg='#7F8C8D'
        )
        self.count_label.pack(side=tk.RIGHT, padx=10)

    def load_annees(self):
        """Charge les années dans le tableau"""
        try:
            # Effacer le tableau
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Récupérer les années
            annees = Annee.get_all()

            # Remplir le tableau
            for i, annee in enumerate(annees):
                statut = "Active" if annee.active else "Inactive"
                values = (
                    annee.id,
                    annee.annee,
                    f"{annee.balance_cible:,.0f} {CURRENCY_SYMBOL}".replace(',', ' '),
                    f"{annee.balance_actuelle:,.0f} {CURRENCY_SYMBOL}".replace(',', ' '),
                    annee.nombre_adherents,
                    f"{annee.montant_par_adherent:,.0f} {CURRENCY_SYMBOL}".replace(',', ' '),
                    statut
                )

                # Tag pour l'alternance de couleurs et année active
                if annee.active:
                    tag = 'active'
                else:
                    tag = 'evenrow' if i % 2 == 0 else 'oddrow'

                self.tree.insert('', tk.END, values=values, tags=(tag,))

            # Mettre à jour le compteur
            self.count_label.config(text=f"{len(annees)} année(s)")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement:\n{str(e)}")

    def on_new_annee(self):
        """Ouvre le formulaire de nouvelle année"""
        form = AnneeForm(self, "Nouvelle année")
        self.wait_window(form)

        # Rafraîchir la liste si une année a été créée
        if form.result:
            self.load_annees()
            self.main_window.refresh_annee_active()
            messagebox.showinfo("Succès", "Année créée avec succès")

    def on_activate_annee(self):
        """Active une année"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une année")
            return

        # Récupérer l'année
        values = self.tree.item(selected[0])['values']
        annee_id = values[0]
        annee = Annee.get_by_id(annee_id)

        if not annee:
            messagebox.showerror("Erreur", "Année non trouvée")
            return

        # Confirmation
        if not messagebox.askyesno(
            "Confirmer l'activation",
            f"Activer l'année {annee.annee}?\n\n"
            f"Cela désactivera toutes les autres années."
        ):
            return

        try:
            annee.set_active()
            self.load_annees()
            self.main_window.refresh_annee_active()
            messagebox.showinfo("Succès", f"Année {annee.annee} activée")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'activation:\n{str(e)}")

    def on_view_details(self):
        """Affiche les détails d'une année"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une année")
            return

        values = self.tree.item(selected[0])['values']
        annee_id = values[0]
        annee = Annee.get_by_id(annee_id)

        if not annee:
            messagebox.showerror("Erreur", "Année non trouvée")
            return

        # Afficher les détails (fenêtre modale)
        self.show_details_dialog(annee)

    def show_details_dialog(self, annee):
        """Affiche une fenêtre modale avec les détails de l'année"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Détails Année {annee.annee}")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()

        # Centrer la fenêtre
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')

        # Frame principal
        main_frame = tk.Frame(dialog, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Titre
        title = tk.Label(
            main_frame,
            text=f"Année {annee.annee}",
            font=("Arial", 16, "bold"),
            bg='white',
            fg='#2C3E50'
        )
        title.pack(pady=(0, 20))

        # Informations
        info_frame = tk.Frame(main_frame, bg='white')
        info_frame.pack(fill=tk.BOTH, expand=True)

        infos = [
            ("Balance cible", f"{annee.balance_cible:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')),
            ("Balance actuelle", f"{annee.balance_actuelle:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')),
            ("Nombre d'adhérents", str(annee.nombre_adherents)),
            ("Montant par adhérent", f"{annee.montant_par_adherent:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')),
            ("Total contributions payées", f"{annee.get_total_contributions_payees():,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')),
            ("Total dépenses", f"{annee.get_total_depenses():,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')),
            ("Taux de recouvrement", f"{annee.get_taux_recouvrement():.1f}%"),
            ("Statut", "Active" if annee.active else "Inactive")
        ]

        for i, (label, value) in enumerate(infos):
            label_widget = tk.Label(
                info_frame,
                text=f"{label}:",
                font=("Arial", 11, "bold"),
                bg='white',
                fg='#7F8C8D',
                anchor='w'
            )
            label_widget.grid(row=i, column=0, sticky='w', pady=5, padx=(0, 20))

            value_widget = tk.Label(
                info_frame,
                text=value,
                font=("Arial", 11),
                bg='white',
                fg='#2C3E50',
                anchor='w'
            )
            value_widget.grid(row=i, column=1, sticky='w', pady=5)

        # Bouton Fermer
        btn_close = tk.Button(
            main_frame,
            text="Fermer",
            font=("Arial", 11),
            bg='#95A5A6',
            fg='white',
            padx=20,
            pady=10,
            command=dialog.destroy
        )
        btn_close.pack(pady=(20, 0))

    def on_create_contributions(self):
        """Crée les contributions pour l'année sélectionnée"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une année")
            return

        values = self.tree.item(selected[0])['values']
        annee_id = values[0]
        annee = Annee.get_by_id(annee_id)

        if not annee:
            messagebox.showerror("Erreur", "Année non trouvée")
            return

        # Confirmation
        if not messagebox.askyesno(
            "Confirmer la création",
            f"Créer les contributions pour l'année {annee.annee}?\n\n"
            f"Cela créera une contribution de {annee.montant_par_adherent:,.0f} {CURRENCY_SYMBOL}\n"
            f"pour chacun des {annee.nombre_adherents} adhérents actifs.".replace(',', ' ')
        ):
            return

        try:
            from services.contribution_service import ContributionService
            count = ContributionService.creer_contributions_annee(annee_id)

            messagebox.showinfo(
                "Succès",
                f"{count} contribution(s) créée(s) pour l'année {annee.annee}"
            )
            self.load_annees()
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Erreur lors de la création des contributions:\n{str(e)}"
            )
