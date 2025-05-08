# MeilleureCopro - API de Statistiques Immobilières

API simple de statistiques sur des données d'annonces immobilières pour des besoins internes de MeilleureCopro.

## Fonctionnalités

- Consultation des charges de copropriétés moyennes, quantiles 10% et 90% par département, ville ou code postal
- Interface web simple pour consulter les statistiques
- Ajout d'annonces depuis BienIci.com via URL

## Installation

### Prérequis

- Python 3.8+
- pip

### Étapes d'installation

1. **Cloner le dépôt**

```bash
git clone https://github.com/gbaelen/meilleureCopro_technical_exercise.git
cd meilleureCopro_technical_exercise/exercice1/
```

2. **Créer un environnement virtuel**

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

4. **Initialiser la base de données**

```bash
cd meilleureCopro
python manage.py migrate
```

5. **Télécharger le dataset initial**

```bash
wget https://storage.googleapis.com/data.meilleurecopro.com/stage/dataset_annonces.csv.tar.gz
```

6. **Importer les données**

```bash
python manage.py import_listings --file dataset_annonces.csv.tar.gz
```

Note: Il y a un dossier data où vous pouvez mettre le tar.gz, dans ce cas, la commande sera:
```bash
python manage.py import_listings --file ../data/dataset_annonces.csv.tar.gz
```

7. **Lancer le serveur de développement**

```bash
python manage.py runserver
```

L'application est maintenant accessible à l'adresse http://localhost:8000/

## Utilisation

### Interface Web

1. Accédez à http://localhost:8000/ pour ouvrir l'interface web
2. Utilisez le formulaire pour rechercher des statistiques par département, ville ou code postal
3. Utilisez le formulaire en bas de page pour ajouter une nouvelle annonce depuis BienIci

### API REST

#### Obtenir des statistiques

```
GET /api/stats/?query_type=department&query_value=75
GET /api/stats/?query_type=city&query_value=Paris
GET /api/stats/?query_type=postal_code&query_value=75012
```

#### Ajouter une annonce BienIci

```
POST /api/add/
Content-Type: application/json

{
    "url": "https://www.bienici.com/annonce/vente/paris-12e/appartement/3pieces/century-21-202_2907_27607"
}
```

## Notes de développement

Les optimisations possibles incluent:

- Ajout de tests unitaires et d'intégration
- Amélioration de la gestion des erreurs
- Mise en cache des résultats de statistiques fréquemment demandées
- Migration vers une base de données plus robuste (PostgreSQL)
- Filtres et options de recherche supplémentaires
