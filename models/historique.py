"""
Modele Historique
Journal d'evenements par adherent
"""
from database.db_manager import DatabaseManager


class Historique:
    """Modele representant un evenement dans l'historique d'un adherent"""

    TYPES = [
        'inscription', 'frais_entree', 'paiement_cotisation',
        'activation', 'desactivation', 'deces', 'deces_proche',
        'modification'
    ]

    def __init__(self, id, adherent_id, type_evenement, description=None,
                 montant=None, admin_id=None, created_at=None):
        self.id = id
        self.adherent_id = adherent_id
        self.type_evenement = type_evenement
        self.description = description
        self.montant = montant
        self.admin_id = admin_id
        self.created_at = created_at

    @staticmethod
    def log(adherent_id, type_evenement, description=None, montant=None, admin_id=None):
        """Ajoute une entree dans l'historique"""
        db = DatabaseManager()
        query = """
            INSERT INTO historique (adherent_id, type_evenement, description, montant, admin_id)
            VALUES (?, ?, ?, ?, ?)
        """
        db.execute_query(query, (adherent_id, type_evenement, description, montant, admin_id))

    @staticmethod
    def get_for_adherent(adherent_id):
        """Recupere l'historique complet d'un adherent (plus recent en premier)"""
        db = DatabaseManager()
        query = """
            SELECT * FROM historique
            WHERE adherent_id = ?
            ORDER BY created_at DESC
        """
        rows = db.fetch_all(query, (adherent_id,))
        return [Historique._from_row(row) for row in rows]

    @staticmethod
    def get_recent(limit=20):
        """Recupere les derniers evenements globaux"""
        db = DatabaseManager()
        query = """
            SELECT h.*, a.nom, a.prenom
            FROM historique h
            JOIN adherents a ON h.adherent_id = a.id
            ORDER BY h.created_at DESC
            LIMIT ?
        """
        rows = db.fetch_all(query, (limit,))
        return [Historique._from_row(row) for row in rows]

    @staticmethod
    def _from_row(row):
        return Historique(
            id=row['id'],
            adherent_id=row['adherent_id'],
            type_evenement=row['type_evenement'],
            description=row['description'],
            montant=row['montant'],
            admin_id=row['admin_id'],
            created_at=row['created_at']
        )

    def get_icone(self):
        """Retourne l'icone Bootstrap pour ce type d'evenement"""
        icones = {
            'inscription': 'person-plus',
            'frais_entree': 'cash',
            'paiement_cotisation': 'check-circle',
            'activation': 'play-circle',
            'desactivation': 'pause-circle',
            'deces': 'heart',
            'deces_proche': 'heart',
            'modification': 'pencil',
        }
        return icones.get(self.type_evenement, 'circle')

    def get_couleur(self):
        """Retourne la couleur Bootstrap pour ce type d'evenement"""
        couleurs = {
            'inscription': 'primary',
            'frais_entree': 'info',
            'paiement_cotisation': 'success',
            'activation': 'success',
            'desactivation': 'warning',
            'deces': 'danger',
            'deces_proche': 'danger',
            'modification': 'secondary',
        }
        return couleurs.get(self.type_evenement, 'secondary')
