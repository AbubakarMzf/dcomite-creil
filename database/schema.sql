-- Schema de base de donnees pour le systeme de gestion de tontine
-- SQLite 3

-- Table: adherents
CREATE TABLE IF NOT EXISTS adherents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    telephone TEXT,
    email TEXT,
    adresse TEXT,
    date_entree DATE DEFAULT (date('now')),
    date_sortie DATE,
    actif INTEGER DEFAULT 1,
    frais_entree REAL DEFAULT 0,
    frais_entree_paye INTEGER DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: annees (simplifiee - sert de reference temporelle pour les depenses)
CREATE TABLE IF NOT EXISTS annees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    annee INTEGER UNIQUE NOT NULL,
    active INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: appels_de_fonds
CREATE TABLE IF NOT EXISTS appels_de_fonds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    annee INTEGER NOT NULL,
    montant REAL NOT NULL,
    description TEXT,
    admin_id INTEGER,
    date_lancement DATE NOT NULL,
    cloture INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: cotisations (liaison appel <-> adherent)
CREATE TABLE IF NOT EXISTS cotisations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appel_id INTEGER NOT NULL,
    adherent_id INTEGER NOT NULL,
    montant_du REAL NOT NULL,
    montant_paye REAL DEFAULT 0,
    statut TEXT DEFAULT 'non_paye' CHECK(statut IN ('non_paye', 'partiel', 'paye')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appel_id) REFERENCES appels_de_fonds(id) ON DELETE CASCADE,
    FOREIGN KEY (adherent_id) REFERENCES adherents(id) ON DELETE CASCADE,
    UNIQUE(appel_id, adherent_id)
);

-- Table: contributions (paiements des adherents)
CREATE TABLE IF NOT EXISTS contributions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adherent_id INTEGER NOT NULL,
    cotisation_id INTEGER,
    montant REAL NOT NULL,
    date_paiement DATE NOT NULL,
    mode_paiement TEXT,
    reference_paiement TEXT,
    admin_id INTEGER CHECK(admin_id BETWEEN 1 AND 5),
    type_paiement TEXT DEFAULT 'cotisation' CHECK(type_paiement IN ('cotisation', 'frais_entree')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (adherent_id) REFERENCES adherents(id) ON DELETE CASCADE,
    FOREIGN KEY (cotisation_id) REFERENCES cotisations(id) ON DELETE SET NULL
);

-- Table: depenses (chaque depense = un deces)
CREATE TABLE IF NOT EXISTS depenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    annee_id INTEGER NOT NULL,
    adherent_id INTEGER NOT NULL,
    defunt_est_adherent INTEGER NOT NULL DEFAULT 0,
    defunt_nom TEXT,
    defunt_relation TEXT,
    date_deces DATE NOT NULL,
    pays_destination TEXT,
    transport_services REAL DEFAULT 0,
    billet_avion REAL DEFAULT 0,
    imam REAL DEFAULT 0,
    mairie REAL DEFAULT 0,
    autre1 REAL DEFAULT 0,
    autre2 REAL DEFAULT 0,
    autre3 REAL DEFAULT 0,
    montant REAL NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (annee_id) REFERENCES annees(id) ON DELETE CASCADE,
    FOREIGN KEY (adherent_id) REFERENCES adherents(id) ON DELETE CASCADE
);

-- Table: historique (journal d'evenements par adherent)
CREATE TABLE IF NOT EXISTS historique (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adherent_id INTEGER NOT NULL,
    type_evenement TEXT NOT NULL,
    description TEXT,
    montant REAL,
    admin_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (adherent_id) REFERENCES adherents(id) ON DELETE CASCADE
);

-- Index pour ameliorer les performances
CREATE INDEX IF NOT EXISTS idx_contributions_adherent ON contributions(adherent_id);
CREATE INDEX IF NOT EXISTS idx_contributions_cotisation ON contributions(cotisation_id);
CREATE INDEX IF NOT EXISTS idx_contributions_date ON contributions(date_paiement);
CREATE INDEX IF NOT EXISTS idx_cotisations_appel ON cotisations(appel_id);
CREATE INDEX IF NOT EXISTS idx_cotisations_adherent ON cotisations(adherent_id);
CREATE INDEX IF NOT EXISTS idx_cotisations_statut ON cotisations(statut);
CREATE INDEX IF NOT EXISTS idx_depenses_annee ON depenses(annee_id);
CREATE INDEX IF NOT EXISTS idx_depenses_date ON depenses(date_deces);
CREATE INDEX IF NOT EXISTS idx_adherents_nom ON adherents(nom);
CREATE INDEX IF NOT EXISTS idx_adherents_actif ON adherents(actif);
CREATE INDEX IF NOT EXISTS idx_appels_annee ON appels_de_fonds(annee);
CREATE INDEX IF NOT EXISTS idx_historique_adherent ON historique(adherent_id);

-- Triggers pour mettre a jour updated_at automatiquement
CREATE TRIGGER IF NOT EXISTS update_adherent_timestamp
AFTER UPDATE ON adherents
BEGIN
    UPDATE adherents SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_annee_timestamp
AFTER UPDATE ON annees
BEGIN
    UPDATE annees SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_contribution_timestamp
AFTER UPDATE ON contributions
BEGIN
    UPDATE contributions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_depense_timestamp
AFTER UPDATE ON depenses
BEGIN
    UPDATE depenses SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_appel_timestamp
AFTER UPDATE ON appels_de_fonds
BEGIN
    UPDATE appels_de_fonds SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_cotisation_timestamp
AFTER UPDATE ON cotisations
BEGIN
    UPDATE cotisations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
