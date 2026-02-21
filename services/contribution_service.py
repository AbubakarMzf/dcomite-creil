"""
Service de gestion des contributions
Logique metier pour les contributions/paiements (base sur cotisations)
"""
from models.contribution import Contribution
from database.db_manager import DatabaseManager


class ContributionService:
    """Service pour la gestion des contributions"""

    @staticmethod
    def get_dernieres_contributions(limit=10):
        """
        Recupere les derniers paiements avec nom adherent

        Args:
            limit: Nombre maximum de paiements a retourner

        Returns:
            Liste de dictionnaires avec info paiement + adherent
        """
        db = DatabaseManager()
        query = """
            SELECT c.*, a.nom, a.prenom
            FROM contributions c
            JOIN adherents a ON c.adherent_id = a.id
            ORDER BY c.date_paiement DESC, c.created_at DESC
            LIMIT ?
        """
        rows = db.fetch_all(query, (limit,))
        results = []
        for row in rows:
            contrib = Contribution._from_row(row)
            contrib.nom = row['nom']
            contrib.prenom = row['prenom']
            results.append(contrib)
        return results

    @staticmethod
    def get_paiements_adherent(adherent_id):
        """
        Recupere tous les paiements d'un adherent

        Args:
            adherent_id: ID de l'adherent

        Returns:
            Liste de contributions
        """
        return Contribution.get_by_adherent(adherent_id)

    @staticmethod
    def get_total_paye_adherent(adherent_id):
        """
        Calcule le total paye par un adherent (toutes cotisations)

        Args:
            adherent_id: ID de l'adherent

        Returns:
            Montant total paye
        """
        return Contribution.get_total_by_adherent(adherent_id)
