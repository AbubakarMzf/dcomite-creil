"""
Helpers Jinja2 : filtres et context processors
"""
from flask import request
from config import (
    CURRENCY_SYMBOL, ADMIN_IDS, PAYMENT_MODES,
    RELATIONS, POSTES_DEPENSES, APP_NAME, APP_VERSION
)
from models.annee import Annee
from datetime import datetime


def register_helpers(app):
    """Enregistre les filtres et context processors Jinja2."""

    @app.template_filter('format_montant')
    def format_montant(value):
        """Formate un nombre en devise : 1234.5 -> '1 234 EUR'"""
        if value is None:
            return f"0 {CURRENCY_SYMBOL}"
        return f"{value:,.0f} {CURRENCY_SYMBOL}".replace(',', ' ')

    @app.template_filter('format_date')
    def format_date(value):
        """Convertit YYYY-MM-DD en DD/MM/YYYY."""
        if not value:
            return ''
        try:
            date_obj = datetime.strptime(str(value), '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        except ValueError:
            return str(value)

    @app.template_filter('admin_name')
    def admin_name(admin_id):
        """Convertit un admin_id en nom."""
        if admin_id is None:
            return ''
        return ADMIN_IDS.get(int(admin_id), f'Admin {admin_id}')

    @app.context_processor
    def inject_globals():
        """Rend les donnees communes disponibles dans tous les templates."""
        annee_active = Annee.get_active()

        # Determiner la section active depuis le nom du blueprint
        section_map = {
            'dashboard': 'dashboard',
            'adherents': 'adherents',
            'appels': 'appels',
            'contributions': 'paiements',
            'depenses': 'depenses',
            'annees': 'annees',
        }
        active_section = section_map.get(request.blueprint, 'dashboard')

        return {
            'annee_active': annee_active,
            'active_section': active_section,
            'APP_NAME': APP_NAME,
            'APP_VERSION': APP_VERSION,
            'CURRENCY_SYMBOL': CURRENCY_SYMBOL,
            'PAYMENT_MODES': PAYMENT_MODES,
            'ADMIN_IDS': ADMIN_IDS,
            'RELATIONS': RELATIONS,
            'POSTES_DEPENSES': POSTES_DEPENSES,
        }
