"""
Modele Cotisation
Represente l'obligation de paiement d'un adherent pour un appel de fond
"""
from database.db_manager import DatabaseManager


class Cotisation:
    """Modele representant une cotisation (liaison appel <-> adherent)"""

    def __init__(self, id, appel_id, adherent_id, montant_du, montant_paye=0,
                 statut='non_paye', created_at=None, updated_at=None):
        self.id = id
        self.appel_id = appel_id
        self.adherent_id = adherent_id
        self.montant_du = montant_du
        self.montant_paye = montant_paye
        self.statut = statut
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def get_by_id(cotisation_id):
        db = DatabaseManager()
        row = db.fetch_one("SELECT * FROM cotisations WHERE id = ?", (cotisation_id,))
        if row:
            return Cotisation._from_row(row)
        return None

    @staticmethod
    def get_for_adherent(adherent_id):
        """Toutes les cotisations d'un adherent (plus recent en premier)"""
        db = DatabaseManager()
        query = """
            SELECT c.*, a.annee as appel_annee, a.description as appel_description,
                   a.montant as appel_montant, a.date_lancement
            FROM cotisations c
            JOIN appels_de_fonds a ON c.appel_id = a.id
            WHERE c.adherent_id = ?
            ORDER BY a.date_lancement DESC
        """
        rows = db.fetch_all(query, (adherent_id,))
        return [Cotisation._from_row(row) for row in rows]

    @staticmethod
    def get_impayees_adherent(adherent_id):
        """Cotisations non payees ou partielles d'un adherent"""
        db = DatabaseManager()
        query = """
            SELECT c.*, a.annee as appel_annee, a.description as appel_description,
                   a.montant as appel_montant, a.date_lancement
            FROM cotisations c
            JOIN appels_de_fonds a ON c.appel_id = a.id
            WHERE c.adherent_id = ? AND c.statut != 'paye'
            ORDER BY a.date_lancement ASC
        """
        rows = db.fetch_all(query, (adherent_id,))
        return [Cotisation._from_row(row) for row in rows]

    @staticmethod
    def get_for_appel(appel_id):
        """Toutes les cotisations d'un appel avec info adherent"""
        db = DatabaseManager()
        query = """
            SELECT c.*, ad.nom, ad.prenom
            FROM cotisations c
            JOIN adherents ad ON c.adherent_id = ad.id
            ORDER BY ad.nom, ad.prenom
        """
        # Filter by appel_id
        query = """
            SELECT c.*, ad.nom, ad.prenom
            FROM cotisations c
            JOIN adherents ad ON c.adherent_id = ad.id
            WHERE c.appel_id = ?
            ORDER BY ad.nom, ad.prenom
        """
        rows = db.fetch_all(query, (appel_id,))
        return [Cotisation._from_row(row) for row in rows]

    def enregistrer_paiement(self, montant, date_paiement, mode_paiement=None,
                             reference_paiement=None, admin_id=None, notes=None):
        """
        Enregistre un paiement pour cette cotisation.
        Met a jour montant_paye et statut, cree une contribution, log dans historique.
        """
        from models.contribution import Contribution
        from models.historique import Historique

        db = DatabaseManager()

        # Creer la contribution
        Contribution.create(
            adherent_id=self.adherent_id,
            cotisation_id=self.id,
            montant=montant,
            date_paiement=date_paiement,
            mode_paiement=mode_paiement,
            reference_paiement=reference_paiement,
            admin_id=admin_id,
            type_paiement='cotisation',
            notes=notes
        )

        # Mettre a jour la cotisation
        nouveau_paye = self.montant_paye + montant
        if nouveau_paye >= self.montant_du:
            nouveau_statut = 'paye'
        elif nouveau_paye > 0:
            nouveau_statut = 'partiel'
        else:
            nouveau_statut = 'non_paye'

        db.execute_query(
            "UPDATE cotisations SET montant_paye = ?, statut = ? WHERE id = ?",
            (nouveau_paye, nouveau_statut, self.id)
        )
        self.montant_paye = nouveau_paye
        self.statut = nouveau_statut

        # Logger dans historique
        Historique.log(
            self.adherent_id, 'paiement_cotisation',
            f"Paiement de {montant} EUR (cotisation appel #{self.appel_id})",
            montant=montant, admin_id=admin_id
        )

    def get_reste_a_payer(self):
        """Montant restant a payer"""
        reste = self.montant_du - self.montant_paye
        return max(0, reste)

    def get_adherent(self):
        from models.adherent import Adherent
        return Adherent.get_by_id(self.adherent_id)

    def get_appel(self):
        from models.appel import AppelDeFonds
        return AppelDeFonds.get_by_id(self.appel_id)

    @staticmethod
    def _from_row(row):
        c = Cotisation(
            id=row['id'],
            appel_id=row['appel_id'],
            adherent_id=row['adherent_id'],
            montant_du=row['montant_du'],
            montant_paye=row['montant_paye'],
            statut=row['statut'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        # Attach extra JOIN fields if present
        for field in ['appel_annee', 'appel_description', 'appel_montant',
                      'date_lancement', 'nom', 'prenom']:
            try:
                setattr(c, field, row[field])
            except (IndexError, KeyError):
                pass
        return c
