"""
Modele AppelDeFonds
Represente un appel de fond lance par un admin
"""
from database.db_manager import DatabaseManager


class AppelDeFonds:
    """Modele representant un appel de fond"""

    def __init__(self, id, annee, montant, description=None, admin_id=None,
                 date_lancement=None, cloture=0, created_at=None, updated_at=None):
        self.id = id
        self.annee = annee
        self.montant = montant
        self.description = description
        self.admin_id = admin_id
        self.date_lancement = date_lancement
        self.cloture = cloture
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def create(annee, montant, description=None, admin_id=None, date_lancement=None):
        """
        Cree un appel de fond et genere les cotisations pour tous les adherents actifs.
        """
        from models.adherent import Adherent
        from models.historique import Historique
        from datetime import date

        db = DatabaseManager()

        if not date_lancement:
            date_lancement = date.today().isoformat()

        # Creer l'appel
        query = """
            INSERT INTO appels_de_fonds (annee, montant, description, admin_id, date_lancement)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor = db.execute_query(query, (annee, montant, description, admin_id, date_lancement))
        appel_id = cursor.lastrowid

        # Generer une cotisation pour chaque adherent actif
        adherents = Adherent.get_all(actif_only=True)
        for adherent in adherents:
            db.execute_query(
                """INSERT INTO cotisations (appel_id, adherent_id, montant_du)
                   VALUES (?, ?, ?)""",
                (appel_id, adherent.id, montant)
            )
            Historique.log(
                adherent.id, 'paiement_cotisation',
                f"Appel de fond {annee} : {montant} EUR a payer",
                montant=montant, admin_id=admin_id
            )

        return AppelDeFonds.get_by_id(appel_id)

    @staticmethod
    def get_by_id(appel_id):
        db = DatabaseManager()
        row = db.fetch_one("SELECT * FROM appels_de_fonds WHERE id = ?", (appel_id,))
        if row:
            return AppelDeFonds._from_row(row)
        return None

    @staticmethod
    def get_all():
        """Recupere tous les appels (plus recent en premier)"""
        db = DatabaseManager()
        rows = db.fetch_all("SELECT * FROM appels_de_fonds ORDER BY date_lancement DESC")
        return [AppelDeFonds._from_row(row) for row in rows]

    @staticmethod
    def get_for_annee(annee):
        """Recupere les appels pour une annee donnee"""
        db = DatabaseManager()
        rows = db.fetch_all(
            "SELECT * FROM appels_de_fonds WHERE annee = ? ORDER BY date_lancement DESC",
            (annee,)
        )
        return [AppelDeFonds._from_row(row) for row in rows]

    @staticmethod
    def get_ouverts():
        """Recupere les appels non clotures"""
        db = DatabaseManager()
        rows = db.fetch_all(
            "SELECT * FROM appels_de_fonds WHERE cloture = 0 ORDER BY date_lancement DESC"
        )
        return [AppelDeFonds._from_row(row) for row in rows]

    def cloturer(self):
        """Cloture cet appel"""
        db = DatabaseManager()
        db.execute_query("UPDATE appels_de_fonds SET cloture = 1 WHERE id = ?", (self.id,))
        self.cloture = 1

    def get_stats(self):
        """Statistiques de cet appel : nb paye/partiel/non_paye, total collecte, taux"""
        db = DatabaseManager()
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN statut = 'paye' THEN 1 ELSE 0 END) as nb_paye,
                SUM(CASE WHEN statut = 'partiel' THEN 1 ELSE 0 END) as nb_partiel,
                SUM(CASE WHEN statut = 'non_paye' THEN 1 ELSE 0 END) as nb_non_paye,
                COALESCE(SUM(montant_paye), 0) as total_collecte,
                COALESCE(SUM(montant_du), 0) as total_attendu
            FROM cotisations
            WHERE appel_id = ?
        """
        row = db.fetch_one(query, (self.id,))
        total_attendu = row['total_attendu'] if row else 0
        total_collecte = row['total_collecte'] if row else 0
        taux = (total_collecte / total_attendu * 100) if total_attendu > 0 else 0

        return {
            'total': row['total'] if row else 0,
            'nb_paye': row['nb_paye'] if row else 0,
            'nb_partiel': row['nb_partiel'] if row else 0,
            'nb_non_paye': row['nb_non_paye'] if row else 0,
            'total_collecte': total_collecte,
            'total_attendu': total_attendu,
            'taux': taux
        }

    @staticmethod
    def _from_row(row):
        return AppelDeFonds(
            id=row['id'],
            annee=row['annee'],
            montant=row['montant'],
            description=row['description'],
            admin_id=row['admin_id'],
            date_lancement=row['date_lancement'],
            cloture=row['cloture'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
