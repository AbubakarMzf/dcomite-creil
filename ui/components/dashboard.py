"""
Tableau de bord (Dashboard)
Affiche les statistiques principales et les dernières activités
"""
import tkinter as tk
from tkinter import ttk, messagebox
from services.statistique_service import StatistiqueService
from services.contribution_service import ContributionService
from services.depense_service import DepenseService
from config import CURRENCY_SYMBOL


class Dashboard(tk.Frame):
    """Composant du tableau de bord"""

    def __init__(self, parent, main_window):
        super().__init__(parent, bg='#ECF0F1')
        self.main_window = main_window
        self.annee_active = main_window.annee_active

        if self.annee_active:
            self.setup_ui()
            self.load_data()
        else:
            self.show_no_annee_message()

    def show_no_annee_message(self):
        """Affiche un message si aucune année n'est active"""
        container = tk.Frame(self, bg='#ECF0F1')
        container.pack(expand=True)

        icon_label = tk.Label(
            container,
            text="⚠",
            font=("Arial", 48),
            bg='#ECF0F1',
            fg='#F39C12'
        )
        icon_label.pack(pady=10)

        message_label = tk.Label(
            container,
            text="Aucune année active",
            font=("Arial", 18, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        message_label.pack(pady=10)

        info_label = tk.Label(
            container,
            text="Veuillez créer une nouvelle année via le menu Année > Nouvelle année",
            font=("Arial", 12),
            bg='#ECF0F1',
            fg='#7F8C8D'
        )
        info_label.pack(pady=5)

        # Bouton pour créer une année
        btn_create = tk.Button(
            container,
            text="Créer une nouvelle année",
            font=("Arial", 12),
            bg='#3498DB',
            fg='white',
            padx=20,
            pady=10,
            command=self.main_window.new_annee
        )
        btn_create.pack(pady=20)

    def setup_ui(self):
        """Configure l'interface du dashboard"""
        # Titre
        title_frame = tk.Frame(self, bg='#ECF0F1')
        title_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = tk.Label(
            title_frame,
            text=f"Tableau de bord - Année {self.annee_active.annee}",
            font=("Arial", 18, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        title_label.pack(side=tk.LEFT)

        # Bouton rafraîchir
        btn_refresh = tk.Button(
            title_frame,
            text="⟳ Rafraîchir",
            font=("Arial", 10),
            bg='#3498DB',
            fg='white',
            padx=10,
            pady=5,
            command=self.load_data
        )
        btn_refresh.pack(side=tk.RIGHT)

        # Conteneur principal avec scrollbar
        main_container = tk.Frame(self, bg='#ECF0F1')
        main_container.pack(fill=tk.BOTH, expand=True)

        # Canvas pour le scroll
        canvas = tk.Canvas(main_container, bg='#ECF0F1', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='#ECF0F1')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Section Statistiques
        self.setup_statistics_section()

        # Section Balance
        self.setup_balance_section()

        # Section Dernières activités
        self.setup_recent_activities_section()

        # Section Alertes
        self.setup_alerts_section()

    def setup_statistics_section(self):
        """Section des statistiques principales"""
        stats_frame = tk.Frame(self.scrollable_frame, bg='#ECF0F1')
        stats_frame.pack(fill=tk.X, pady=10)

        # Titre de section
        section_title = tk.Label(
            stats_frame,
            text="Statistiques principales",
            font=("Arial", 14, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        section_title.pack(anchor=tk.W, pady=(0, 10))

        # Frame pour les cartes de stats
        cards_frame = tk.Frame(stats_frame, bg='#ECF0F1')
        cards_frame.pack(fill=tk.X)

        # Variables pour stocker les labels
        self.stats_labels = {}

        # Créer les cartes de statistiques
        stats_config = [
            ("adherents", "Adhérents", "#3498DB"),
            ("montant_adherent", "Montant/Adhérent", "#9B59B6"),
            ("total_collecte", "Total collecté", "#27AE60"),
            ("total_depense", "Total dépensé", "#E74C3C"),
            ("balance", "Balance actuelle", "#F39C12"),
            ("taux_recouvrement", "Taux recouvrement", "#16A085")
        ]

        for i, (key, label, color) in enumerate(stats_config):
            row = i // 3
            col = i % 3
            card = self.create_stat_card(cards_frame, label, "...", color)
            card['card'].grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            self.stats_labels[key] = card['value_label']

        # Configurer les colonnes pour qu'elles s'étendent
        for i in range(3):
            cards_frame.grid_columnconfigure(i, weight=1)

    def create_stat_card(self, parent, title, value, color):
        """Crée une carte de statistique"""
        card = tk.Frame(parent, bg='white', relief=tk.RAISED, borderwidth=1)
        card.pack_propagate(False)

        # Barre de couleur en haut
        color_bar = tk.Frame(card, bg=color, height=5)
        color_bar.pack(fill=tk.X)

        # Contenu
        content_frame = tk.Frame(card, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        title_label = tk.Label(
            content_frame,
            text=title,
            font=("Arial", 10),
            bg='white',
            fg='#7F8C8D'
        )
        title_label.pack(anchor=tk.W)

        value_label = tk.Label(
            content_frame,
            text=value,
            font=("Arial", 16, "bold"),
            bg='white',
            fg='#2C3E50'
        )
        value_label.pack(anchor=tk.W, pady=(5, 0))

        return {
            'card': card,
            'title_label': title_label,
            'value_label': value_label
        }

    def setup_balance_section(self):
        """Section de la balance"""
        balance_frame = tk.Frame(self.scrollable_frame, bg='#ECF0F1')
        balance_frame.pack(fill=tk.X, pady=10)

        # Titre
        section_title = tk.Label(
            balance_frame,
            text="Balance",
            font=("Arial", 14, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        section_title.pack(anchor=tk.W, pady=(0, 10))

        # Card de balance
        card = tk.Frame(balance_frame, bg='white', relief=tk.RAISED, borderwidth=1)
        card.pack(fill=tk.X, padx=5, pady=5)

        content = tk.Frame(card, bg='white')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Progress bar pour la balance
        self.balance_label = tk.Label(
            content,
            text=f"Balance: 0 / 0 {CURRENCY_SYMBOL}",
            font=("Arial", 12, "bold"),
            bg='white',
            fg='#2C3E50'
        )
        self.balance_label.pack(anchor=tk.W, pady=(0, 10))

        self.balance_progress = ttk.Progressbar(
            content,
            length=400,
            mode='determinate'
        )
        self.balance_progress.pack(fill=tk.X, pady=(0, 5))

        self.balance_percent_label = tk.Label(
            content,
            text="0%",
            font=("Arial", 10),
            bg='white',
            fg='#7F8C8D'
        )
        self.balance_percent_label.pack(anchor=tk.W)

    def setup_recent_activities_section(self):
        """Section des dernières activités"""
        activities_frame = tk.Frame(self.scrollable_frame, bg='#ECF0F1')
        activities_frame.pack(fill=tk.X, pady=10)

        # Titre
        section_title = tk.Label(
            activities_frame,
            text="Dernières activités",
            font=("Arial", 14, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        section_title.pack(anchor=tk.W, pady=(0, 10))

        # Frame pour contributions et dépenses côte à côte
        activities_container = tk.Frame(activities_frame, bg='#ECF0F1')
        activities_container.pack(fill=tk.X)

        # Dernières contributions
        contrib_frame = tk.Frame(activities_container, bg='white', relief=tk.RAISED, borderwidth=1)
        contrib_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 2.5))

        contrib_title = tk.Label(
            contrib_frame,
            text="Dernières contributions",
            font=("Arial", 11, "bold"),
            bg='white',
            fg='#2C3E50'
        )
        contrib_title.pack(anchor=tk.W, padx=15, pady=(10, 5))

        self.contrib_listbox = tk.Listbox(
            contrib_frame,
            height=5,
            font=("Arial", 9),
            bg='white',
            relief=tk.FLAT
        )
        self.contrib_listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        # Dernières dépenses
        depense_frame = tk.Frame(activities_container, bg='white', relief=tk.RAISED, borderwidth=1)
        depense_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(2.5, 5))

        depense_title = tk.Label(
            depense_frame,
            text="Dernières dépenses",
            font=("Arial", 11, "bold"),
            bg='white',
            fg='#2C3E50'
        )
        depense_title.pack(anchor=tk.W, padx=15, pady=(10, 5))

        self.depense_listbox = tk.Listbox(
            depense_frame,
            height=5,
            font=("Arial", 9),
            bg='white',
            relief=tk.FLAT
        )
        self.depense_listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

    def setup_alerts_section(self):
        """Section des alertes"""
        alerts_frame = tk.Frame(self.scrollable_frame, bg='#ECF0F1')
        alerts_frame.pack(fill=tk.X, pady=10)

        # Titre
        section_title = tk.Label(
            alerts_frame,
            text="Alertes",
            font=("Arial", 14, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        )
        section_title.pack(anchor=tk.W, pady=(0, 10))

        self.alerts_container = tk.Frame(alerts_frame, bg='#ECF0F1')
        self.alerts_container.pack(fill=tk.X)

    def load_data(self):
        """Charge les données du dashboard"""
        try:
            if not self.annee_active:
                return

            # Récupérer les statistiques
            stats = StatistiqueService.get_statistiques_dashboard(self.annee_active.id)

            if stats:
                # Mettre à jour les statistiques
                self.stats_labels['adherents'].config(
                    text=f"{stats['nombre_adherents']}"
                )
                self.stats_labels['montant_adherent'].config(
                    text=f"{stats['montant_par_adherent']:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')
                )
                self.stats_labels['total_collecte'].config(
                    text=f"{stats['total_contributions_payees']:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')
                )
                self.stats_labels['total_depense'].config(
                    text=f"{stats['total_depenses']:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')
                )
                self.stats_labels['balance'].config(
                    text=f"{stats['balance_actuelle']:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')
                )
                self.stats_labels['taux_recouvrement'].config(
                    text=f"{stats['taux_recouvrement']:.1f}%"
                )

                # Mettre à jour la balance
                balance_actuelle = stats['balance_actuelle']
                balance_cible = stats['balance_cible']
                pourcentage = (balance_actuelle / balance_cible * 100) if balance_cible > 0 else 0

                self.balance_label.config(
                    text=f"Balance: {balance_actuelle:,.0f} / {balance_cible:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')
                )
                self.balance_progress['value'] = min(100, pourcentage)
                self.balance_percent_label.config(text=f"{pourcentage:.1f}%")

                # Charger les dernières contributions
                self.load_recent_contributions()

                # Charger les dernières dépenses
                self.load_recent_depenses()

                # Charger les alertes
                self.load_alerts()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des données:\n{str(e)}")

    def load_recent_contributions(self):
        """Charge les derniers paiements"""
        try:
            self.contrib_listbox.delete(0, tk.END)
            contributions = ContributionService.get_dernieres_contributions(
                limit=5,
                annee=self.annee_active.annee
            )

            if contributions:
                for contrib in contributions:
                    adherent = contrib.get_adherent()
                    text = f"{adherent.get_nom_complet()} - {contrib.montant:,.0f} {CURRENCY_SYMBOL} - {contrib.date_paiement}"
                    self.contrib_listbox.insert(tk.END, text.replace(',', ' '))
            else:
                self.contrib_listbox.insert(tk.END, "Aucun paiement recent")

        except Exception as e:
            self.contrib_listbox.insert(tk.END, f"Erreur: {str(e)}")

    def load_recent_depenses(self):
        """Charge les dernières dépenses"""
        try:
            self.depense_listbox.delete(0, tk.END)
            depenses = DepenseService.get_dernieres_depenses(
                limit=5,
                annee_id=self.annee_active.id
            )

            if depenses:
                for depense in depenses:
                    nom_defunt = depense.get_nom_defunt()
                    text = f"{nom_defunt} - {depense.montant:,.0f} {CURRENCY_SYMBOL} - {depense.date_deces}"
                    self.depense_listbox.insert(tk.END, text.replace(',', ' '))
            else:
                self.depense_listbox.insert(tk.END, "Aucune dépense récente")

        except Exception as e:
            self.depense_listbox.insert(tk.END, f"Erreur: {str(e)}")

    def load_alerts(self):
        """Charge les alertes"""
        try:
            # Effacer les alertes existantes
            for widget in self.alerts_container.winfo_children():
                widget.destroy()

            # Récupérer les alertes
            alerts_data = StatistiqueService.get_alertes(self.annee_active.id)

            if alerts_data['nombre_alertes'] == 0:
                # Afficher message "Aucune alerte"
                no_alert = tk.Label(
                    self.alerts_container,
                    text="✓ Aucune alerte",
                    font=("Arial", 11),
                    bg='#27AE60',
                    fg='white',
                    padx=15,
                    pady=10
                )
                no_alert.pack(fill=tk.X, padx=5, pady=2)
            else:
                # Afficher les alertes
                for alert in alerts_data['alertes']:
                    color = {
                        'critique': '#E74C3C',
                        'warning': '#F39C12',
                        'info': '#3498DB'
                    }.get(alert['niveau'], '#95A5A6')

                    alert_label = tk.Label(
                        self.alerts_container,
                        text=f"⚠ {alert['message']}",
                        font=("Arial", 11),
                        bg=color,
                        fg='white',
                        padx=15,
                        pady=10
                    )
                    alert_label.pack(fill=tk.X, padx=5, pady=2)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des alertes:\n{str(e)}")
