from flask import Flask, request, render_template, redirect, url_for, session
import psycopg2
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(minutes=10)

# Fonction de connexion PostgreSQL
def get_conn():
    return psycopg2.connect(
        host="postgres",                   # IMPORTANT : nom du service docker
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

@app.route("/")
def home():
    return render_template("loging.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_post():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (name,email, password)
                VALUES (%s,%s,%s)
            """, (name, email, password))
            conn.commit()

    return render_template("register_success.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, email, name
                FROM users
                WHERE email=%s AND password=%s
            """, (email, password))
            user = cur.fetchone()

    if not user:
        return render_template("loging.html", error="Email ou mot de passe incorrect !")

    session["user_id"] = user[0]
    session["email"] = user[1]
    session["username"] = user[2]
    session.permanent = True

    return redirect(url_for("choices"))

@app.route("/choices")
def choices():
    if "user_id" not in session:
        return redirect(url_for("home"))

    return render_template("choices.html", name=session["username"])

@app.route("/index")
def index():
    if "user_id" not in session:
        return redirect(url_for("home"))

    return render_template("index.html",
                           email=session["email"],
                           mstr=session["username"])

@app.route("/submit", methods=["POST"])
def submit():
    if "user_id" not in session:
        return redirect(url_for("home"))

    url = request.form.get("url")
    seuil = request.form.get("seuil")
    nom = request.form.get("nom")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tracking (product_name, url, seuil, user_id)
                VALUES (%s,%s,%s,%s)
            """, (nom, url, seuil, session["user_id"]))
            conn.commit()

    return render_template("succes.html")

@app.route("/products")
def products():
    if "user_id" not in session:
        return redirect(url_for("home"))

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT e.id, e.product_name, e.url, e.seuil, s.price
                FROM tracking e
                LEFT JOIN LATERAL (
                    SELECT price
                    FROM scrap s
                    WHERE s.product_id = e.id
                    ORDER BY s.scrap_date DESC
                    LIMIT 1
                ) s ON true
                WHERE e.user_id = %s
                ORDER BY e.id
            """, (session["user_id"],))
            rows = cur.fetchall()

    products = [
        {
            "id": r[0],
            "product_name": r[1],
            "url": r[2],
            "seuil": r[3],
            "last_price": r[4]
        }
        for r in rows
    ]

    return render_template("products.html", products=products)

@app.route("/update_seuil/<int:product_id>", methods=["POST"])
def update_seuil(product_id):
    if "user_id" not in session:
        return redirect(url_for("home"))

    new_seuil = request.form.get("seuil")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE tracking
                SET seuil=%s
                WHERE id=%s AND user_id=%s
            """, (new_seuil, product_id, session["user_id"]))
            conn.commit()

    return redirect(url_for("products"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
