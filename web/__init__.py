"""
Application Flask pour DComite
Factory pattern pour creer l'application web
"""
import sys
import os

# Ajouter le repertoire racine du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from config import DATABASE_PATH, APP_NAME, APP_VERSION
from database.db_manager import DatabaseManager


def create_app():
    """Cree et configure l'application Flask."""

    # Initialiser le singleton DB avant tout import de blueprint
    db = DatabaseManager(DATABASE_PATH)
    db.create_tables()

    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )
    app.config['SECRET_KEY'] = 'dcomite-web-secret-key'
    app.config['APP_NAME'] = APP_NAME
    app.config['APP_VERSION'] = APP_VERSION

    # Enregistrer les helpers Jinja2
    from web.helpers import register_helpers
    register_helpers(app)

    # Enregistrer les blueprints
    from web.blueprints.dashboard import dashboard_bp
    from web.blueprints.adherents import adherents_bp
    from web.blueprints.appels import appels_bp
    from web.blueprints.contributions import contributions_bp
    from web.blueprints.depenses import depenses_bp
    from web.blueprints.annees import annees_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(adherents_bp, url_prefix='/adherents')
    app.register_blueprint(appels_bp, url_prefix='/appels')
    app.register_blueprint(contributions_bp, url_prefix='/paiements')
    app.register_blueprint(depenses_bp, url_prefix='/depenses')
    app.register_blueprint(annees_bp, url_prefix='/annees')

    return app
