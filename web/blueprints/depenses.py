"""
Blueprint Depenses - Gestion des depenses (deces)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.depense import Depense
from models.adherent import Adherent
from models.annee import Annee

depenses_bp = Blueprint('depenses', __name__)


@depenses_bp.route('/')
def index():
    annee_active = Annee.get_active()

    if not annee_active:
        depenses = []
    else:
        depenses = Depense.get_all_for_annee(annee_active.id)

    # Enrichir avec nom defunt et adherent
    depenses_enriched = []
    for d in depenses:
        adherent = d.get_adherent()
        depenses_enriched.append({
            'depense': d,
            'defunt_nom': d.get_nom_defunt(),
            'adherent_nom': adherent.get_nom_complet() if adherent else 'Inconnu'
        })

    return render_template('depenses/index.html',
                           depenses=depenses_enriched)


@depenses_bp.route('/<int:id>')
def detail(id):
    depense = Depense.get_by_id(id)
    if not depense:
        return '<div class="modal-body"><div class="alert alert-danger">Depense non trouvee</div></div>'

    adherent = depense.get_adherent()

    return render_template('depenses/detail.html',
                           depense=depense,
                           adherent=adherent)


@depenses_bp.route('/nouveau', methods=['GET'])
def form_nouveau():
    adherents = Adherent.get_all(actif_only=True)
    return render_template('depenses/form.html',
                           depense=None,
                           adherents=adherents,
                           title='Enregistrer une depense',
                           action_url=url_for('depenses.creer'))


@depenses_bp.route('/nouveau', methods=['POST'])
def creer():
    annee_active = Annee.get_active()
    if not annee_active:
        flash('Aucune annee active.', 'danger')
        return redirect(url_for('depenses.index'))

    adherent_id = request.form.get('adherent_id')
    defunt_est_adherent = request.form.get('defunt_est_adherent', '0')
    defunt_nom = request.form.get('defunt_nom', '').strip() or None
    defunt_relation = request.form.get('defunt_relation', '').strip() or None
    date_deces = request.form.get('date_deces', '').strip()
    pays_destination = request.form.get('pays_destination', '').strip() or None

    if not adherent_id or not date_deces:
        flash('Adherent et date de deces sont obligatoires.', 'danger')
        return redirect(url_for('depenses.index'))

    # Recuperer les montants des postes
    def get_float(name):
        val = request.form.get(name, '').strip()
        try:
            return float(val) if val else 0
        except ValueError:
            return 0

    Depense.create(
        annee_id=annee_active.id,
        adherent_id=int(adherent_id),
        defunt_est_adherent=int(defunt_est_adherent),
        date_deces=date_deces,
        defunt_nom=defunt_nom,
        defunt_relation=defunt_relation,
        pays_destination=pays_destination,
        transport_services=get_float('transport_services'),
        billet_avion=get_float('billet_avion'),
        imam=get_float('imam'),
        mairie=get_float('mairie'),
        autre1=get_float('autre1'),
        autre2=get_float('autre2'),
        autre3=get_float('autre3'),
        notes=request.form.get('notes', '').strip() or None
    )

    flash('Depense enregistree avec succes.', 'success')
    return redirect(url_for('depenses.index'))


@depenses_bp.route('/<int:id>/supprimer', methods=['POST'])
def supprimer(id):
    depense = Depense.get_by_id(id)
    if not depense:
        flash('Depense non trouvee.', 'danger')
        return redirect(url_for('depenses.index'))

    depense.delete()
    flash('Depense supprimee avec succes.', 'success')
    return redirect(url_for('depenses.index'))
