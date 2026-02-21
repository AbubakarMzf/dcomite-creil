"""
Modele Depense
Represente une depense liee a un deces
"""
from database.db_manager import DatabaseManager
from config import POSTES_DEPENSES


class Depense:
    """Modele representant une depense (deces)"""

    POSTES = list(POSTES_DEPENSES.keys())

    def __init__(self, id, annee_id, adherent_id, defunt_est_adherent,
                 date_deces, montant=0, defunt_nom=None, defunt_relation=None,
                 pays_destination=None, transport_services=0, billet_avion=0,
                 imam=0, mairie=0, autre1=0, autre2=0, autre3=0,
                 notes=None, created_at=None, updated_at=None):
        self.id = id
        self.annee_id = annee_id
        self.adherent_id = adherent_id
        self.defunt_est_adherent = defunt_est_adherent
        self.defunt_nom = defunt_nom
        self.defunt_relation = defunt_relation
        self.date_deces = date_deces
        self.pays_destination = pays_destination
        self.transport_services = transport_services or 0
        self.billet_avion = billet_avion or 0
        self.imam = imam or 0
        self.mairie = mairie or 0
        self.autre1 = autre1 or 0
        self.autre2 = autre2 or 0
        self.autre3 = autre3 or 0
        self.montant = montant
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at

    def calculer_montant(self):
        """Calcule le montant total a partir des postes de frais"""
        return (self.transport_services + self.billet_avion + self.imam +
                self.mairie + self.autre1 + self.autre2 + self.autre3)

    @staticmethod
    def create(annee_id, adherent_id, defunt_est_adherent, date_deces,
               defunt_nom=None, defunt_relation=None, pays_destination=None,
               transport_services=0, billet_avion=0, imam=0, mairie=0,
               autre1=0, autre2=0, autre3=0, notes=None):
        """
        Cree une nouvelle depense (deces)

        Si defunt_est_adherent=1, l'adherent est passe en inactif.
        """
        db = DatabaseManager()

        # Calculer le montant total
        montant = ((transport_services or 0) + (billet_avion or 0) +
                   (imam or 0) + (mairie or 0) + (autre1 or 0) +
                   (autre2 or 0) + (autre3 or 0))

        query = """
            INSERT INTO depenses (annee_id, adherent_id, defunt_est_adherent,
                                  defunt_nom, defunt_relation, date_deces,
                                  pays_destination, transport_services,
                                  billet_avion, imam, mairie, autre1, autre2,
                                  autre3, montant, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (annee_id, adherent_id, defunt_est_adherent, defunt_nom,
                  defunt_relation, date_deces, pays_destination,
                  transport_services or 0, billet_avion or 0, imam or 0,
                  mairie or 0, autre1 or 0, autre2 or 0, autre3 or 0,
                  montant, notes)

        cursor = db.execute_query(query, params)
        depense_id = cursor.lastrowid

        # Si le defunt est l'adherent, le passer en inactif
        if defunt_est_adherent:
            from models.adherent import Adherent
            adherent = Adherent.get_by_id(adherent_id)
            if adherent and adherent.actif:
                adherent.update(actif=0, date_sortie=date_deces)

        # Recalculer la balance de l'annee
        from models.annee import Annee
        annee = Annee.get_by_id(annee_id)
        if annee:
            annee.recalculer_balance()

        return Depense.get_by_id(depense_id)

    @staticmethod
    def get_by_id(depense_id):
        """Recupere une depense par son ID"""
        db = DatabaseManager()
        query = "SELECT * FROM depenses WHERE id = ?"
        row = db.fetch_one(query, (depense_id,))

        if row:
            return Depense._from_row(row)
        return None

    @staticmethod
    def get_all_for_annee(annee_id):
        """Recupere toutes les depenses pour une annee"""
        db = DatabaseManager()
        query = """
            SELECT * FROM depenses
            WHERE annee_id = ?
            ORDER BY date_deces DESC
        """
        rows = db.fetch_all(query, (annee_id,))
        return [Depense._from_row(row) for row in rows]

    @staticmethod
    def get_all():
        """Recupere toutes les depenses"""
        db = DatabaseManager()
        query = "SELECT * FROM depenses ORDER BY date_deces DESC"
        rows = db.fetch_all(query)
        return [Depense._from_row(row) for row in rows]

    @staticmethod
    def get_by_date_range(annee_id, date_debut, date_fin):
        """Recupere les depenses pour une periode donnee"""
        db = DatabaseManager()
        query = """
            SELECT * FROM depenses
            WHERE annee_id = ? AND date_deces BETWEEN ? AND ?
            ORDER BY date_deces DESC
        """
        rows = db.fetch_all(query, (annee_id, date_debut, date_fin))
        return [Depense._from_row(row) for row in rows]

    def update(self, **kwargs):
        """Met a jour les informations de la depense"""
        db = DatabaseManager()

        valid_fields = ['adherent_id', 'defunt_est_adherent', 'defunt_nom',
                        'defunt_relation', 'date_deces', 'pays_destination',
                        'transport_services', 'billet_avion', 'imam',
                        'mairie', 'autre1', 'autre2', 'autre3',
                        'montant', 'notes']

        updates = []
        params = []

        for field, value in kwargs.items():
            if field in valid_fields:
                updates.append(f"{field} = ?")
                params.append(value)
                setattr(self, field, value)

        if not updates:
            return False

        params.append(self.id)
        query = f"UPDATE depenses SET {', '.join(updates)} WHERE id = ?"

        db.execute_query(query, params)

        # Recalculer la balance si le montant a change
        if 'montant' in kwargs or any(p in kwargs for p in Depense.POSTES):
            from models.annee import Annee
            annee = Annee.get_by_id(self.annee_id)
            if annee:
                annee.recalculer_balance()

        return True

    def delete(self):
        """Supprime la depense"""
        db = DatabaseManager()
        query = "DELETE FROM depenses WHERE id = ?"
        db.execute_query(query, (self.id,))

        # Recalculer la balance
        from models.annee import Annee
        annee = Annee.get_by_id(self.annee_id)
        if annee:
            annee.recalculer_balance()

        return True

    def get_adherent(self):
        """Recupere l'adherent lie a cette depense"""
        from models.adherent import Adherent
        return Adherent.get_by_id(self.adherent_id)

    def get_annee(self):
        """Recupere l'annee associee"""
        from models.annee import Annee
        return Annee.get_by_id(self.annee_id)

    def get_nom_defunt(self):
        """Retourne le nom du defunt (adherent ou proche)"""
        if self.defunt_est_adherent:
            adherent = self.get_adherent()
            return adherent.get_nom_complet() if adherent else "Inconnu"
        return self.defunt_nom or "Inconnu"

    @staticmethod
    def _from_row(row):
        """Cree une instance a partir d'une ligne de la base de donnees"""
        return Depense(
            id=row['id'],
            annee_id=row['annee_id'],
            adherent_id=row['adherent_id'],
            defunt_est_adherent=row['defunt_est_adherent'],
            defunt_nom=row['defunt_nom'],
            defunt_relation=row['defunt_relation'],
            date_deces=row['date_deces'],
            pays_destination=row['pays_destination'],
            transport_services=row['transport_services'],
            billet_avion=row['billet_avion'],
            imam=row['imam'],
            mairie=row['mairie'],
            autre1=row['autre1'],
            autre2=row['autre2'],
            autre3=row['autre3'],
            montant=row['montant'],
            notes=row['notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            'id': self.id,
            'annee_id': self.annee_id,
            'adherent_id': self.adherent_id,
            'defunt_est_adherent': self.defunt_est_adherent,
            'defunt_nom': self.defunt_nom,
            'defunt_relation': self.defunt_relation,
            'date_deces': self.date_deces,
            'pays_destination': self.pays_destination,
            'transport_services': self.transport_services,
            'billet_avion': self.billet_avion,
            'imam': self.imam,
            'mairie': self.mairie,
            'autre1': self.autre1,
            'autre2': self.autre2,
            'autre3': self.autre3,
            'montant': self.montant,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __str__(self):
        return (f"Depense(ID:{self.id}, Montant:{self.montant}, "
                f"Date:{self.date_deces})")

    def __repr__(self):
        return self.__str__()
