"""
Blueprint Adherents - Gestion des membres
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.adherent import Adherent
from datetime import datetime

adherents_bp = Blueprint('adherents', __name__)


@adherents_bp.route('/')
def index():
    q = request.args.get('q', '').strip()
    actifs_only = request.args.get('actifs_only', '1') == '1'

    if q:
        adherents = Adherent.search(q)
    else:
        adherents = Adherent.get_all(actif_only=actifs_only)

    return render_template('adherents/index.html',
                           adherents=adherents,
                           search_query=q,
                           actifs_only=actifs_only)


@adherents_bp.route('/<int:id>')
def detail(id):
    adherent = Adherent.get_by_id(id)
    if not adherent:
        return '<div class="modal-body"><div class="alert alert-danger">Adherent non trouve</div></div>'

    cotisations = adherent.get_cotisations()
    historique = adherent.get_historique()

    return render_template('adherents/detail.html',
                           adherent=adherent,
                           cotisations=cotisations,
                           historique=historique)


@adherents_bp.route('/nouveau', methods=['GET'])
def form_nouveau():
    return render_template('adherents/form.html',
                           adherent=None,
                           title='Ajouter un adherent',
                           action_url=url_for('adherents.creer'))


@adherents_bp.route('/nouveau', methods=['POST'])
def creer():
    nom = request.form.get('nom', '').strip()
    prenom = request.form.get('prenom', '').strip()

    if not nom or not prenom:
        flash('Le nom et le prenom sont obligatoires.', 'danger')
        return redirect(url_for('adherents.index'))

    date_entree = request.form.get('date_entree', '').strip() or None
    if date_entree:
        try:
            date_entree = datetime.strptime(date_entree, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            flash('Format de date invalide.', 'danger')
            return redirect(url_for('adherents.index'))

    # Frais d'entree
    frais_entree_str = request.form.get('frais_entree', '').strip()
    frais_entree = 0
    if frais_entree_str:
        try:
            frais_entree = float(frais_entree_str)
            if frais_entree < 0:
                frais_entree = 0
        except ValueError:
            frais_entree = 0

    Adherent.create(
        nom=nom,
        prenom=prenom,
        telephone=request.form.get('telephone', '').strip() or None,
        email=request.form.get('email', '').strip() or None,
        adresse=request.form.get('adresse', '').strip() or None,
        date_entree=date_entree,
        actif=1,
        frais_entree=frais_entree,
        notes=request.form.get('notes', '').strip() or None
    )

    flash('Adherent ajoute avec succes.', 'success')
    return redirect(url_for('adherents.index'))


@adherents_bp.route('/<int:id>/modifier', methods=['GET'])
def form_modifier(id):
    adherent = Adherent.get_by_id(id)
    if not adherent:
        return '<div class="modal-body"><div class="alert alert-danger">Adherent non trouve</div></div>'

    return render_template('adherents/form.html',
                           adherent=adherent,
                           title='Modifier un adherent',
                           action_url=url_for('adherents.modifier', id=id))


@adherents_bp.route('/<int:id>/modifier', methods=['POST'])
def modifier(id):
    adherent = Adherent.get_by_id(id)
    if not adherent:
        flash('Adherent non trouve.', 'danger')
        return redirect(url_for('adherents.index'))

    nom = request.form.get('nom', '').strip()
    prenom = request.form.get('prenom', '').strip()

    if not nom or not prenom:
        flash('Le nom et le prenom sont obligatoires.', 'danger')
        return redirect(url_for('adherents.index'))

    adherent.update(
        nom=nom,
        prenom=prenom,
        telephone=request.form.get('telephone', '').strip() or None,
        email=request.form.get('email', '').strip() or None,
        adresse=request.form.get('adresse', '').strip() or None,
        notes=request.form.get('notes', '').strip() or None
    )

    flash('Adherent modifie avec succes.', 'success')
    return redirect(url_for('adherents.index'))


@adherents_bp.route('/<int:id>/supprimer', methods=['POST'])
def supprimer(id):
    adherent = Adherent.get_by_id(id)
    if not adherent:
        flash('Adherent non trouve.', 'danger')
        return redirect(url_for('adherents.index'))

    nom = adherent.get_nom_complet()
    adherent.delete()
    flash(f'{nom} supprime avec succes.', 'success')
    return redirect(url_for('adherents.index'))


@adherents_bp.route('/<int:id>/toggle', methods=['POST'])
def toggle(id):
    adherent = Adherent.get_by_id(id)
    if not adherent:
        flash('Adherent non trouve.', 'danger')
        return redirect(url_for('adherents.index'))

    if adherent.actif:
        adherent.update(actif=0, date_sortie=datetime.now().strftime('%Y-%m-%d'))
        flash(f'{adherent.get_nom_complet()} desactive.', 'success')
    else:
        adherent.update(actif=1, date_sortie=None)
        flash(f'{adherent.get_nom_complet()} reactive.', 'success')

    return redirect(url_for('adherents.index'))
