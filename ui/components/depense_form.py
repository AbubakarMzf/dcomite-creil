"""
Formulaire de depense
Enregistrement d'une depense liee a un deces
Deux sections : infos deces + detail des frais
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.adherent import Adherent
from models.depense import Depense
from datetime import datetime
from config import RELATIONS, CURRENCY_SYMBOL, POSTES_DEPENSES


class DepenseForm(tk.Toplevel):
    """Formulaire d'enregistrement de depense (deces)"""

    def __init__(self, parent, annee):
        super().__init__(parent)

        self.title("Nouvelle depense - Deces")
        self.geometry("520x750")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.annee = annee
        self.result = None
        self.poste_entries = {}

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
        # Canvas scrollable
        canvas = tk.Canvas(self, bg='#ECF0F1', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#ECF0F1')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Mousewheel scroll
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        main_frame = tk.Frame(scrollable_frame, bg='#ECF0F1')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Titre
        tk.Label(
            main_frame,
            text=f"Nouvelle depense - Annee {self.annee.annee}",
            font=("Arial", 14, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50'
        ).pack(pady=(0, 15))

        # ============ SECTION 1 : DECES ============
        deces_frame = tk.LabelFrame(
            main_frame,
            text=" Informations sur le deces ",
            font=("Arial", 11, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50',
            padx=10,
            pady=10
        )
        deces_frame.pack(fill=tk.X, pady=(0, 15))

        # Qui est decede ?
        tk.Label(
            deces_frame,
            text="Qui est decede ? *",
            font=("Arial", 10, "bold"),
            bg='#ECF0F1'
        ).pack(anchor='w', pady=(0, 5))

        self.type_defunt_var = tk.IntVar(value=1)

        type_frame = tk.Frame(deces_frame, bg='#ECF0F1')
        type_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Radiobutton(
            type_frame,
            text="L'adherent lui-meme",
            variable=self.type_defunt_var,
            value=1,
            font=("Arial", 10),
            bg='#ECF0F1',
            command=self.on_type_defunt_change
        ).pack(anchor='w')

        tk.Radiobutton(
            type_frame,
            text="Un proche de l'adherent",
            variable=self.type_defunt_var,
            value=0,
            font=("Arial", 10),
            bg='#ECF0F1',
            command=self.on_type_defunt_change
        ).pack(anchor='w')

        # Selection de l'adherent
        tk.Label(
            deces_frame,
            text="Adherent *",
            font=("Arial", 10, "bold"),
            bg='#ECF0F1'
        ).pack(anchor='w', pady=(0, 5))

        self.adherent_var = tk.StringVar()
        self.adherent_combo = ttk.Combobox(
            deces_frame,
            textvariable=self.adherent_var,
            font=("Arial", 11),
            state='readonly'
        )
        self.adherent_combo.pack(fill=tk.X, pady=(0, 10))
        self.load_adherents()

        # Section proche (masquable)
        self.proche_frame = tk.Frame(deces_frame, bg='#ECF0F1')

        tk.Label(
            self.proche_frame,
            text="Nom du defunt *",
            font=("Arial", 10, "bold"),
            bg='#ECF0F1'
        ).pack(anchor='w', pady=(0, 5))

        self.defunt_nom_entry = tk.Entry(
            self.proche_frame,
            font=("Arial", 11)
        )
        self.defunt_nom_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            self.proche_frame,
            text="Relation avec l'adherent *",
            font=("Arial", 10, "bold"),
            bg='#ECF0F1'
        ).pack(anchor='w', pady=(0, 5))

        self.relation_var = tk.StringVar()
        relation_combo = ttk.Combobox(
            self.proche_frame,
            textvariable=self.relation_var,
            values=RELATIONS,
            font=("Arial", 11),
            state='readonly'
        )
        relation_combo.pack(fill=tk.X, pady=(0, 5))

        # Initialement cache (defunt = adherent par defaut)
        self.on_type_defunt_change()

        # Date du deces
        tk.Label(
            deces_frame,
            text="Date du deces *",
            font=("Arial", 10, "bold"),
            bg='#ECF0F1'
        ).pack(anchor='w', pady=(5, 5))

        self.date_entry = tk.Entry(deces_frame, font=("Arial", 11))
        self.date_entry.pack(fill=tk.X, pady=(0, 10))
        self.date_entry.insert(0, datetime.now().strftime('%d/%m/%Y'))

        # Pays de destination
        tk.Label(
            deces_frame,
            text="Pays de destination (lieu d'enterrement)",
            font=("Arial", 10),
            bg='#ECF0F1'
        ).pack(anchor='w', pady=(0, 5))

        self.pays_entry = tk.Entry(deces_frame, font=("Arial", 11))
        self.pays_entry.pack(fill=tk.X)

        # ============ SECTION 2 : FRAIS ============
        frais_frame = tk.LabelFrame(
            main_frame,
            text=" Detail des frais ",
            font=("Arial", 11, "bold"),
            bg='#ECF0F1',
            fg='#2C3E50',
            padx=10,
            pady=10
        )
        frais_frame.pack(fill=tk.X, pady=(0, 15))

        # Creer un champ pour chaque poste de depense
        for key, label in POSTES_DEPENSES.items():
            row_frame = tk.Frame(frais_frame, bg='#ECF0F1')
            row_frame.pack(fill=tk.X, pady=2)

            tk.Label(
                row_frame,
                text=f"{label} ({CURRENCY_SYMBOL})",
                font=("Arial", 10),
                bg='#ECF0F1',
                width=22,
                anchor='w'
            ).pack(side=tk.LEFT)

            entry = tk.Entry(row_frame, font=("Arial", 11), width=15)
            entry.pack(side=tk.RIGHT)
            entry.insert(0, "0")
            entry.bind('<KeyRelease>', lambda e: self.update_total())
            self.poste_entries[key] = entry

        # Total
        total_frame = tk.Frame(frais_frame, bg='#ECF0F1')
        total_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(
            total_frame,
            text="TOTAL",
            font=("Arial", 11, "bold"),
            bg='#ECF0F1',
            fg='#E74C3C',
            width=22,
            anchor='w'
        ).pack(side=tk.LEFT)

        self.total_label = tk.Label(
            total_frame,
            text=f"0 {CURRENCY_SYMBOL}",
            font=("Arial", 11, "bold"),
            bg='#ECF0F1',
            fg='#E74C3C'
        )
        self.total_label.pack(side=tk.RIGHT)

        # Notes
        tk.Label(
            main_frame,
            text="Notes",
            font=("Arial", 10),
            bg='#ECF0F1'
        ).pack(anchor='w', pady=(0, 5))

        self.notes_text = tk.Text(main_frame, font=("Arial", 10), height=3)
        self.notes_text.pack(fill=tk.X, pady=(0, 15))

        # Boutons
        buttons_frame = tk.Frame(main_frame, bg='#ECF0F1')
        buttons_frame.pack(fill=tk.X)

        tk.Button(
            buttons_frame,
            text="Enregistrer",
            font=("Arial", 11, "bold"),
            bg='#E74C3C',
            fg='white',
            padx=20,
            pady=10,
            command=self.on_save
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        tk.Button(
            buttons_frame,
            text="Annuler",
            font=("Arial", 11),
            bg='#95A5A6',
            fg='white',
            padx=20,
            pady=10,
            command=self.on_cancel
        ).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))

    def load_adherents(self):
        """Charge la liste des adherents actifs"""
        try:
            adherents = Adherent.get_all(actif_only=True)
            adherents_list = [
                f"{a.id} - {a.get_nom_complet()}" for a in adherents
            ]
            self.adherent_combo['values'] = adherents_list
            if adherents_list:
                self.adherent_combo.current(0)
        except:
            pass

    def on_type_defunt_change(self):
        """Gere le changement du type de defunt"""
        if self.type_defunt_var.get() == 1:
            # Defunt = adherent -> cacher les champs proche
            self.proche_frame.pack_forget()
        else:
            # Defunt = proche -> afficher les champs
            self.proche_frame.pack(fill=tk.X, pady=(0, 5))

    def update_total(self):
        """Met a jour le total des frais"""
        total = 0
        for key, entry in self.poste_entries.items():
            try:
                val = float(entry.get().strip() or 0)
                total += val
            except ValueError:
                pass
        self.total_label.config(
            text=f"{total:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')
        )

    def get_poste_value(self, key):
        """Recupere la valeur d'un poste de frais"""
        try:
            return float(self.poste_entries[key].get().strip() or 0)
        except ValueError:
            return 0

    def validate_fields(self):
        """Valide les champs"""
        # Adherent
        if not self.adherent_var.get():
            messagebox.showerror("Erreur", "Veuillez selectionner un adherent")
            return False

        # Si proche : nom et relation obligatoires
        if self.type_defunt_var.get() == 0:
            if not self.defunt_nom_entry.get().strip():
                messagebox.showerror("Erreur", "Le nom du defunt est obligatoire")
                self.defunt_nom_entry.focus()
                return False
            if not self.relation_var.get():
                messagebox.showerror("Erreur", "La relation est obligatoire")
                return False

        # Date
        date_str = self.date_entry.get().strip()
        if not date_str:
            messagebox.showerror("Erreur", "La date du deces est obligatoire")
            return False
        try:
            datetime.strptime(date_str, '%d/%m/%Y')
        except ValueError:
            messagebox.showerror("Erreur", "Format de date invalide (JJ/MM/AAAA)")
            return False

        # Au moins un poste > 0
        total = sum(self.get_poste_value(k) for k in POSTES_DEPENSES)
        if total <= 0:
            messagebox.showerror("Erreur", "Le montant total doit etre positif")
            return False

        # Verifier que les valeurs sont positives
        for key, label in POSTES_DEPENSES.items():
            val = self.get_poste_value(key)
            if val < 0:
                messagebox.showerror("Erreur", f"{label} ne peut pas etre negatif")
                return False

        return True

    def on_save(self):
        """Enregistre la depense"""
        if not self.validate_fields():
            return

        try:
            # Recuperer l'adherent
            adherent_str = self.adherent_var.get()
            adherent_id = int(adherent_str.split(' - ')[0])

            defunt_est_adherent = self.type_defunt_var.get()

            # Verifier que l'adherent est actif si c'est lui le defunt
            if defunt_est_adherent:
                adherent = Adherent.get_by_id(adherent_id)
                if not adherent or not adherent.actif:
                    messagebox.showerror(
                        "Erreur",
                        "Cet adherent est deja inactif. "
                        "Impossible de l'enregistrer comme decede."
                    )
                    return

            # Date
            date_str = self.date_entry.get().strip()
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            date_deces = date_obj.strftime('%Y-%m-%d')

            # Infos proche
            defunt_nom = None
            defunt_relation = None
            if not defunt_est_adherent:
                defunt_nom = self.defunt_nom_entry.get().strip()
                defunt_relation = self.relation_var.get()

            pays_destination = self.pays_entry.get().strip() or None
            notes = self.notes_text.get('1.0', tk.END).strip() or None

            # Creer la depense
            depense = Depense.create(
                annee_id=self.annee.id,
                adherent_id=adherent_id,
                defunt_est_adherent=defunt_est_adherent,
                date_deces=date_deces,
                defunt_nom=defunt_nom,
                defunt_relation=defunt_relation,
                pays_destination=pays_destination,
                transport_services=self.get_poste_value('transport_services'),
                billet_avion=self.get_poste_value('billet_avion'),
                imam=self.get_poste_value('imam'),
                mairie=self.get_poste_value('mairie'),
                autre1=self.get_poste_value('autre1'),
                autre2=self.get_poste_value('autre2'),
                autre3=self.get_poste_value('autre3'),
                notes=notes
            )

            # Generer le PDF
            try:
                from services.pdf_service import PdfService
                PdfService.generer_pdf_depense(depense)
            except Exception as pdf_err:
                messagebox.showwarning(
                    "PDF",
                    f"La depense a ete enregistree mais le PDF n'a pas pu etre genere:\n{str(pdf_err)}"
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
