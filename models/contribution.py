"""
Modele Contribution
Represente un paiement d'un adherent
"""
from database.db_manager import DatabaseManager


class Contribution:
    """Modele representant un paiement/contribution"""

    def __init__(self, id, adherent_id, montant, date_paiement,
                 cotisation_id=None, mode_paiement=None, reference_paiement=None,
                 admin_id=None, type_paiement='cotisation', notes=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.adherent_id = adherent_id
        self.cotisation_id = cotisation_id
        self.montant = montant
        self.date_paiement = date_paiement
        self.mode_paiement = mode_paiement
        self.reference_paiement = reference_paiement
        self.admin_id = admin_id
        self.type_paiement = type_paiement or 'cotisation'
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def create(adherent_id, montant, date_paiement, cotisation_id=None,
               mode_paiement=None, reference_paiement=None, admin_id=None,
               type_paiement='cotisation', notes=None):
        """Cree un nouveau paiement"""
        db = DatabaseManager()
        query = """
            INSERT INTO contributions (adherent_id, cotisation_id, montant,
                                      date_paiement, mode_paiement,
                                      reference_paiement, admin_id,
                                      type_paiement, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (adherent_id, cotisation_id, montant, date_paiement,
                  mode_paiement, reference_paiement, admin_id,
                  type_paiement, notes)
        cursor = db.execute_query(query, params)
        return Contribution.get_by_id(cursor.lastrowid)

    @staticmethod
    def get_by_id(contribution_id):
        db = DatabaseManager()
        row = db.fetch_one("SELECT * FROM contributions WHERE id = ?", (contribution_id,))
        if row:
            return Contribution._from_row(row)
        return None

    @staticmethod
    def get_by_adherent(adherent_id, annee=None):
        db = DatabaseManager()
        if annee:
            query = """
                SELECT * FROM contributions
                WHERE adherent_id = ? AND strftime('%Y', date_paiement) = ?
                ORDER BY date_paiement DESC
            """
            rows = db.fetch_all(query, (adherent_id, str(annee)))
        else:
            query = """
                SELECT * FROM contributions
                WHERE adherent_id = ?
                ORDER BY date_paiement DESC
            """
            rows = db.fetch_all(query, (adherent_id,))
        return [Contribution._from_row(row) for row in rows]

    @staticmethod
    def get_total_by_adherent(adherent_id, annee=None):
        db = DatabaseManager()
        if annee:
            query = """
                SELECT COALESCE(SUM(montant), 0) as total
                FROM contributions
                WHERE adherent_id = ? AND strftime('%Y', date_paiement) = ?
            """
            row = db.fetch_one(query, (adherent_id, str(annee)))
        else:
            query = """
                SELECT COALESCE(SUM(montant), 0) as total
                FROM contributions WHERE adherent_id = ?
            """
            row = db.fetch_one(query, (adherent_id,))
        return row['total'] if row else 0

    @staticmethod
    def get_all():
        db = DatabaseManager()
        query = """
            SELECT c.*, a.nom, a.prenom
            FROM contributions c
            JOIN adherents a ON c.adherent_id = a.id
            ORDER BY c.date_paiement DESC
        """
        rows = db.fetch_all(query)
        return [Contribution._from_row(row) for row in rows]

    @staticmethod
    def get_recent(limit=10):
        db = DatabaseManager()
        query = """
            SELECT c.*, a.nom, a.prenom
            FROM contributions c
            JOIN adherents a ON c.adherent_id = a.id
            ORDER BY c.date_paiement DESC
            LIMIT ?
        """
        rows = db.fetch_all(query, (limit,))
        return [Contribution._from_row(row) for row in rows]

    def update(self, **kwargs):
        db = DatabaseManager()
        valid_fields = ['montant', 'date_paiement', 'mode_paiement',
                        'reference_paiement', 'admin_id', 'notes']
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
        query = f"UPDATE contributions SET {', '.join(updates)} WHERE id = ?"
        db.execute_query(query, params)
        return True

    def delete(self):
        """Supprime la contribution et met a jour la cotisation si liee"""
        db = DatabaseManager()
        if self.cotisation_id:
            from models.cotisation import Cotisation
            cotisation = Cotisation.get_by_id(self.cotisation_id)
            if cotisation:
                nouveau_paye = max(0, cotisation.montant_paye - self.montant)
                if nouveau_paye >= cotisation.montant_du:
                    statut = 'paye'
                elif nouveau_paye > 0:
                    statut = 'partiel'
                else:
                    statut = 'non_paye'
                db.execute_query(
                    "UPDATE cotisations SET montant_paye = ?, statut = ? WHERE id = ?",
                    (nouveau_paye, statut, self.cotisation_id)
                )
        db.execute_query("DELETE FROM contributions WHERE id = ?", (self.id,))
        return True

    def get_adherent(self):
        from models.adherent import Adherent
        return Adherent.get_by_id(self.adherent_id)

    @staticmethod
    def _from_row(row):
        c = Contribution(
            id=row['id'],
            adherent_id=row['adherent_id'],
            cotisation_id=row['cotisation_id'],
            montant=row['montant'],
            date_paiement=row['date_paiement'],
            mode_paiement=row['mode_paiement'],
            reference_paiement=row['reference_paiement'],
            admin_id=row['admin_id'],
            type_paiement=row['type_paiement'],
            notes=row['notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        # Attach extra JOIN fields if present
        for field in ['nom', 'prenom']:
            try:
                setattr(c, field, row[field])
            except (IndexError, KeyError):
                pass
        return c

    def to_dict(self):
        return {
            'id': self.id, 'adherent_id': self.adherent_id,
            'cotisation_id': self.cotisation_id,
            'montant': self.montant, 'date_paiement': self.date_paiement,
            'mode_paiement': self.mode_paiement,
            'reference_paiement': self.reference_paiement,
            'admin_id': self.admin_id, 'type_paiement': self.type_paiement,
            'notes': self.notes, 'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __str__(self):
        return (f"Contribution(ID:{self.id}, Adherent:{self.adherent_id}, "
                f"Montant:{self.montant}, Date:{self.date_paiement})")

    def __repr__(self):
        return self.__str__()
