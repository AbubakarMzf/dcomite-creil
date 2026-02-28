"""
Modele Annee
Represente une annee (simplifiee - reference temporelle pour les depenses)
"""
from database.db_manager import DatabaseManager


class Annee:
    """Modele representant une annee"""

    def __init__(self, id, annee, active=0, created_at=None, updated_at=None):
        self.id = id
        self.annee = annee
        self.active = active
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def create(annee):
        """Cree une nouvelle annee"""
        db = DatabaseManager()
        query = "INSERT INTO annees (annee) VALUES (?)"
        cursor = db.execute_query(query, (annee,))
        return Annee.get_by_id(cursor.lastrowid)

    @staticmethod
    def get_by_id(annee_id):
        db = DatabaseManager()
        row = db.fetch_one("SELECT * FROM annees WHERE id = ?", (annee_id,))
        if row:
            return Annee._from_row(row)
        return None

    @staticmethod
    def get_active():
        db = DatabaseManager()
        row = db.fetch_one("SELECT * FROM annees WHERE active = 1")
        if row:
            return Annee._from_row(row)
        return None

    @staticmethod
    def get_by_year(year):
        db = DatabaseManager()
        row = db.fetch_one("SELECT * FROM annees WHERE annee = ?", (year,))
        if row:
            return Annee._from_row(row)
        return None

    @staticmethod
    def get_all():
        db = DatabaseManager()
        rows = db.fetch_all("SELECT * FROM annees ORDER BY annee DESC")
        return [Annee._from_row(row) for row in rows]

    def set_active(self):
        """Active cette annee et desactive toutes les autres"""
        db = DatabaseManager()
        db.execute_query("UPDATE annees SET active = 0")
        db.execute_query("UPDATE annees SET active = 1 WHERE id = ?", (self.id,))
        self.active = 1

    def get_total_depenses(self):
        """Total des depenses pour cette annee"""
        db = DatabaseManager()
        query = """
            SELECT COALESCE(SUM(montant), 0) as total
            FROM depenses WHERE annee_id = ?
        """
        row = db.fetch_one(query, (self.id,))
        return row['total'] if row else 0

    def get_nombre_depenses(self):
        """Nombre de depenses (deces) pour cette annee"""
        db = DatabaseManager()
        query = "SELECT COUNT(*) as nombre FROM depenses WHERE annee_id = ?"
        row = db.fetch_one(query, (self.id,))
        return row['nombre'] if row else 0

    def get_balance_actuelle(self):
        """Balance de l'annee = total cotisations collectees - total depenses"""
        db = DatabaseManager()
        row_collecte = db.fetch_one("""
            SELECT COALESCE(SUM(c.montant_paye), 0) as total
            FROM cotisations c
            JOIN appels_de_fonds a ON c.appel_id = a.id
            WHERE a.annee = ?
        """, (self.annee,))
        total_collecte = row_collecte['total'] if row_collecte else 0

        row_depenses = db.fetch_one(
            "SELECT COALESCE(SUM(montant), 0) as total FROM depenses WHERE annee_id = ?",
            (self.id,)
        )
        total_depenses = row_depenses['total'] if row_depenses else 0

        return total_collecte - total_depenses

    @staticmethod
    def _from_row(row):
        return Annee(
            id=row['id'],
            annee=row['annee'],
            active=row['active'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    def __str__(self):
        statut = "Active" if self.active else "Inactive"
        return f"Annee({self.annee} - {statut})"

    def __repr__(self):
        return self.__str__()
