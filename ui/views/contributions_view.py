"""
Vue d'enregistrement des contributions
Affiche tous les paiements individuels
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.adherent import Adherent
from models.contribution import Contribution
from ui.components.paiement_form import PaiementForm
from database.db_manager import DatabaseManager
from datetime import datetime
from config import CURRENCY_SYMBOL, ADMIN_IDS


class ContributionsView(tk.Frame):
    """Vue d'enregistrement des contributions"""

    def __init__(self, parent, main_window):
        super().__init__(parent, bg='#ECF0F1')
        self.main_window = main_window
        self.annee_courante = datetime.now().year

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Configure l'interface"""
        # En-tete
        header_frame = tk.Frame(self, bg='#ECF0F1')
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = tk.Label(
            header_frame,
            text=f"Paiements - Annee {self.annee_courante}",
            font=("Arial", 18, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        title_label.pack()

        # Barre de recherche
        search_frame = tk.Frame(self, bg='#ECF0F1')
        search_frame.pack(fill=tk.X, pady=(0, 10))

        search_label = tk.Label(
            search_frame,
            text="Rechercher adherent:",
            font=("Arial", 12, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        search_label.pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.on_search())

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 12),
            width=40
        )
        search_entry.pack(side=tk.LEFT)
        search_entry.focus()

        # Bouton rafraichir
        btn_refresh = tk.Button(
            search_frame,
            text="Rafraichir",
            font=("Arial", 10),
            bg='#3498DB',
            fg='white',
            padx=10,
            pady=5,
            command=self.load_data
        )
        btn_refresh.pack(side=tk.RIGHT)

        # Tableau des resultats
        self.setup_treeview()

        # Boutons d'action
        self.setup_buttons()

    def setup_treeview(self):
        """Configure le tableau"""
        table_frame = tk.Frame(self, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        vsb = ttk.Scrollbar(table_frame, orient="vertical")

        columns = ('id', 'adherent_id', 'nom', 'prenom', 'montant',
                   'date_paiement', 'mode_paiement', 'admin')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set
        )

        vsb.config(command=self.tree.yview)

        # En-tetes
        self.tree.heading('id', text='ID')
        self.tree.heading('adherent_id', text='')
        self.tree.heading('nom', text='Nom')
        self.tree.heading('prenom', text='Prenom')
        self.tree.heading('montant', text='Montant')
        self.tree.heading('date_paiement', text='Date')
        self.tree.heading('mode_paiement', text='Mode')
        self.tree.heading('admin', text='Admin')

        # Largeur
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('adherent_id', width=0, minwidth=0, stretch=False)
        self.tree.column('nom', width=150)
        self.tree.column('prenom', width=150)
        self.tree.column('montant', width=120, anchor=tk.E)
        self.tree.column('date_paiement', width=100, anchor=tk.CENTER)
        self.tree.column('mode_paiement', width=100, anchor=tk.CENTER)
        self.tree.column('admin', width=100, anchor=tk.CENTER)

        # Tags pour colorer (alternance)
        self.tree.tag_configure('oddrow', background='#F8F9FA')
        self.tree.tag_configure('evenrow', background='white')

        # Double-clic pour payer
        self.tree.bind('<Double-1>', lambda e: self.on_enregistrer_paiement())

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def setup_buttons(self):
        """Configure les boutons"""
        buttons_frame = tk.Frame(self, bg='#ECF0F1')
        buttons_frame.pack(fill=tk.X)

        btn_paiement = tk.Button(
            buttons_frame,
            text="Enregistrer un paiement",
            font=("Arial", 11, "bold"),
            bg='#27AE60',
            fg='white',
            padx=20,
            pady=10,
            command=self.on_enregistrer_paiement
        )
        btn_paiement.pack(side=tk.LEFT, padx=(0, 5))

        btn_historique = tk.Button(
            buttons_frame,
            text="Voir historique",
            font=("Arial", 10),
            bg='#3498DB',
            fg='white',
            padx=15,
            pady=10,
            command=self.on_voir_historique
        )
        btn_historique.pack(side=tk.LEFT, padx=5)

        # Label compteur
        self.count_label = tk.Label(
            buttons_frame,
            text="0 paiement(s)",
            font=("Arial", 10),
            bg='#ECF0F1',
            fg='#7F8C8D'
        )
        self.count_label.pack(side=tk.RIGHT, padx=10)

    def load_data(self):
        """Charge tous les paiements individuels de l'annee"""
        try:
            # Effacer le tableau
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Recuperer tous les paiements avec info adherent
            db = DatabaseManager()
            query = """
                SELECT c.id, c.adherent_id, a.nom, a.prenom,
                       c.montant, c.date_paiement, c.mode_paiement, c.admin_id
                FROM contributions c
                JOIN adherents a ON c.adherent_id = a.id
                WHERE strftime('%Y', c.date_paiement) = ?
                ORDER BY c.date_paiement DESC
            """
            rows = db.fetch_all(query, (str(self.annee_courante),))

            # Remplir le tableau
            for i, row in enumerate(rows):
                # Formater la date
                date_str = row['date_paiement'] or '-'
                if date_str != '-':
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        date_str = date_obj.strftime('%d/%m/%Y')
                    except:
                        pass

                # Nom admin
                admin_id = row['admin_id']
                admin_name = ADMIN_IDS.get(admin_id, '') if admin_id else ''

                values = (
                    row['id'],
                    row['adherent_id'],
                    row['nom'],
                    row['prenom'],
                    f"{row['montant']:,.0f} {CURRENCY_SYMBOL}".replace(',', ' '),
                    date_str,
                    row['mode_paiement'] or '',
                    admin_name
                )

                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tree.insert('', tk.END, values=values, tags=(tag,))

            # Mettre a jour le compteur
            self.count_label.config(text=f"{len(rows)} paiement(s)")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement:\n{str(e)}")

    def on_search(self):
        """Gere la recherche par nom d'adherent"""
        keyword = self.search_var.get().strip()

        if not keyword:
            self.load_data()
            return

        if len(keyword) < 2:
            return

        try:
            # Effacer le tableau
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Rechercher les adherents
            adherents = Adherent.search(keyword)

            if not adherents:
                self.count_label.config(text="0 paiement(s)")
                return

            # Pour chaque adherent trouve, afficher ses paiements
            count = 0
            for adherent in adherents:
                paiements = Contribution.get_by_adherent(
                    adherent.id, self.annee_courante
                )

                for contrib in paiements:
                    # Formater la date
                    date_str = contrib.date_paiement or '-'
                    if date_str != '-':
                        try:
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            date_str = date_obj.strftime('%d/%m/%Y')
                        except:
                            pass

                    admin_name = ADMIN_IDS.get(contrib.admin_id, '') if contrib.admin_id else ''

                    values = (
                        contrib.id,
                        adherent.id,
                        adherent.nom,
                        adherent.prenom,
                        f"{contrib.montant:,.0f} {CURRENCY_SYMBOL}".replace(',', ' '),
                        date_str,
                        contrib.mode_paiement or '',
                        admin_name
                    )

                    tag = 'evenrow' if count % 2 == 0 else 'oddrow'
                    self.tree.insert('', tk.END, values=values, tags=(tag,))
                    count += 1

            self.count_label.config(text=f"{count} paiement(s)")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la recherche:\n{str(e)}")

    def _get_selected_adherent(self):
        """Recupere l'adherent de la ligne selectionnee"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez selectionner une ligne")
            return None

        values = self.tree.item(selected[0])['values']
        adherent_id = values[1]  # adherent_id est en colonne 1
        adherent = Adherent.get_by_id(adherent_id)

        if not adherent:
            messagebox.showerror("Erreur", "Adherent non trouve")
            return None

        return adherent

    def on_enregistrer_paiement(self):
        """Enregistre un paiement"""
        adherent = self._get_selected_adherent()
        if not adherent:
            return

        if not adherent.actif:
            messagebox.showerror(
                "Erreur",
                f"{adherent.get_nom_complet()} est inactif.\n"
                "Les paiements ne sont pas autorises pour les adherents inactifs."
            )
            return

        # Ouvrir le formulaire de paiement
        form = PaiementForm(self, adherent)
        self.wait_window(form)

        # Rafraichir si un paiement a ete enregistre
        if form.result:
            keyword = self.search_var.get().strip()
            if keyword:
                self.on_search()
            else:
                self.load_data()
            messagebox.showinfo("Succes", "Paiement enregistre avec succes")

    def on_voir_historique(self):
        """Affiche l'historique des paiements"""
        adherent = self._get_selected_adherent()
        if not adherent:
            return

        # Recuperer les paiements
        paiements = Contribution.get_by_adherent(adherent.id, self.annee_courante)

        if not paiements:
            messagebox.showinfo(
                "Historique",
                f"Aucun paiement enregistre pour {adherent.get_nom_complet()} en {self.annee_courante}"
            )
            return

        # Creer une fenetre pour l'historique
        dialog = tk.Toplevel(self)
        dialog.title(f"Historique - {adherent.get_nom_complet()}")
        dialog.geometry("600x400")
        dialog.transient(self)

        # Liste des paiements
        text = tk.Text(dialog, font=("Arial", 10), wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text.insert(tk.END, f"Historique des paiements - {adherent.get_nom_complet()}\n")
        text.insert(tk.END, f"Annee: {self.annee_courante}\n")
        text.insert(tk.END, "="*60 + "\n\n")

        total = 0
        for paiement in paiements:
            total += paiement.montant

            # Formater la date
            date_str = paiement.date_paiement
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                date_str = date_obj.strftime('%d/%m/%Y')
            except:
                pass

            text.insert(tk.END, f"Date: {date_str}\n")
            text.insert(tk.END, f"Montant: {paiement.montant:,.0f} {CURRENCY_SYMBOL}\n".replace(',', ' '))
            if paiement.mode_paiement:
                text.insert(tk.END, f"Mode: {paiement.mode_paiement}\n")
            if paiement.reference_paiement:
                text.insert(tk.END, f"Reference: {paiement.reference_paiement}\n")
            if paiement.admin_id:
                admin_name = ADMIN_IDS.get(paiement.admin_id, f"Admin {paiement.admin_id}")
                text.insert(tk.END, f"Admin: {admin_name}\n")
            text.insert(tk.END, "\n")

        text.insert(tk.END, "="*60 + "\n")
        text.insert(tk.END, f"TOTAL: {total:,.0f} {CURRENCY_SYMBOL}\n".replace(',', ' '))

        text.config(state=tk.DISABLED)
