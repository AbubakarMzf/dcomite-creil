"""
Blueprint Appels de fonds - Gestion des appels de cotisations
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.appel import AppelDeFonds
from models.cotisation import Cotisation
from models.adherent import Adherent
from datetime import date

appels_bp = Blueprint('appels', __name__)


@appels_bp.route('/')
def index():
    appels = AppelDeFonds.get_all()

    # Enrichir chaque appel avec ses stats
    appels_enriched = []
    for appel in appels:
        stats = appel.get_stats()
        appels_enriched.append({
            'appel': appel,
            'stats': stats
        })

    return render_template('appels/index.html', appels=appels_enriched)


@appels_bp.route('/<int:id>')
def detail(id):
    appel = AppelDeFonds.get_by_id(id)
    if not appel:
        return '<div class="modal-body"><div class="alert alert-danger">Appel non trouve</div></div>'

    stats = appel.get_stats()
    cotisations = Cotisation.get_for_appel(id)

    return render_template('appels/detail.html',
                           appel=appel,
                           stats=stats,
                           cotisations=cotisations)


@appels_bp.route('/nouveau', methods=['GET'])
def form_nouveau():
    nb_adherents = len(Adherent.get_all(actif_only=True))
    return render_template('appels/form.html',
                           appel=None,
                           nb_adherents=nb_adherents,
                           title='Lancer un appel de fond',
                           action_url=url_for('appels.creer'))


@appels_bp.route('/nouveau', methods=['POST'])
def creer():
    annee = request.form.get('annee', '').strip()
    montant = request.form.get('montant', '').strip()
    description = request.form.get('description', '').strip() or None
    admin_id = request.form.get('admin_id') or None
    date_lancement = request.form.get('date_lancement', '').strip() or None

    if not annee or not montant:
        flash('Annee et montant sont obligatoires.', 'danger')
        return redirect(url_for('appels.index'))

    try:
        annee = int(annee)
        montant = float(montant)
        if montant <= 0:
            raise ValueError()
    except ValueError:
        flash('Valeurs invalides.', 'danger')
        return redirect(url_for('appels.index'))

    AppelDeFonds.create(
        annee=annee,
        montant=montant,
        description=description,
        admin_id=int(admin_id) if admin_id else None,
        date_lancement=date_lancement
    )

    flash(f'Appel de fond {annee} lance avec succes.', 'success')
    return redirect(url_for('appels.index'))


@appels_bp.route('/<int:id>/cloturer', methods=['POST'])
def cloturer(id):
    appel = AppelDeFonds.get_by_id(id)
    if not appel:
        flash('Appel non trouve.', 'danger')
        return redirect(url_for('appels.index'))

    appel.cloturer()
    flash(f'Appel {appel.annee} cloture.', 'success')
    return redirect(url_for('appels.index'))
