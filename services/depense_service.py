"""
Service de gestion des depenses
Logique metier pour les depenses (deces)
"""
from models.depense import Depense
from models.annee import Annee
from database.db_manager import DatabaseManager
from config import CURRENCY_SYMBOL


class DepenseService:
    """Service pour la gestion des depenses"""

    @staticmethod
    def get_total_depenses(annee_id):
        """Calcule le total des depenses pour une annee"""
        db = DatabaseManager()
        query = """
            SELECT COALESCE(SUM(montant), 0) as total
            FROM depenses
            WHERE annee_id = ?
        """
        row = db.fetch_one(query, (annee_id,))
        return row['total'] if row else 0

    @staticmethod
    def get_nombre_deces(annee_id):
        """Compte le nombre de deces pour une annee"""
        db = DatabaseManager()
        query = """
            SELECT COUNT(*) as nombre
            FROM depenses
            WHERE annee_id = ?
        """
        row = db.fetch_one(query, (annee_id,))
        return row['nombre'] if row else 0

    @staticmethod
    def get_depenses_par_mois(annee_id):
        """Recupere les depenses groupees par mois"""
        db = DatabaseManager()
        query = """
            SELECT strftime('%m', date_deces) as mois,
                   COUNT(*) as nombre,
                   SUM(montant) as total
            FROM depenses
            WHERE annee_id = ?
            GROUP BY mois
            ORDER BY mois
        """
        rows = db.fetch_all(query, (annee_id,))

        mois_noms = [
            'Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin',
            'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre'
        ]

        result = {}
        for i, nom in enumerate(mois_noms, 1):
            result[nom] = {'nombre': 0, 'total': 0}

        for row in rows:
            mois_num = int(row['mois'])
            mois_nom = mois_noms[mois_num - 1]
            result[mois_nom] = {
                'nombre': row['nombre'],
                'total': row['total']
            }

        return result

    @staticmethod
    def get_dernieres_depenses(limit=10, annee_id=None):
        """Recupere les dernieres depenses"""
        db = DatabaseManager()

        if annee_id:
            query = """
                SELECT * FROM depenses
                WHERE annee_id = ?
                ORDER BY date_deces DESC, created_at DESC
                LIMIT ?
            """
            rows = db.fetch_all(query, (annee_id, limit))
        else:
            query = """
                SELECT * FROM depenses
                ORDER BY date_deces DESC, created_at DESC
                LIMIT ?
            """
            rows = db.fetch_all(query, (limit,))

        return [Depense._from_row(row) for row in rows]

    @staticmethod
    def get_statistiques_depenses(annee_id):
        """Recupere les statistiques des depenses pour une annee"""
        total_depenses = DepenseService.get_total_depenses(annee_id)
        nombre_deces = DepenseService.get_nombre_deces(annee_id)

        return {
            'total_depenses': total_depenses,
            'nombre_deces': nombre_deces
        }

    @staticmethod
    def verifier_balance_suffisante(annee_id, montant_depense):
        """Verifie si la balance de l'annee est suffisante"""
        annee = Annee.get_by_id(annee_id)
        if not annee:
            return (False, 0, "Annee non trouvee")

        balance = annee.get_balance_actuelle()

        if balance >= montant_depense:
            return (True, balance, "Balance suffisante")
        else:
            deficit = montant_depense - balance
            return (
                False,
                balance,
                f"Balance insuffisante. Deficit: {deficit:.2f} {CURRENCY_SYMBOL}"
            )

    @staticmethod
    def get_depenses_adherent(adherent_id, annee_id=None):
        """Recupere toutes les depenses liees a un adherent"""
        db = DatabaseManager()

        if annee_id:
            query = """
                SELECT * FROM depenses
                WHERE adherent_id = ? AND annee_id = ?
                ORDER BY date_deces DESC
            """
            rows = db.fetch_all(query, (adherent_id, annee_id))
        else:
            query = """
                SELECT * FROM depenses
                WHERE adherent_id = ?
                ORDER BY date_deces DESC
            """
            rows = db.fetch_all(query, (adherent_id,))

        return [Depense._from_row(row) for row in rows]
