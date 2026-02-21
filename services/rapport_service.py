"""
Service de generation de rapports
Logique metier pour les rapports
"""
from models.annee import Annee
from models.adherent import Adherent
from models.contribution import Contribution
from models.depense import Depense
from services.statistique_service import StatistiqueService
from services.contribution_service import ContributionService
from services.depense_service import DepenseService
from datetime import datetime
from config import CURRENCY_SYMBOL


class RapportService:
    """Service pour la generation de rapports"""

    @staticmethod
    def rapport_annuel(annee_id):
        """
        Genere un rapport annuel complet

        Args:
            annee_id: ID de l'annee

        Returns:
            Dictionnaire avec toutes les donnees du rapport
        """
        annee = Annee.get_by_id(annee_id)
        if not annee:
            raise ValueError(f"Annee avec ID {annee_id} non trouvee")

        # Statistiques generales
        stats = StatistiqueService.get_statistiques_dashboard(annee_id)

        # Tous les paiements de l'annee
        contributions = Contribution.get_all_for_year(annee.annee)

        # Depenses
        depenses = Depense.get_all_for_annee(annee_id)

        # Adherents non payes
        non_payes = ContributionService.get_adherents_non_payes(annee.annee)

        return {
            'annee': annee,
            'statistiques': stats,
            'contributions': contributions,
            'depenses': depenses,
            'adherents_non_payes': non_payes,
            'date_generation': datetime.now().strftime('%d/%m/%Y %H:%M')
        }

    @staticmethod
    def rapport_adherent(adherent_id, annee=None):
        """
        Genere un rapport pour un adherent

        Args:
            adherent_id: ID de l'adherent
            annee: Numero de l'annee (optionnel, toutes les annees si None)

        Returns:
            Dictionnaire avec les donnees du rapport
        """
        adherent = Adherent.get_by_id(adherent_id)
        if not adherent:
            raise ValueError(f"Adherent avec ID {adherent_id} non trouve")

        # Paiements de l'adherent
        paiements = Contribution.get_by_adherent(adherent_id, annee)
        total_paye = Contribution.get_total_by_adherent(adherent_id, annee)

        # Depenses liees a l'adherent
        depenses = DepenseService.get_depenses_adherent(adherent_id)

        return {
            'adherent': adherent,
            'paiements': paiements,
            'total_paye': total_paye,
            'depenses': depenses,
            'date_generation': datetime.now().strftime('%d/%m/%Y %H:%M')
        }

    @staticmethod
    def rapport_contributions(annee_id):
        """
        Genere un rapport des contributions/paiements

        Args:
            annee_id: ID de l'annee

        Returns:
            Dictionnaire avec les donnees du rapport
        """
        annee = Annee.get_by_id(annee_id)
        if not annee:
            raise ValueError(f"Annee avec ID {annee_id} non trouvee")

        # Resume par adherent
        resume = ContributionService.get_resume_adherents(annee.annee)

        # Statistiques
        stats = ContributionService.get_statistiques_paiements(annee.annee)

        return {
            'annee': annee,
            'resume_adherents': resume,
            'statistiques': stats,
            'date_generation': datetime.now().strftime('%d/%m/%Y %H:%M')
        }

    @staticmethod
    def rapport_depenses(annee_id, date_debut=None, date_fin=None):
        """
        Genere un rapport des depenses

        Args:
            annee_id: ID de l'annee
            date_debut: Date de debut (optionnel)
            date_fin: Date de fin (optionnel)

        Returns:
            Dictionnaire avec les donnees du rapport
        """
        annee = Annee.get_by_id(annee_id)
        if not annee:
            raise ValueError(f"Annee avec ID {annee_id} non trouvee")

        # Recuperer les depenses
        if date_debut and date_fin:
            depenses = Depense.get_by_date_range(annee_id, date_debut, date_fin)
        else:
            depenses = Depense.get_all_for_annee(annee_id)

        # Enrichir avec les informations des adherents
        depenses_enrichies = []
        for depense in depenses:
            adherent = depense.get_adherent()
            depenses_enrichies.append({
                'depense': depense,
                'adherent': adherent
            })

        # Statistiques
        stats = DepenseService.get_statistiques_depenses(annee_id)

        return {
            'annee': annee,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'depenses': depenses_enrichies,
            'statistiques': stats,
            'date_generation': datetime.now().strftime('%d/%m/%Y %H:%M')
        }

    @staticmethod
    def rapport_balance(annee_id):
        """
        Genere un rapport de balance

        Args:
            annee_id: ID de l'annee

        Returns:
            Dictionnaire avec les donnees du rapport
        """
        annee = Annee.get_by_id(annee_id)
        if not annee:
            raise ValueError(f"Annee avec ID {annee_id} non trouvee")

        # Statistiques
        stats = StatistiqueService.get_statistiques_dashboard(annee_id)

        # Derniers paiements
        derniers_paiements = ContributionService.get_dernieres_contributions(
            limit=20,
            annee=annee.annee
        )

        # Dernieres depenses
        dernieres_depenses = DepenseService.get_dernieres_depenses(
            limit=20,
            annee_id=annee_id
        )

        return {
            'annee': annee,
            'statistiques': stats,
            'derniers_paiements': derniers_paiements,
            'dernieres_depenses': dernieres_depenses,
            'date_generation': datetime.now().strftime('%d/%m/%Y %H:%M')
        }

    @staticmethod
    def rapport_adherents_non_payes(annee_id):
        """
        Genere un rapport des adherents n'ayant pas paye

        Args:
            annee_id: ID de l'annee

        Returns:
            Dictionnaire avec les donnees du rapport
        """
        annee = Annee.get_by_id(annee_id)
        if not annee:
            raise ValueError(f"Annee avec ID {annee_id} non trouvee")

        # Adherents non payes
        non_payes = ContributionService.get_adherents_non_payes(annee.annee)

        return {
            'annee': annee,
            'adherents_non_payes': non_payes,
            'nombre_non_payes': len(non_payes),
            'date_generation': datetime.now().strftime('%d/%m/%Y %H:%M')
        }

    @staticmethod
    def generer_resume_annuel(annee_id):
        """
        Genere un resume annuel concis

        Args:
            annee_id: ID de l'annee

        Returns:
            Dictionnaire avec le resume
        """
        stats = StatistiqueService.get_statistiques_dashboard(annee_id)
        if not stats:
            return None

        return {
            'titre': f"Resume Annee {stats['annee']}",
            'balance': {
                'cible': stats['balance_cible'],
                'actuelle': stats['balance_actuelle'],
                'pourcentage': (stats['balance_actuelle'] /
                               stats['balance_cible'] * 100)
                               if stats['balance_cible'] > 0 else 0
            },
            'contributions': {
                'total_paye': stats['total_contributions_payees'],
                'total_attendu': stats['total_contributions_attendues'],
                'taux_recouvrement': stats['taux_recouvrement']
            },
            'depenses': {
                'total': stats['total_depenses'],
                'nombre_deces': stats['nombre_deces']
            },
            'adherents': {
                'total': stats['nombre_adherents'],
                'non_payes': stats['nombre_adherents_non_payes'],
                'montant_par_adherent': stats['montant_par_adherent']
            }
        }

    @staticmethod
    def formater_montant(montant, devise=None):
        """
        Formate un montant avec separateurs de milliers

        Args:
            montant: Montant a formater
            devise: Devise (defaut: CURRENCY_SYMBOL de config)

        Returns:
            Montant formate
        """
        if devise is None:
            devise = CURRENCY_SYMBOL
        return f"{montant:,.2f} {devise}".replace(',', ' ')

    @staticmethod
    def formater_date(date_str, format_sortie='%d/%m/%Y'):
        """
        Formate une date

        Args:
            date_str: Date en format string
            format_sortie: Format de sortie desire

        Returns:
            Date formatee
        """
        if not date_str:
            return ''

        try:
            for format_entree in ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    date_obj = datetime.strptime(date_str, format_entree)
                    return date_obj.strftime(format_sortie)
                except ValueError:
                    continue
            return date_str
        except Exception:
            return date_str
