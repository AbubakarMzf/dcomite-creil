"""
Gestionnaire de base de données SQLite
Gestion singleton de la connexion à la base de données
"""
import sqlite3
import os
from datetime import datetime


class DatabaseManager:
    """Gestionnaire singleton de la connexion SQLite"""

    _instance = None
    _connection = None

    def __new__(cls, db_path=None):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path=None):
        if db_path and not self._connection:
            self.db_path = db_path
            self._ensure_db_directory()
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._connection.row_factory = sqlite3.Row
            # Activer les foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")

    def _ensure_db_directory(self):
        """Crée le répertoire de la base de données s'il n'existe pas"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def get_connection(self):
        """Retourne la connexion à la base de données"""
        if not self._connection:
            raise Exception("Base de données non initialisée")
        return self._connection

    def execute_query(self, query, params=None):
        """
        Exécute une requête SQL et retourne le cursor

        Args:
            query: Requête SQL à exécuter
            params: Paramètres de la requête (tuple ou dict)

        Returns:
            Cursor avec le résultat
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erreur SQL: {str(e)}")

    def execute_many(self, query, data):
        """
        Exécute une requête avec plusieurs ensembles de paramètres

        Args:
            query: Requête SQL à exécuter
            data: Liste de tuples de paramètres

        Returns:
            Cursor avec le résultat
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.executemany(query, data)
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erreur SQL: {str(e)}")

    def fetch_one(self, query, params=None):
        """
        Exécute une requête et retourne une seule ligne

        Args:
            query: Requête SQL SELECT
            params: Paramètres de la requête

        Returns:
            Une ligne (Row object) ou None
        """
        cursor = self.execute_query(query, params)
        return cursor.fetchone()

    def fetch_all(self, query, params=None):
        """
        Exécute une requête et retourne toutes les lignes

        Args:
            query: Requête SQL SELECT
            params: Paramètres de la requête

        Returns:
            Liste de lignes (Row objects)
        """
        cursor = self.execute_query(query, params)
        return cursor.fetchall()

    def create_tables(self):
        """Crée les tables de la base de données à partir du schema.sql"""
        schema_path = os.path.join(
            os.path.dirname(__file__),
            'schema.sql'
        )

        if not os.path.exists(schema_path):
            raise Exception(f"Fichier schema.sql non trouvé: {schema_path}")

        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        conn = self.get_connection()
        try:
            conn.executescript(schema_sql)
            conn.commit()
            print("Tables créées avec succès")
        except sqlite3.Error as e:
            conn.rollback()
            raise Exception(f"Erreur lors de la création des tables: {str(e)}")

    def backup_database(self, backup_dir=None):
        """
        Crée une sauvegarde de la base de données

        Args:
            backup_dir: Répertoire de sauvegarde (optionnel)

        Returns:
            Chemin du fichier de sauvegarde
        """
        if not backup_dir:
            backup_dir = os.path.join(
                os.path.dirname(self.db_path),
                '..',
                'backups'
            )

        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"tontine_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)

        # Créer une copie de la base de données
        source_conn = self.get_connection()
        backup_conn = sqlite3.connect(backup_path)

        try:
            source_conn.backup(backup_conn)
            backup_conn.close()
            print(f"Sauvegarde créée: {backup_path}")
            return backup_path
        except sqlite3.Error as e:
            raise Exception(f"Erreur lors de la sauvegarde: {str(e)}")

    def close(self):
        """Ferme la connexion à la base de données"""
        if self._connection:
            self._connection.close()
            self._connection = None
            print("Connexion à la base de données fermée")

    def begin_transaction(self):
        """Démarre une transaction"""
        conn = self.get_connection()
        conn.execute("BEGIN TRANSACTION")

    def commit_transaction(self):
        """Valide une transaction"""
        conn = self.get_connection()
        conn.commit()

    def rollback_transaction(self):
        """Annule une transaction"""
        conn = self.get_connection()
        conn.rollback()

    @staticmethod
    def row_to_dict(row):
        """
        Convertit un objet Row SQLite en dictionnaire

        Args:
            row: Objet Row de SQLite

        Returns:
            Dictionnaire avec les données de la ligne
        """
        if row is None:
            return None
        return dict(zip(row.keys(), row))

    @staticmethod
    def rows_to_list(rows):
        """
        Convertit une liste de Row en liste de dictionnaires

        Args:
            rows: Liste d'objets Row

        Returns:
            Liste de dictionnaires
        """
        if not rows:
            return []
        return [DatabaseManager.row_to_dict(row) for row in rows]
