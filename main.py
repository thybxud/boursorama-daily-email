import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import os
import sys

# Lecture des variables depuis les Secrets GitHub
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# Vérification des variables obligatoires
if not EMAIL_SENDER or not EMAIL_RECEIVER or not EMAIL_PASSWORD:
    print("❌ Erreur : Variables d'environnement EMAIL_SENDER, EMAIL_RECEIVER ou EMAIL_PASSWORD manquantes.")
    sys.exit(1)

# URL de base
BASE_URL = "https://www.boursorama.com/bourse/actions/consensus/recommandations-paris/"
PARAMS = {
    "national_market_filter[market]": "1rPCAC",
    "national_market_filter[sector]": "",
    "national_market_filter[analysts]": "",
    "national_market_filter[period]": "2025",
    "national_market_filter[filter]": ""
}

def scrape_all_pages():
    page = 1
    results = []

    while True:
        url = f"{BASE_URL}page-{page}"
        print(f"📄 Scraping page {page}...")

        try:
            r = requests.get(url, params=PARAMS, timeout=10)
        except Exception as e:
            print(f"⚠ Erreur de connexion HTTP : {e}")
            break

        if r.status_code != 200:
            print(f"⚠ HTTP {r.status_code} - arrêt du scraping.")
            break

        soup = BeautifulSoup(r.text, "lxml")
        table = soup.find("table")
        if not table:
            print("⚠ Pas de tableau trouvé - fin.")
            break

        rows = table.find_all("tr")[1:]  # skip header
        if not rows:
            print("⚠ Aucune ligne trouvée - fin.")
            break

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                action = cols[0].get_text(strip=True)
                reco = cols[1].get_text(strip=True)
                objectif = cols[2].get_text(strip=True)
                results.append((action, reco, objectif))

        page += 1
        time.sleep(1)  # éviter de spammer le serveur

    print(f"✅ Scraping terminé - {len(results)} lignes trouvées.")
    return results

def send_email(data):
    subject = "Récapitulatif des actions - Boursorama"
    body = "<h2>Résumé des recommandations</h2><table border='1'><tr><th>Action</th><th>Recommandation</th><th>Objectif</th></tr>"

    for action, reco, objectif in data:
        body += f"<tr><td>{action}</td><td>{reco}</td><td>{objectif}</td></tr>"

    body += "</table>"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        print("📨 Connexion à Gmail...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            print("🔑 Authentification...")
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            print("✉ Envoi du mail...")
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("✅ Email envoyé avec succès.")
    except smtplib.SMTPAuthenticationError as e:
        print("❌ Erreur d'authentification Gmail.")
        print(f"Détails : {e}")
    except Exception as e:
        print(f"⚠ Erreur lors de l'envoi de l'email : {e}")

if __name__ == "__main__":
    print("🚀 Lancement du script...")
    data = scrape_all_pages()
    if data:
        send_email(data)
    else:
        print("⚠ Aucune donnée trouvée.")

