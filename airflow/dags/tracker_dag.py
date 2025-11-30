import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

import psycopg2
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

# --- Variables depuis .env ---
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = int(os.getenv("POSTGRES_PORT", 5432))
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

# --- Fonction pour scrapper et envoyer email ---
def check_prices():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()

        cur.execute("SELECT id, url, seuil, email, user_id, product_name FROM tracking")
        rows = cur.fetchall()

        for row in rows:
            tracking_id, url, seuil, email_to, user_id, product_name = row

            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers)
            soup = BeautifulSoup(resp.text, "html.parser")

            # Scrapper le prix
            price = None
            el = soup.find("span", class_="price__current")
            if el:
                price_text = el.get_text(strip=True).replace("R", "").replace(",", "")
                try:
                    price = float(price_text)
                except:
                    price = None

            # Comparer avec seuil
            if price is not None and price <= seuil:
                msg = MIMEText(
                    f"Produit: {product_name}\nURL: {url}\nPrix actuel: {price}\nSeuil: {seuil}"
                )
                msg["Subject"] = f"Alerte Prix : {product_name}"
                msg["From"] = EMAIL_FROM
                msg["To"] = email_to

                # Envoyer email via SMTP authentifié
                try:
                    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                        server.starttls()
                        server.login(EMAIL_FROM, EMAIL_PASSWORD)
                        server.send_message(msg)
                        print(f"Email envoyé à {email_to} pour {product_name}")
                except Exception as e:
                    print("Erreur envoi email:", e)

                # Supprimer la ligne de tracking
                cur.execute("DELETE FROM tracking WHERE id = %s", (tracking_id,))
                conn.commit()

        cur.close()
        conn.close()
    except Exception as e:
        print("Erreur DB:", e)

# --- DAG Airflow ---
default_args = {"owner": "airflow", "retries": 1}

with DAG(
    "price_tracker",
    default_args=default_args,
    description="Scrappe les prix et envoie alertes par email",
    schedule_interval="@hourly",
    start_date=days_ago(1),
    catchup=False
) as dag:

    task_check_prices = PythonOperator(
        task_id="check_prices",
        python_callable=check_prices
    )

    task_check_prices

