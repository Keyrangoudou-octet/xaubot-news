import requests
import schedule
import time
from datetime import datetime, timedelta
import pytz

TELEGRAM_TOKEN = "8710635829:AAG2rL4hQ5XBf17F5mn7nhiIViAO6824WRg"
CHAT_ID = "5111483159"

def send_telegram(message):
    url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("Message envoye")
        else:
            print("Erreur: " + response.text)
    except Exception as e:
        print("Exception: " + str(e))

def get_robot_instructions(event_title, event_time):
    title_lower = event_title.lower()

    if any(kw in title_lower for kw in ["non-farm", "nfp", "payroll"]):
        return "<b>NFP DETECTE - " + event_title + "</b>\n\nCOUPE LE ROBOT TOUTE LA JOURNEE !\n\nDesactive Algo Trading ce matin\nNe relance que lundi matin\n\nMouvement possible : 100-200 pips"

    elif any(kw in title_lower for kw in ["cpi", "consumer price"]):
        return "<b>CPI DETECTE - " + event_title + "</b>\n\nBLOQUE LE ROBOT DE 14h30 A 16h00 !\n\nInstructions MT5 ce matin :\nNewsBlockHour = 15\nNewsBlockDuration = 90\n\nLe robot reprendra automatiquement a 16h00\nMouvement possible : 50-80 pips"

    elif any(kw in title_lower for kw in ["fomc", "fed rate", "interest rate", "federal funds"]):
        return "<b>FOMC DETECTE - " + event_title + "</b>\n\nBLOQUE LE ROBOT A PARTIR DE 19h30 !\n\nInstructions MT5 ce matin :\nNewsBlockHour = 20\nNewsBlockDuration = 120\n\nLe robot reprendra automatiquement a 22h00\nMouvement possible : 80-150 pips"

    else:
        return "<b>NEWS USD - " + event_title + "</b>\n\nLe robot peut continuer a trader\nImpact modere, pas besoin de couper\nSurveille si grosse surprise"

def get_economic_news():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return []

        events = response.json()

        gold_keywords = [
            "non-farm", "payroll", "nfp",
            "fed", "fomc", "interest rate", "federal funds",
            "cpi", "consumer price",
            "gdp", "unemployment", "powell",
            "pce", "inflation"
        ]

        result = []
        for event in events:
            if event.get("impact") != "High":
                continue
            if event.get("country") != "USD":
                continue

            title = event.get("title", "").lower()
            is_relevant = any(kw in title for kw in gold_keywords)

            if is_relevant:
                result.append({
                    "title": event.get("title", ""),
                    "date": event.get("date", ""),
                    "time": event.get("time", ""),
                    "impact": event.get("impact", ""),
                })

        return result

    except Exception as e:
        print("Erreur news: " + str(e))
        return []

def send_daily_recap():
    print("Envoi recap... " + str(datetime.now()))

    events = get_economic_news()

    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow_events = [e for e in events if tomorrow in e.get("date", "")]

    if not tomorrow_events:
        message = "RECAP NEWS OR - DEMAIN\n\nAucune annonce majeure USD demain !\nLe robot peut trader normalement.\n\nNewsBlockHour = 0"
    else:
        message = "RECAP NEWS OR - DEMAIN\n\n"
        for event in tomorrow_events:
            message += get_robot_instructions(event["title"], event["time"])
            message += "\n\n--------------------\n\n"

    send_telegram(message)

def send_startup_message():
    message = "XAUBOT NEWS BOT ACTIF !\n\nSurveillance des news USD en cours\nRecap quotidien : chaque soir a 20h\n\nJe t alerte pour :\nNFP - Journee off\nCPI - NewsBlockHour = 15\nFOMC - NewsBlockHour = 20\n\nBonne chance sur le challenge FXIFY !"
    send_telegram(message)

def main():
    print("XauBot News Bot demarre...")

    send_startup_message()

    schedule.every().day.at("20:00").do(send_daily_recap)

    send_daily_recap()

    print("Bot actif - recap a 20h chaque soir")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
