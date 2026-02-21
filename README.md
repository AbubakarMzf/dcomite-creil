# Système de Gestion de Tontine - DComité

Système de gestion de tontine pour les décès et solidarité familiale. Application locale avec interface graphique Tkinter.

## 🎯 Fonctionnalités

### ✅ Gestion des adhérents
- Ajouter, modifier, supprimer des adhérents
- Recherche par nom, prénom, téléphone
- Activation/désactivation des adhérents
- Historique des contributions par adhérent

### ✅ Gestion des années fiscales
- Créer une nouvelle année avec balance cible
- Calcul automatique du montant par adhérent
- Création automatique des contributions pour tous les adhérents actifs
- Une seule année active à la fois
- Suivi de la balance actuelle (contributions - dépenses)

### ✅ Enregistrement des contributions
- Recherche rapide d'adhérent
- Enregistrement de paiements complets ou partiels
- Suivi du statut (Payé/Non payé/Partiel)
- Historique détaillé des paiements
- Calcul automatique du montant restant

### ✅ Enregistrement des dépenses
- Enregistrement des décès avec informations détaillées
- Autres types de dépenses
- Lien avec un adhérent (optionnel)
- Déduction automatique de la balance
- Statistiques des dépenses

### ✅ Tableau de bord
- Statistiques principales (adhérents, montants, balance)
- Barre de progression de la balance
- Dernières contributions et dépenses
- Alertes (balance faible, adhérents non payés)
- Taux de recouvrement

## 📦 Installation

### Prérequis
- Python 3.8 ou supérieur
- tkinter (inclus avec Python standard)
- sqlite3 (inclus avec Python standard)

### Dépendances optionnelles
```bash
pip install -r requirements.txt
```

Les dépendances optionnelles (reportlab, openpyxl, pillow) sont pour les fonctionnalités avancées de rapports (Phase 9).

## 🚀 Démarrage

```bash
cd c:\Users\abuba\Desktop\dcomite
python main.py
```

## 📖 Guide d'utilisation

### Première utilisation

1. **Créer une nouvelle année**
   - Menu `Année` → `Nouvelle année`
   - Saisir l'année (ex: 2025)
   - Définir la balance cible (ex: 500000 FCFA)
   - Le système calcule automatiquement le montant par adhérent
   - Cocher "Créer automatiquement les contributions" pour générer les contributions

2. **Ajouter des adhérents**
   - Menu `Adhérents` → `Ajouter un adhérent`
   - Remplir le formulaire (nom, prénom, téléphone, etc.)
   - Si l'année est déjà créée, retourner dans `Année` pour créer les contributions

### Utilisation quotidienne

**Enregistrer un paiement:**
1. Menu `Contributions` → `Enregistrer un paiement`
2. Rechercher l'adhérent par nom
3. Double-cliquer sur l'adhérent ou cliquer sur "Enregistrer un paiement"
4. Saisir le montant, la date, le mode de paiement
5. Valider

**Enregistrer un décès:**
1. Menu `Dépenses` → `Enregistrer une dépense`
2. Cliquer sur "Nouvelle dépense"
3. Sélectionner "Décès"
4. Remplir les informations (montant, bénéficiaire, nom du défunt, etc.)
5. Valider

**Consulter le tableau de bord:**
- Retourner à l'accueil pour voir les statistiques mises à jour
- Voir la balance actuelle, le taux de recouvrement
- Consulter les dernières activités

### Fonctions avancées

**Backup de la base de données:**
- Menu `Fichier` → `Backup Base de données`
- Un fichier de sauvegarde est créé dans le dossier `backups/`

**Voir les détails d'une année:**
- Menu `Année` → `Gérer les années`
- Double-cliquer sur une année pour voir ses détails

**Rechercher un adhérent:**
- Menu `Adhérents` → `Gérer les adhérents`
- Utiliser la barre de recherche en haut

## 📊 Structure de la base de données

Le système utilise SQLite avec 5 tables principales:

- **adherents**: Informations sur les adhérents
- **annees**: Années fiscales avec balances
- **contributions**: Contributions des adhérents par année
- **depenses**: Dépenses (décès et autres)
- **paiements_details**: Historique détaillé des paiements partiels

Base de données: `data/tontine.db`

## 🔧 Maintenance

### Backup
- Les backups sont créés dans `backups/`
- Format: `tontine_backup_YYYYMMDD_HHMMSS.db`
- Conserver régulièrement des copies

### Rapports et exports
- Les exports sont sauvegardés dans `exports/`
- Formats: PDF et Excel (à venir dans Phase 9)

## 📝 Notes techniques

### Architecture
```
dcomite/
├── database/          # Gestion SQLite
├── models/            # Modèles de données (CRUD)
├── services/          # Logique métier
├── ui/                # Interface Tkinter
│   ├── components/    # Composants réutilisables
│   └── views/         # Vues principales
└── utils/             # Utilitaires
```

### Règles métier importantes

1. **Une seule année active**: Une seule année peut être active à la fois
2. **Contribution unique**: Un adhérent = 1 contribution par année maximum
3. **Balance automatique**: Balance = Total contributions payées - Total dépenses
4. **Statut automatique**: Le statut de paiement se met à jour automatiquement
5. **Cascade**: La suppression d'un adhérent supprime aussi ses contributions

## 🐛 Dépannage

**L'application ne démarre pas:**
- Vérifier que Python 3.8+ est installé
- Vérifier que tkinter est disponible: `python -m tkinter`

**Erreur de base de données:**
- Vérifier que le dossier `data/` existe
- Restaurer depuis un backup si nécessaire

**Interface ne s'affiche pas correctement:**
- Augmenter la résolution de l'écran
- La taille minimale recommandée est 1200x800

## 📄 Licence

Usage interne pour DComité.

## 👨‍💻 Développement

Système développé avec:
- Python 3.x
- Tkinter (interface graphique)
- SQLite (base de données)
- Architecture MVC

Pour contribuer ou modifier:
1. Consulter le plan d'implémentation dans `.claude/plans/`
2. Respecter l'architecture existante
3. Tester les modifications localement avant déploiement
