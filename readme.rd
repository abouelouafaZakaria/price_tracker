Price Tracker & Airflow

Cette application Flask permet de suivre les prix de produits et d'envoyer des alertes par email lorsque les prix atteignent un seuil défini. Un DAG Airflow récupère les données depuis PostgreSQL et déclenche l'envoi des notifications.

## Structure du projet

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

## Prérequis

* Docker et Docker Compose installés
* Connexion internet pour télécharger les images
* SMTP configuré pour l’envoi des emails depuis le DAG

## Installation

1. Cloner le projet :
git clone <ton-repo-github>
cd Price_tracker

2. Créer un fichier `.env` avec les valeurs nécessaires pour la base de données, Flask et l’email :

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

# Airflow
AIRFLOW_PORT=8080

## Lancement des containers

docker compose up --build

* Flask : http://localhost:5000
* Airflow : http://localhost:8080

## Bases de données

* Flask : price_tracker (tables users, tracking, scrap)
  Initialisation : initdb/init.sql
* Airflow : airflow_db (tables internes)
  Initialisation : initdb/airflow.sql

## DAG Airflow

* Fichier : airflow/dags/tracker_dag.py
* Fonction : scrapper les prix et envoyer un email si un seuil est atteint
* Fréquence : toutes les heures (@hourly)
* Les variables SMTP et DB sont définies dans .env
