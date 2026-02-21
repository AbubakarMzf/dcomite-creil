"""
Blueprint Dashboard - Page d'accueil avec statistiques
"""
from flask import Blueprint, render_template, redirect, url_for
from services.statistique_service import StatistiqueService
from services.contribution_service import ContributionService
from services.depense_service import DepenseService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def home():
    return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/dashboard')
def index():
    stats = StatistiqueService.get_statistiques_dashboard()
    alertes = StatistiqueService.get_alertes()

    # Dernieres contributions avec nom adherent
    contributions = ContributionService.get_dernieres_contributions(5)
    dernieres_contributions = []
    for c in contributions:
        nom = f"{c.prenom} {c.nom}" if hasattr(c, 'nom') else 'Inconnu'
        dernieres_contributions.append({
            'id': c.id,
            'adherent_nom': nom,
            'montant': c.montant,
            'date_paiement': c.date_paiement,
            'type_paiement': c.type_paiement
        })

    # Dernieres depenses
    depenses = DepenseService.get_dernieres_depenses(5)
    dernieres_depenses = []
    for d in depenses:
        dernieres_depenses.append({
            'id': d.id,
            'defunt_nom': d.get_nom_defunt(),
            'montant': d.montant,
            'date_deces': d.date_deces
        })

    return render_template('dashboard/index.html',
                           stats=stats,
                           alertes=alertes,
                           dernieres_contributions=dernieres_contributions,
                           dernieres_depenses=dernieres_depenses)
