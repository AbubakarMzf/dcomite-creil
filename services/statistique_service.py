"""
Service de calcul des statistiques
Logique metier pour les statistiques et calculs (base sur appels/cotisations)
"""
from models.adherent import Adherent
from models.appel import AppelDeFonds
from models.cotisation import Cotisation
from services.depense_service import DepenseService
from database.db_manager import DatabaseManager
from config import CURRENCY_SYMBOL


class StatistiqueService:
    """Service pour le calcul des statistiques"""

    @staticmethod
    def get_statistiques_dashboard():
        """
        Recupere toutes les statistiques pour le tableau de bord

        Returns:
            Dictionnaire avec toutes les statistiques
        """
        db = DatabaseManager()

        # Nombre d'adherents actifs
        adherents = Adherent.get_all(actif_only=True)
        nb_adherents_actifs = len(adherents)

        # Nombre d'appels ouverts
        appels_ouverts = AppelDeFonds.get_ouverts()
        nb_appels_ouverts = len(appels_ouverts)

        # Total collecte (toutes cotisations confondues)
        row = db.fetch_one("""
            SELECT COALESCE(SUM(montant_paye), 0) as total
            FROM cotisations
        """)
        total_collecte = row['total'] if row else 0

        # Total depenses (toutes annees)
        row = db.fetch_one("""
            SELECT COALESCE(SUM(montant), 0) as total
            FROM depenses
        """)
        total_depenses = row['total'] if row else 0

        # Balance globale
        balance_globale = total_collecte - total_depenses

        # Taux de recouvrement global
        row = db.fetch_one("""
            SELECT COALESCE(SUM(montant_du), 0) as total_attendu,
                   COALESCE(SUM(montant_paye), 0) as total_paye
            FROM cotisations
        """)
        total_attendu = row['total_attendu'] if row else 0
        total_paye = row['total_paye'] if row else 0
        taux_recouvrement = (total_paye / total_attendu * 100) if total_attendu > 0 else 0

        # Nombre de cotisations impayees
        row = db.fetch_one("""
            SELECT COUNT(*) as nombre
            FROM cotisations WHERE statut != 'paye'
        """)
        nb_cotisations_impayees = row['nombre'] if row else 0

        return {
            'nb_adherents_actifs': nb_adherents_actifs,
            'nb_appels_ouverts': nb_appels_ouverts,
            'total_collecte': total_collecte,
            'total_depenses': total_depenses,
            'balance_globale': balance_globale,
            'taux_recouvrement': taux_recouvrement,
            'total_attendu': total_attendu,
            'nb_cotisations_impayees': nb_cotisations_impayees
        }

    @staticmethod
    def get_alertes():
        """
        Recupere les alertes globales

        Returns:
            Dictionnaire avec les alertes
        """
        alertes = []
        db = DatabaseManager()

        # Alerte: Appels ouverts avec taux faible (< 50%)
        appels_ouverts = AppelDeFonds.get_ouverts()
        for appel in appels_ouverts:
            stats = appel.get_stats()
            if stats['taux'] < 50 and stats['total'] > 0:
                alertes.append({
                    'type': 'taux_faible',
                    'niveau': 'warning',
                    'message': f"Appel {appel.annee} ({appel.description or 'Sans description'}) : "
                               f"taux de recouvrement {stats['taux']:.0f}%"
                })

        # Alerte: Cotisations totalement impayees
        row = db.fetch_one("""
            SELECT COUNT(*) as nombre
            FROM cotisations WHERE statut = 'non_paye'
        """)
        nb_non_paye = row['nombre'] if row else 0
        if nb_non_paye > 0:
            alertes.append({
                'type': 'cotisations_impayees',
                'niveau': 'info',
                'message': f"{nb_non_paye} cotisation(s) totalement impayee(s)"
            })

        # Alerte: Adherents avec frais d'entree impayes
        row = db.fetch_one("""
            SELECT COUNT(*) as nombre
            FROM adherents WHERE frais_entree > 0 AND frais_entree_paye = 0 AND actif = 1
        """)
        nb_frais_impayes = row['nombre'] if row else 0
        if nb_frais_impayes > 0:
            alertes.append({
                'type': 'frais_entree_impayes',
                'niveau': 'info',
                'message': f"{nb_frais_impayes} adherent(s) avec frais d'entree impayes"
            })

        # Alerte: Balance negative
        stats = StatistiqueService.get_statistiques_dashboard()
        if stats['balance_globale'] < 0:
            alertes.append({
                'type': 'balance_negative',
                'niveau': 'critique',
                'message': f"Balance globale negative : {stats['balance_globale']:.2f} {CURRENCY_SYMBOL}"
            })

        return {
            'nombre_alertes': len(alertes),
            'alertes': alertes
        }
