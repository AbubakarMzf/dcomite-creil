"""
Vue de gestion des adhérents
Liste, recherche et CRUD des adhérents
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.adherent import Adherent
from ui.components.adherent_form import AdherentForm


class AdherentsView(tk.Frame):
    """Vue de gestion des adhérents"""

    def __init__(self, parent, main_window):
        super().__init__(parent, bg='#ECF0F1')
        self.main_window = main_window

        self.setup_ui()
        self.load_adherents()

    def setup_ui(self):
        """Configure l'interface"""
        # En-tête
        header_frame = tk.Frame(self, bg='#ECF0F1')
        header_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = tk.Label(
            header_frame,
            text="Gestion des adhérents",
            font=("Arial", 18, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        title_label.pack(side=tk.LEFT)

        # Bouton Ajouter
        btn_add = tk.Button(
            header_frame,
            text="+ Ajouter un adhérent",
            font=("Arial", 10, "bold"),
            bg='#27AE60',
            fg='white',
            padx=15,
            pady=8,
            command=self.on_add_adherent
        )
        btn_add.pack(side=tk.RIGHT)

        # Barre de recherche
        search_frame = tk.Frame(self, bg='#ECF0F1')
        search_frame.pack(fill=tk.X, pady=(0, 10))

        search_label = tk.Label(
            search_frame,
            text="Rechercher:",
            font=("Arial", 10),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        search_label.pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.on_search())

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 10),
            width=40
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Filtre actif/inactif
        self.show_actifs_only = tk.BooleanVar(value=True)
        check_actifs = tk.Checkbutton(
            search_frame,
            text="Adhérents actifs uniquement",
            variable=self.show_actifs_only,
            font=("Arial", 10),
            bg='#ECF0F1',
            command=self.load_adherents
        )
        check_actifs.pack(side=tk.LEFT, padx=10)

        # Bouton rafraîchir
        btn_refresh = tk.Button(
            search_frame,
            text="⟳ Rafraîchir",
            font=("Arial", 10),
            bg='#3498DB',
            fg='white',
            padx=10,
            pady=5,
            command=self.load_adherents
        )
        btn_refresh.pack(side=tk.RIGHT)

        # Tableau des adhérents
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
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")

        # Treeview
        columns = ('id', 'nom', 'prenom', 'telephone', 'email', 'actif')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Définir les colonnes
        self.tree.heading('id', text='ID')
        self.tree.heading('nom', text='Nom')
        self.tree.heading('prenom', text='Prénom')
        self.tree.heading('telephone', text='Téléphone')
        self.tree.heading('email', text='Email')
        self.tree.heading('actif', text='Statut')

        # Largeur des colonnes
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('nom', width=150)
        self.tree.column('prenom', width=150)
        self.tree.column('telephone', width=120)
        self.tree.column('email', width=200)
        self.tree.column('actif', width=80, anchor=tk.CENTER)

        # Style des lignes alternées
        self.tree.tag_configure('oddrow', background='#F8F9FA')
        self.tree.tag_configure('evenrow', background='white')
        self.tree.tag_configure('inactive', foreground='#95A5A6')

        # Double-clic pour éditer
        self.tree.bind('<Double-1>', lambda e: self.on_edit_adherent())

        # Grid
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def setup_buttons(self):
        """Configure les boutons d'action"""
        buttons_frame = tk.Frame(self, bg='#ECF0F1')
        buttons_frame.pack(fill=tk.X)

        btn_edit = tk.Button(
            buttons_frame,
            text="✏ Modifier",
            font=("Arial", 10),
            bg='#3498DB',
            fg='white',
            padx=15,
            pady=8,
            command=self.on_edit_adherent
        )
        btn_edit.pack(side=tk.LEFT, padx=(0, 5))

        btn_delete = tk.Button(
            buttons_frame,
            text="🗑 Supprimer",
            font=("Arial", 10),
            bg='#E74C3C',
            fg='white',
            padx=15,
            pady=8,
            command=self.on_delete_adherent
        )
        btn_delete.pack(side=tk.LEFT, padx=5)

        btn_toggle = tk.Button(
            buttons_frame,
            text="↔ Activer/Désactiver",
            font=("Arial", 10),
            bg='#F39C12',
            fg='white',
            padx=15,
            pady=8,
            command=self.on_toggle_active
        )
        btn_toggle.pack(side=tk.LEFT, padx=5)

        btn_paiement = tk.Button(
            buttons_frame,
            text="💰 Enregistrer paiement",
            font=("Arial", 10),
            bg='#27AE60',
            fg='white',
            padx=15,
            pady=8,
            command=self.on_enregistrer_paiement
        )
        btn_paiement.pack(side=tk.LEFT, padx=5)

        # Label compteur
        self.count_label = tk.Label(
            buttons_frame,
            text="0 adhérent(s)",
            font=("Arial", 10),
            bg='#ECF0F1',
            fg='#7F8C8D'
        )
        self.count_label.pack(side=tk.RIGHT, padx=10)

    def load_adherents(self, keyword=None):
        """Charge les adhérents dans le tableau"""
        try:
            # Effacer le tableau
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Récupérer les adhérents
            if keyword:
                adherents = Adherent.search(keyword)
            else:
                actifs_only = self.show_actifs_only.get()
                adherents = Adherent.get_all(actif_only=actifs_only)

            # Remplir le tableau
            for i, adherent in enumerate(adherents):
                statut = "Actif" if adherent.actif else "Inactif"
                values = (
                    adherent.id,
                    adherent.nom,
                    adherent.prenom,
                    adherent.telephone or '',
                    adherent.email or '',
                    statut
                )

                # Tag pour l'alternance de couleurs
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                if not adherent.actif:
                    tag = 'inactive'

                self.tree.insert('', tk.END, values=values, tags=(tag,))

            # Mettre à jour le compteur
            self.count_label.config(text=f"{len(adherents)} adhérent(s)")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement:\n{str(e)}")

    def on_search(self):
        """Gère la recherche"""
        keyword = self.search_var.get().strip()
        if keyword:
            self.load_adherents(keyword)
        else:
            self.load_adherents()

    def on_add_adherent(self):
        """Ouvre le formulaire d'ajout d'adhérent"""
        form = AdherentForm(self, "Ajouter un adhérent")
        self.wait_window(form)

        # Rafraîchir la liste si un adhérent a été créé
        if form.result:
            self.load_adherents()
            messagebox.showinfo("Succès", "Adhérent ajouté avec succès")

    def on_edit_adherent(self):
        """Ouvre le formulaire d'édition d'adhérent"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un adhérent")
            return

        # Récupérer l'ID de l'adhérent
        values = self.tree.item(selected[0])['values']
        adherent_id = values[0]

        # Récupérer l'adhérent
        adherent = Adherent.get_by_id(adherent_id)
        if not adherent:
            messagebox.showerror("Erreur", "Adhérent non trouvé")
            return

        # Ouvrir le formulaire
        form = AdherentForm(self, "Modifier un adhérent", adherent)
        self.wait_window(form)

        # Rafraîchir la liste si l'adhérent a été modifié
        if form.result:
            self.load_adherents()
            messagebox.showinfo("Succès", "Adhérent modifié avec succès")

    def on_delete_adherent(self):
        """Supprime un adhérent"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un adhérent")
            return

        # Récupérer l'adhérent
        values = self.tree.item(selected[0])['values']
        adherent_id = values[0]
        adherent = Adherent.get_by_id(adherent_id)

        if not adherent:
            messagebox.showerror("Erreur", "Adhérent non trouvé")
            return

        # Confirmation
        if not messagebox.askyesno(
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer {adherent.get_nom_complet()}?\n\n"
            f"Cette action supprimera aussi toutes ses contributions."
        ):
            return

        try:
            adherent.delete()
            self.load_adherents()
            messagebox.showinfo("Succès", "Adhérent supprimé avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression:\n{str(e)}")

    def on_toggle_active(self):
        """Active/désactive un adhérent"""
        from datetime import datetime

        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un adhérent")
            return

        # Récupérer l'adhérent
        values = self.tree.item(selected[0])['values']
        adherent_id = values[0]
        adherent = Adherent.get_by_id(adherent_id)

        if not adherent:
            messagebox.showerror("Erreur", "Adhérent non trouvé")
            return

        # Inverser le statut
        nouveau_statut = 0 if adherent.actif else 1
        try:
            if nouveau_statut == 0:
                # Désactivation : mettre la date de sortie
                date_sortie = datetime.now().strftime('%Y-%m-%d')
                adherent.update(actif=nouveau_statut, date_sortie=date_sortie)
            else:
                # Réactivation : effacer la date de sortie
                adherent.update(actif=nouveau_statut, date_sortie=None)

            self.load_adherents()
            statut_text = "activé" if nouveau_statut else "désactivé"
            messagebox.showinfo("Succès", f"Adhérent {statut_text} avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la modification:\n{str(e)}")

    def on_enregistrer_paiement(self):
        """Enregistre un paiement pour l'adhérent sélectionné"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner un adhérent")
            return

        values = self.tree.item(selected[0])['values']
        adherent_id = values[0]
        adherent = Adherent.get_by_id(adherent_id)

        if not adherent:
            messagebox.showerror("Erreur", "Adhérent non trouvé")
            return

        # Vérifier que l'adhérent est actif
        if not adherent.actif:
            messagebox.showerror(
                "Erreur",
                f"{adherent.get_nom_complet()} est inactif.\n"
                "Les paiements ne sont pas autorisés pour les adhérents inactifs."
            )
            return

        # Ouvrir le formulaire de paiement
        from ui.components.paiement_form import PaiementForm
        form = PaiementForm(self, adherent)
        self.wait_window(form)

        # Rafraîchir si paiement enregistré
        if form.result:
            messagebox.showinfo("Succès", "Paiement enregistré avec succès")
            self.main_window.show_dashboard()
