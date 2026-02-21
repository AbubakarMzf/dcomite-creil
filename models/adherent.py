"""
Modele Adherent
Represente un adherent de la tontine
"""
from database.db_manager import DatabaseManager


class Adherent:
    """Modele representant un adherent"""

    def __init__(self, id, nom, prenom, telephone=None, email=None,
                 adresse=None, date_entree=None, date_sortie=None, actif=1,
                 frais_entree=0, frais_entree_paye=1,
                 notes=None, created_at=None, updated_at=None):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.telephone = telephone
        self.email = email
        self.adresse = adresse
        self.date_entree = date_entree
        self.date_sortie = date_sortie
        self.actif = actif
        self.frais_entree = frais_entree or 0
        self.frais_entree_paye = frais_entree_paye
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def create(nom, prenom, telephone=None, email=None, adresse=None,
               date_entree=None, date_sortie=None, actif=1,
               frais_entree=0, frais_entree_paye=1, notes=None):
        """Cree un nouvel adherent et log l'inscription dans l'historique"""
        from models.historique import Historique
        db = DatabaseManager()

        # Determiner le statut frais_entree_paye
        if not frais_entree or frais_entree <= 0:
            frais_entree = 0
            frais_entree_paye = 1  # Pas de frais = considere comme paye
        else:
            frais_entree_paye = 0  # Frais definis = impaye par defaut

        query = """
            INSERT INTO adherents (nom, prenom, telephone, email, adresse,
                                  date_entree, date_sortie, actif,
                                  frais_entree, frais_entree_paye, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (nom, prenom, telephone, email, adresse,
                  date_entree, date_sortie, actif,
                  frais_entree, frais_entree_paye, notes)

        cursor = db.execute_query(query, params)
        adherent_id = cursor.lastrowid

        # Logger l'inscription
        Historique.log(adherent_id, 'inscription',
                       f"Inscription de {prenom} {nom}")

        if frais_entree > 0:
            Historique.log(adherent_id, 'frais_entree',
                           f"Frais d'entree : {frais_entree} EUR (impaye)",
                           montant=frais_entree)

        return Adherent.get_by_id(adherent_id)

    @staticmethod
    def get_by_id(adherent_id):
        db = DatabaseManager()
        row = db.fetch_one("SELECT * FROM adherents WHERE id = ?", (adherent_id,))
        if row:
            return Adherent._from_row(row)
        return None

    @staticmethod
    def get_all(actif_only=True):
        db = DatabaseManager()
        if actif_only:
            query = "SELECT * FROM adherents WHERE actif = 1 ORDER BY nom, prenom"
        else:
            query = "SELECT * FROM adherents ORDER BY nom, prenom"
        rows = db.fetch_all(query)
        return [Adherent._from_row(row) for row in rows]

    @staticmethod
    def search(keyword):
        db = DatabaseManager()
        query = """
            SELECT * FROM adherents
            WHERE nom LIKE ? OR prenom LIKE ? OR telephone LIKE ?
            ORDER BY nom, prenom
        """
        search_term = f"%{keyword}%"
        rows = db.fetch_all(query, (search_term, search_term, search_term))
        return [Adherent._from_row(row) for row in rows]

    def update(self, **kwargs):
        db = DatabaseManager()
        valid_fields = ['nom', 'prenom', 'telephone', 'email', 'adresse',
                        'date_entree', 'date_sortie', 'actif',
                        'frais_entree', 'frais_entree_paye', 'notes']
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
        query = f"UPDATE adherents SET {', '.join(updates)} WHERE id = ?"
        db.execute_query(query, params)
        return True

    def delete(self):
        db = DatabaseManager()
        db.execute_query("DELETE FROM adherents WHERE id = ?", (self.id,))
        return True

    def get_contributions(self, annee=None):
        from models.contribution import Contribution
        return Contribution.get_by_adherent(self.id, annee)

    def get_total_paye(self, annee=None):
        from models.contribution import Contribution
        return Contribution.get_total_by_adherent(self.id, annee)

    def get_cotisations(self):
        from models.cotisation import Cotisation
        return Cotisation.get_for_adherent(self.id)

    def get_cotisations_impayees(self):
        from models.cotisation import Cotisation
        return Cotisation.get_impayees_adherent(self.id)

    def get_historique(self):
        from models.historique import Historique
        return Historique.get_for_adherent(self.id)

    @staticmethod
    def _from_row(row):
        return Adherent(
            id=row['id'],
            nom=row['nom'],
            prenom=row['prenom'],
            telephone=row['telephone'],
            email=row['email'],
            adresse=row['adresse'],
            date_entree=row['date_entree'],
            date_sortie=row['date_sortie'],
            actif=row['actif'],
            frais_entree=row['frais_entree'],
            frais_entree_paye=row['frais_entree_paye'],
            notes=row['notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def to_dict(self):
        return {
            'id': self.id, 'nom': self.nom, 'prenom': self.prenom,
            'telephone': self.telephone, 'email': self.email,
            'adresse': self.adresse, 'date_entree': self.date_entree,
            'date_sortie': self.date_sortie, 'actif': self.actif,
            'frais_entree': self.frais_entree,
            'frais_entree_paye': self.frais_entree_paye,
            'notes': self.notes, 'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def get_nom_complet(self):
        return f"{self.prenom} {self.nom}"

    def __str__(self):
        return f"Adherent({self.id}: {self.get_nom_complet()})"

    def __repr__(self):
        return self.__str__()
