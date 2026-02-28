"""
Blueprint Contributions - Gestion des paiements
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.contribution import Contribution
from models.cotisation import Cotisation
from models.adherent import Adherent
from models.historique import Historique
from services.contribution_service import ContributionService
from database.db_manager import DatabaseManager
from config import CURRENCY_SYMBOL

contributions_bp = Blueprint('contributions', __name__)


@contributions_bp.route('/')
def index():
    contributions = ContributionService.get_dernieres_contributions(100)
    return render_template('contributions/index.html', contributions=contributions)


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
                           title='Enregistrer un paiement',
                           action_url=url_for('contributions.creer'))


@contributions_bp.route('/api/cotisations/<int:adherent_id>')
def api_cotisations(adherent_id):
    """API AJAX : cotisations impayees + frais d'entree d'un adherent"""
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

    adherent = Adherent.get_by_id(adherent_id)
    frais_impaye = (
        adherent is not None
        and adherent.frais_entree
        and adherent.frais_entree > 0
        and not adherent.frais_entree_paye
    )
    frais_montant = adherent.frais_entree if frais_impaye else 0

    return jsonify({
        'cotisations': result,
        'frais_impaye': frais_impaye,
        'frais_montant': frais_montant
    })


@contributions_bp.route('/nouveau', methods=['POST'])
def creer():
    adherent_id = request.form.get('adherent_id')
    montant_str = request.form.get('montant', '').strip()
    date_paiement = request.form.get('date_paiement', '').strip()
    mode_paiement = request.form.get('mode_paiement', '').strip() or None
    reference_paiement = request.form.get('reference_paiement', '').strip() or None
    admin_id = request.form.get('admin_id') or None
    notes = request.form.get('notes', '').strip() or None
    cotisation_id = request.form.get('cotisation_id') or None
    type_paiement = request.form.get('type_paiement', 'cotisation')

    if not adherent_id or not montant_str or not date_paiement:
        flash('Adherent, montant et date sont obligatoires.', 'danger')
        return redirect(url_for('contributions.index'))

    try:
        montant = float(montant_str)
        if montant <= 0:
            raise ValueError()
    except ValueError:
        flash('Le montant doit etre un nombre positif.', 'danger')
        return redirect(url_for('contributions.index'))

    admin_id_int = int(admin_id) if admin_id else None
    adherent_id_int = int(adherent_id)
    contribution = None

    if type_paiement == 'frais_entree':
        contribution = Contribution.create(
            adherent_id=adherent_id_int,
            montant=montant,
            date_paiement=date_paiement,
            mode_paiement=mode_paiement,
            reference_paiement=reference_paiement,
            admin_id=admin_id_int,
            type_paiement='frais_entree',
            notes=notes
        )
        adherent = Adherent.get_by_id(adherent_id_int)
        if adherent:
            adherent.update(frais_entree_paye=1)
        Historique.log(
            adherent_id_int, 'frais_entree',
            f"Paiement frais d'entree: {montant} {CURRENCY_SYMBOL}",
            montant=montant, admin_id=admin_id_int
        )
        flash("Frais d'entree enregistres.", 'success')

    elif cotisation_id:
        cotisation = Cotisation.get_by_id(int(cotisation_id))
        if cotisation:
            contribution = cotisation.enregistrer_paiement(
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
            return redirect(url_for('contributions.index'))

    else:
        # Paiement libre sans cotisation associee
        contribution = Contribution.create(
            adherent_id=adherent_id_int,
            montant=montant,
            date_paiement=date_paiement,
            mode_paiement=mode_paiement,
            reference_paiement=reference_paiement,
            admin_id=admin_id_int,
            type_paiement='cotisation',
            notes=notes
        )
        Historique.log(
            adherent_id_int, 'paiement_cotisation',
            f"Paiement cotisation: {montant} {CURRENCY_SYMBOL}",
            montant=montant, admin_id=admin_id_int
        )
        flash('Paiement enregistre.', 'success')

    # Generer le PDF recu
    if contribution:
        try:
            from services.pdf_service import PdfService
            chemin = PdfService.generer_pdf_paiement(contribution)
            flash(f'Recu PDF genere : {chemin}', 'info')
        except Exception as e:
            flash(f'PDF non genere : {e}', 'warning')

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


# ------------------------------------------------------------------
# Liste des impayes
# ------------------------------------------------------------------

@contributions_bp.route('/impayes')
def impayes():
    db = DatabaseManager()
    rows = db.fetch_all("""
        SELECT a.id, a.nom, a.prenom,
               COUNT(c.id) as nb_impayees,
               COALESCE(SUM(c.montant_du - c.montant_paye), 0) as montant_restant
        FROM adherents a
        JOIN cotisations c ON c.adherent_id = a.id
        WHERE c.statut != 'paye'
        GROUP BY a.id, a.nom, a.prenom
        ORDER BY a.nom, a.prenom
    """)
    lignes = [dict(row) for row in rows]
    total = sum(l['montant_restant'] for l in lignes)
    return render_template('contributions/impayes.html', lignes=lignes, total=total)


@contributions_bp.route('/impayes/pdf', methods=['POST'])
def impayes_pdf():
    db = DatabaseManager()
    rows = db.fetch_all("""
        SELECT a.id, a.nom, a.prenom,
               COUNT(c.id) as nb_impayees,
               COALESCE(SUM(c.montant_du - c.montant_paye), 0) as montant_restant
        FROM adherents a
        JOIN cotisations c ON c.adherent_id = a.id
        WHERE c.statut != 'paye'
        GROUP BY a.id, a.nom, a.prenom
        ORDER BY a.nom, a.prenom
    """)
    lignes = [dict(row) for row in rows]
    try:
        from services.pdf_service import PdfService
        chemin = PdfService.generer_pdf_impayes(lignes)
        flash(f'PDF genere : {chemin}', 'success')
    except Exception as e:
        flash(f'Erreur PDF : {e}', 'danger')
    return redirect(url_for('contributions.impayes'))
