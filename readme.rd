# Price Tracker & Airflow

Application Flask pour suivre les prix de produits et recevoir des alertes par email. Un DAG Airflow scrappe les prix depuis PostgreSQL et envoie un email si le prix atteint le seuil défini.

## Arborescence

```
Price_tracker/
│
├─ app/
│   ├─ Dockerfile.flask
│   ├─ main.py
│   ├─ requirements.txt
│   └─ templates/
│
├─ airflow/
│   ├─ dags/
│   │   └─ tracker_dag.py
│   ├─ logs/
│   ├─ plugins/
│   └─ Dockerfile.airflow
│
├─ initdb/
│   ├─ init.sql
│   └─ airflow.sql
│
├─ docker-compose.yml
└─ .env
```

## Prérequis

* Docker & Docker Compose
* Connexion internet pour télécharger les images
* SMTP (pour l’envoi d’emails depuis le DAG)

## Installation

1. Cloner le projet :

```bash
git clone <ton-repo-github>
cd Price_tracker
```

2. Créer un fichier `.env` avec les valeurs suivantes :

```env
# PostgreSQL
POSTGRES_HOST=*****
POSTGRES_USER=******
POSTGRES_PASSWORD=*****
POSTGRES_DB=**********
POSTGRES_PORT=5432

# Flask
FLASK_APP=main.py
FLASK_ENV=development
SECRET_KEY=ma_super_cle_secrete

# Email
EMAIL_FROM=ton_email@gmail.com
EMAIL_PASSWORD=mot_de_passe_application
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

> Ne jamais pousser `.env` sur GitHub.

## Lancer les containers

```bash
docker compose up --build
```

* Flask : [http://localhost:5000](http://localhost:5000)
* Airflow : [http://localhost:8080](http://localhost:8080)

## Bases de données

* **Flask** : `price_tracker` (tables `users`, `tracking`, `scrap`)
  Initialisation : `initdb/init.sql`
* **Airflow** : `airflow_db` (tables internes)
  Initialisation : `initdb/airflow.sql`

## DAG Airflow

* Fichier : `airflow/dags/tracker_dag.py`
* Fonction : scrapper les prix et envoyer un email si seuil atteint
* Fréquence : toutes les heures (`@hourly`)
* Variables SMTP et DB dans `.env`
