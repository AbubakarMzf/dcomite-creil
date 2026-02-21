"""
Vue de gestion des depenses
Liste des depenses (deces) et enregistrement
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.depense import Depense
from ui.components.depense_form import DepenseForm
from config import CURRENCY_SYMBOL, POSTES_DEPENSES
from datetime import datetime


class DepensesView(tk.Frame):
    """Vue de gestion des depenses"""

    def __init__(self, parent, main_window):
        super().__init__(parent, bg='#ECF0F1')
        self.main_window = main_window
        self.annee_active = main_window.annee_active

        if self.annee_active:
            self.setup_ui()
            self.load_depenses()
        else:
            self.show_no_annee_message()

    def show_no_annee_message(self):
        """Affiche un message si aucune annee n'est active"""
        container = tk.Frame(self, bg='#ECF0F1')
        container.pack(expand=True)

        tk.Label(
            container,
            text="Aucune annee active\n\nVeuillez creer et activer une annee via le menu Annee",
            font=("Arial", 14),
            bg='#ECF0F1',
            fg='#7F8C8D',
            justify=tk.CENTER
        ).pack(pady=50)

    def setup_ui(self):
        """Configure l'interface"""
        # En-tete
        header_frame = tk.Frame(self, bg='#ECF0F1')
        header_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            header_frame,
            text=f"Depenses (Deces) - Annee {self.annee_active.annee}",
            font=("Arial", 18, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        ).pack(side=tk.LEFT)

        tk.Button(
            header_frame,
            text="+ Nouvelle depense",
            font=("Arial", 10, "bold"),
            bg='#E74C3C',
            fg='white',
            padx=15,
            pady=8,
            command=self.on_add_depense
        ).pack(side=tk.RIGHT)

        # Bouton rafraichir
        filter_frame = tk.Frame(self, bg='#ECF0F1')
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Button(
            filter_frame,
            text="Rafraichir",
            font=("Arial", 10),
            bg='#3498DB',
            fg='white',
            padx=10,
            pady=5,
            command=self.load_depenses
        ).pack(side=tk.RIGHT)

        # Statistiques
        self.stats_frame = tk.Frame(self, bg='white', relief=tk.RAISED, borderwidth=1)
        self.stats_frame.pack(fill=tk.X, pady=(0, 10))

        stats_content = tk.Frame(self.stats_frame, bg='white')
        stats_content.pack(padx=15, pady=10)

        self.stats_labels = {}
        stats_items = [
            ("total_depenses", "Total depenses:"),
            ("nombre_deces", "Nombre de deces:"),
            ("balance_restante", "Balance restante:")
        ]

        for i, (key, label) in enumerate(stats_items):
            tk.Label(
                stats_content,
                text=label,
                font=("Arial", 10, "bold"),
                bg='white',
                fg='#7F8C8D'
            ).grid(row=0, column=i*2, padx=(0, 10))

            value_widget = tk.Label(
                stats_content,
                text=f"0 {CURRENCY_SYMBOL}",
                font=("Arial", 10),
                bg='white',
                fg='#2C3E50'
            )
            value_widget.grid(row=0, column=i*2+1, padx=(0, 20))

            self.stats_labels[key] = value_widget

        # Tableau
        self.setup_treeview()

        # Boutons d'action
        self.setup_buttons()

    def setup_treeview(self):
        """Configure le tableau"""
        table_frame = tk.Frame(self, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        vsb = ttk.Scrollbar(table_frame, orient="vertical")

        columns = ('id', 'date', 'defunt', 'adherent', 'montant', 'pays')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set
        )

        vsb.config(command=self.tree.yview)

        self.tree.heading('id', text='ID')
        self.tree.heading('date', text='Date deces')
        self.tree.heading('defunt', text='Defunt')
        self.tree.heading('adherent', text='Adherent lie')
        self.tree.heading('montant', text='Montant')
        self.tree.heading('pays', text='Pays')

        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('date', width=100, anchor=tk.CENTER)
        self.tree.column('defunt', width=180)
        self.tree.column('adherent', width=180)
        self.tree.column('montant', width=120, anchor=tk.E)
        self.tree.column('pays', width=120)

        self.tree.tag_configure('oddrow', background='#F8F9FA')
        self.tree.tag_configure('evenrow', background='white')

        self.tree.bind('<Double-1>', lambda e: self.on_view_details())

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def setup_buttons(self):
        """Configure les boutons"""
        buttons_frame = tk.Frame(self, bg='#ECF0F1')
        buttons_frame.pack(fill=tk.X)

        tk.Button(
            buttons_frame,
            text="Supprimer",
            font=("Arial", 10),
            bg='#E74C3C',
            fg='white',
            padx=15,
            pady=8,
            command=self.on_delete_depense
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.count_label = tk.Label(
            buttons_frame,
            text="0 depense(s)",
            font=("Arial", 10),
            bg='#ECF0F1',
            fg='#7F8C8D'
        )
        self.count_label.pack(side=tk.RIGHT, padx=10)

    def load_depenses(self):
        """Charge les depenses"""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)

            depenses = Depense.get_all_for_annee(self.annee_active.id)

            for i, depense in enumerate(depenses):
                # Nom du defunt
                nom_defunt = depense.get_nom_defunt()

                # Nom de l'adherent lie
                adherent = depense.get_adherent()
                nom_adherent = adherent.get_nom_complet() if adherent else "-"

                # Si le defunt est l'adherent, indiquer
                if depense.defunt_est_adherent:
                    nom_defunt = f"{nom_defunt} (adherent)"

                # Formater la date
                date_str = depense.date_deces or '-'
                if date_str != '-':
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        date_str = date_obj.strftime('%d/%m/%Y')
                    except:
                        pass

                values = (
                    depense.id,
                    date_str,
                    nom_defunt,
                    nom_adherent,
                    f"{depense.montant:,.0f} {CURRENCY_SYMBOL}".replace(',', ' '),
                    depense.pays_destination or ''
                )

                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tree.insert('', tk.END, values=values, tags=(tag,))

            self.count_label.config(text=f"{len(depenses)} depense(s)")
            self.update_statistics()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement:\n{str(e)}")

    def update_statistics(self):
        """Met a jour les statistiques"""
        try:
            from services.depense_service import DepenseService

            total = DepenseService.get_total_depenses(self.annee_active.id)
            nombre_deces = DepenseService.get_nombre_deces(self.annee_active.id)
            balance = self.annee_active.get_balance_actuelle()

            self.stats_labels['total_depenses'].config(
                text=f"{total:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')
            )
            self.stats_labels['nombre_deces'].config(text=str(nombre_deces))
            self.stats_labels['balance_restante'].config(
                text=f"{balance:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')
            )
        except:
            pass

    def on_add_depense(self):
        """Ajoute une depense"""
        form = DepenseForm(self, self.annee_active)
        self.wait_window(form)

        if form.result:
            self.load_depenses()
            self.main_window.show_dashboard()
            messagebox.showinfo("Succes", "Depense enregistree avec succes")

    def on_delete_depense(self):
        """Supprime une depense"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez selectionner une depense")
            return

        values = self.tree.item(selected[0])['values']
        depense_id = values[0]
        depense = Depense.get_by_id(depense_id)

        if not depense:
            messagebox.showerror("Erreur", "Depense non trouvee")
            return

        if not messagebox.askyesno(
            "Confirmer la suppression",
            f"Supprimer cette depense de {depense.montant:,.0f} {CURRENCY_SYMBOL}?".replace(',', ' ')
        ):
            return

        try:
            depense.delete()
            self.load_depenses()
            messagebox.showinfo("Succes", "Depense supprimee avec succes")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression:\n{str(e)}")

    def on_view_details(self):
        """Affiche les details d'une depense"""
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])['values']
        depense_id = values[0]
        depense = Depense.get_by_id(depense_id)

        if not depense:
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Details Depense #{depense.id}")
        dialog.geometry("500x500")
        dialog.transient(self)

        main_frame = tk.Frame(dialog, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            main_frame,
            text=f"Depense #{depense.id}",
            font=("Arial", 14, "bold"),
            bg='white'
        ).pack(pady=(0, 15))

        # Section deces
        deces_frame = tk.LabelFrame(
            main_frame,
            text=" Deces ",
            font=("Arial", 10, "bold"),
            bg='white',
            padx=10,
            pady=5
        )
        deces_frame.pack(fill=tk.X, pady=(0, 10))

        adherent = depense.get_adherent()
        adherent_nom = adherent.get_nom_complet() if adherent else "-"

        infos_deces = [
            ("Defunt", depense.get_nom_defunt()),
            ("Adherent lie", adherent_nom),
            ("Date du deces", depense.date_deces),
            ("Pays destination", depense.pays_destination or "-"),
        ]

        if not depense.defunt_est_adherent and depense.defunt_relation:
            infos_deces.insert(2, ("Relation", depense.defunt_relation))

        for i, (label, value) in enumerate(infos_deces):
            tk.Label(
                deces_frame, text=f"{label}:", font=("Arial", 9, "bold"),
                bg='white', fg='#7F8C8D', anchor='w'
            ).grid(row=i, column=0, sticky='w', pady=2, padx=(0, 15))
            tk.Label(
                deces_frame, text=value, font=("Arial", 9),
                bg='white', anchor='w'
            ).grid(row=i, column=1, sticky='w', pady=2)

        # Section frais
        frais_frame = tk.LabelFrame(
            main_frame,
            text=" Detail des frais ",
            font=("Arial", 10, "bold"),
            bg='white',
            padx=10,
            pady=5
        )
        frais_frame.pack(fill=tk.X, pady=(0, 10))

        postes = [
            ('transport_services', depense.transport_services),
            ('billet_avion', depense.billet_avion),
            ('imam', depense.imam),
            ('mairie', depense.mairie),
            ('autre1', depense.autre1),
            ('autre2', depense.autre2),
            ('autre3', depense.autre3),
        ]

        for i, (key, val) in enumerate(postes):
            label = POSTES_DEPENSES.get(key, key)
            tk.Label(
                frais_frame, text=f"{label}:", font=("Arial", 9),
                bg='white', fg='#7F8C8D', anchor='w'
            ).grid(row=i, column=0, sticky='w', pady=2, padx=(0, 15))
            tk.Label(
                frais_frame,
                text=f"{val:,.0f} {CURRENCY_SYMBOL}".replace(',', ' '),
                font=("Arial", 9), bg='white', anchor='e'
            ).grid(row=i, column=1, sticky='e', pady=2)

        # Total
        tk.Label(
            frais_frame, text="TOTAL:", font=("Arial", 9, "bold"),
            bg='white', fg='#E74C3C', anchor='w'
        ).grid(row=len(postes), column=0, sticky='w', pady=(5, 2), padx=(0, 15))
        tk.Label(
            frais_frame,
            text=f"{depense.montant:,.0f} {CURRENCY_SYMBOL}".replace(',', ' '),
            font=("Arial", 9, "bold"), bg='white', fg='#E74C3C', anchor='e'
        ).grid(row=len(postes), column=1, sticky='e', pady=(5, 2))

        tk.Button(
            main_frame,
            text="Fermer",
            command=dialog.destroy,
            bg='#95A5A6',
            fg='white',
            padx=20,
            pady=10
        ).pack(pady=(15, 0))
