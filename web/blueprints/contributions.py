"""
Blueprint Contributions - Gestion des paiements
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.contribution import Contribution
from models.cotisation import Cotisation
from models.adherent import Adherent
from services.contribution_service import ContributionService
from datetime import datetime

contributions_bp = Blueprint('contributions', __name__)


@contributions_bp.route('/')
def index():
    contributions = ContributionService.get_dernieres_contributions(100)

    return render_template('contributions/index.html',
                           contributions=contributions)


@contributions_bp.route('/<int:id>')
def detail(id):
    contribution = Contribution.get_by_id(id)
    if not contribution:
        return '<div class="modal-body"><div class="alert alert-danger">Paiement non trouve</div></div>'

    adherent = contribution.get_adherent()

    return render_template('contributions/detail.html',
                           contribution=contribution,
                           adherent=adherent)


@contributions_bp.route('/nouveau', methods=['GET'])
def form_nouveau():
    adherents = Adherent.get_all(actif_only=True)
    return render_template('contributions/form.html',
                           contribution=None,
                           adherents=adherents,
                           cotisations_impayees=[],
                           title='Enregistrer un paiement',
                           action_url=url_for('contributions.creer'))


@contributions_bp.route('/api/cotisations/<int:adherent_id>')
def api_cotisations(adherent_id):
    """API pour charger les cotisations impayees d'un adherent (AJAX)"""
    cotisations = Cotisation.get_impayees_adherent(adherent_id)
    result = []
    for c in cotisations:
        appel_info = ''
        if hasattr(c, 'appel_annee'):
            appel_info = f"Appel {c.appel_annee}"
            if hasattr(c, 'appel_description') and c.appel_description:
                appel_info += f" - {c.appel_description}"
        result.append({
            'id': c.id,
            'appel_info': appel_info,
            'montant_du': c.montant_du,
            'montant_paye': c.montant_paye,
            'reste': c.get_reste_a_payer()
        })

    # Verifier si frais d'entree impayes
    adherent = Adherent.get_by_id(adherent_id)
    frais_impaye = False
    frais_montant = 0
    if adherent and adherent.frais_entree and adherent.frais_entree > 0 and not adherent.frais_entree_paye:
        frais_impaye = True
        frais_montant = adherent.frais_entree

    return jsonify({
        'cotisations': result,
        'frais_impaye': frais_impaye,
        'frais_montant': frais_montant
    })


@contributions_bp.route('/nouveau', methods=['POST'])
def creer():
    adherent_id = request.form.get('adherent_id')
    montant = request.form.get('montant', '').strip()
    date_paiement = request.form.get('date_paiement', '').strip()
    mode_paiement = request.form.get('mode_paiement', '').strip() or None
    reference_paiement = request.form.get('reference_paiement', '').strip() or None
    admin_id = request.form.get('admin_id') or None
    notes = request.form.get('notes', '').strip() or None
    cotisation_id = request.form.get('cotisation_id') or None
    type_paiement = request.form.get('type_paiement', 'cotisation')

    if not adherent_id or not montant or not date_paiement:
        flash('Adherent, montant et date sont obligatoires.', 'danger')
        return redirect(url_for('contributions.index'))

    try:
        montant = float(montant)
        if montant <= 0:
            raise ValueError()
    except ValueError:
        flash('Le montant doit etre un nombre positif.', 'danger')
        return redirect(url_for('contributions.index'))

    admin_id_int = int(admin_id) if admin_id else None

    if type_paiement == 'frais_entree':
        # Paiement de frais d'entree
        Contribution.create(
            adherent_id=int(adherent_id),
            montant=montant,
            date_paiement=date_paiement,
            mode_paiement=mode_paiement,
            reference_paiement=reference_paiement,
            admin_id=admin_id_int,
            type_paiement='frais_entree',
            notes=notes
        )
        # Marquer les frais comme payes
        adherent = Adherent.get_by_id(int(adherent_id))
        if adherent:
            adherent.update(frais_entree_paye=1)
        flash('Frais d\'entree enregistres.', 'success')

    elif cotisation_id:
        # Paiement d'une cotisation specifique
        cotisation = Cotisation.get_by_id(int(cotisation_id))
        if cotisation:
            cotisation.enregistrer_paiement(
                montant=montant,
                date_paiement=date_paiement,
                mode_paiement=mode_paiement,
                reference_paiement=reference_paiement,
                admin_id=admin_id_int,
                notes=notes
            )
            flash('Paiement de cotisation enregistre.', 'success')
        else:
            flash('Cotisation non trouvee.', 'danger')
    else:
        # Paiement libre (sans cotisation liee)
        Contribution.create(
            adherent_id=int(adherent_id),
            montant=montant,
            date_paiement=date_paiement,
            mode_paiement=mode_paiement,
            reference_paiement=reference_paiement,
            admin_id=admin_id_int,
            type_paiement='cotisation',
            notes=notes
        )
        flash('Paiement enregistre.', 'success')

    return redirect(url_for('contributions.index'))


@contributions_bp.route('/<int:id>/supprimer', methods=['POST'])
def supprimer(id):
    contribution = Contribution.get_by_id(id)
    if not contribution:
        flash('Paiement non trouve.', 'danger')
        return redirect(url_for('contributions.index'))

    contribution.delete()
    flash('Paiement supprime avec succes.', 'success')
    return redirect(url_for('contributions.index'))
