"""
Blueprint Annees - Gestion des annees
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.annee import Annee

annees_bp = Blueprint('annees', __name__)


@annees_bp.route('/')
def index():
    annees = Annee.get_all()

    # Enrichir avec stats depenses
    annees_enriched = []
    for a in annees:
        annees_enriched.append({
            'annee': a,
            'total_depenses': a.get_total_depenses(),
            'nb_depenses': a.get_nombre_depenses()
        })

    return render_template('annees/index.html', annees=annees_enriched)


@annees_bp.route('/<int:id>')
def detail(id):
    annee = Annee.get_by_id(id)
    if not annee:
        return '<div class="modal-body"><div class="alert alert-danger">Annee non trouvee</div></div>'

    total_depenses = annee.get_total_depenses()
    nb_depenses = annee.get_nombre_depenses()

    return render_template('annees/detail.html',
                           annee=annee,
                           total_depenses=total_depenses,
                           nb_depenses=nb_depenses)


@annees_bp.route('/nouveau', methods=['GET'])
def form_nouveau():
    return render_template('annees/form.html',
                           annee=None,
                           title='Creer une annee',
                           action_url=url_for('annees.creer'))


@annees_bp.route('/nouveau', methods=['POST'])
def creer():
    annee_num = request.form.get('annee', '').strip()

    if not annee_num:
        flash('L\'annee est obligatoire.', 'danger')
        return redirect(url_for('annees.index'))

    try:
        annee_num = int(annee_num)
    except ValueError:
        flash('Valeur invalide.', 'danger')
        return redirect(url_for('annees.index'))

    if Annee.get_by_year(annee_num):
        flash(f'L\'annee {annee_num} existe deja.', 'danger')
        return redirect(url_for('annees.index'))

    Annee.create(annee=annee_num)

    flash(f'Annee {annee_num} creee avec succes.', 'success')
    return redirect(url_for('annees.index'))


@annees_bp.route('/<int:id>/activer', methods=['POST'])
def activer(id):
    annee = Annee.get_by_id(id)
    if not annee:
        flash('Annee non trouvee.', 'danger')
        return redirect(url_for('annees.index'))

    annee.set_active()
    flash(f'Annee {annee.annee} activee.', 'success')
    return redirect(url_for('annees.index'))
