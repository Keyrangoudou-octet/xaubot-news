import requests
import schedule
import time
from datetime import datetime, timedelta
import pytz

TELEGRAM_TOKEN = "8710635829:AAG2rL4hQ5XBf17F5mn7nhiIViAO6824WRg"
CHAT_ID = "5111483159"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erreur: {e}")

def get_economic_news():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []
        events = response.json()
        gold_keywords = ['nfp','non-farm','payroll','fed','fomc','interest rate',
            'cpi','inflation','gdp','unemployment','powell','treasury','pce']
        result = []
        for event in events:
            if event.get('impact') not in ['High', 'Medium']:
                continue
            title = event.get('title', '').lower()
            is_relevant = any(kw in title for kw in gold_keywords)
            if event.get('country') == 'USD' and event.get('impact') == 'High':
                is_relevant = True
            if is_relevant:
                result.append({
                    'title': event.get('title', ''),
                    'time': event.get('time', ''),
                    'impact': event.get('impact', ''),
                    'forecast': event.get('forecast', 'N/A'),
                })
        return result
    except Exception as e:
        print(f"Erreur news: {e}")
        return []

def send_daily_recap():
    events = get_economic_news()
    if not events:
        message = "📅 <b>RÉCAP NEWS OR — DEMAIN</b>\n\n✅ Aucune annonce majeure.\nLe robot peut trader normalement ! 🤖"
    else:
        message = "📅 <b>⚠️ RÉCAP NEWS OR — DEMAIN</b>\n\n🔴 <b>Annonces qui impactent l'or :</b>\n\n"
        for event in events[:8]:
            emoji = "🔴" if event['impact'] == 'High' else "🟡"
            message += f"{emoji} <b>{event['time']}</b> — {event['title']}\n"
        message += "\n━━━━━━━━━━━━━━━━━━━━\n"
        message += "⚠️ <b>CONSEIL :</b> Coupe le robot avant ces annonces !\n"
        message += "▶️ Relance 30 minutes après."
    send_telegram(message)

def main():
    send_telegram("🤖 <b>XAUBOT NEWS BOT DÉMARRÉ !</b>\n\n✅ Récap quotidien à 20h chaque soir\n⚠️ Alertes avant chaque news importante\n\n🥇 Bonne chance sur le challenge FXIFY !")
    schedule.every().day.at("20:00").do(send_daily_recap)
    send_daily_recap()
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
