import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Configuration e-mail
EMAIL_SENDER = "boursemails@gmail.com"
EMAIL_RECEIVER = "boursemails@gmail.com"
EMAIL_PASSWORD = "zkbq tprd qmnb qzkz"  

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
        print(f"Scraping page {page}...")

        r = requests.get(url, params=PARAMS)
        if r.status_code != 200:
            break

        soup = BeautifulSoup(r.text, "lxml")
        table = soup.find("table")
        if not table:
            break

        rows = table.find_all("tr")[1:]  # skip header
        if not rows:
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

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

if __name__ == "__main__":
    data = scrape_all_pages()
    if data:
        send_email(data)
        print("✅ Email envoyé avec succès.")
    else:
        print("⚠ Aucune donnée trouvée.")
