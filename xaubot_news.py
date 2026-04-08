import requests
import schedule
import time
from datetime import datetime, timedelta

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


def get_robot_instructions(event_title, impact):
    title_lower = event_title.lower()

    if any(kw in title_lower for kw in ["non-farm", "nfp", "payroll"]):
        return "NFP - " + event_title + "\n\nCOUPE LE ROBOT TOUTE LA JOURNEE\nDesactive Algo Trading\nNe relance que lundi"

    elif any(kw in title_lower for kw in ["cpi", "consumer price"]):
        return "CPI - " + event_title + "\n\nNewsBlockHour = 15\nNewsBlockDuration = 90"

    elif any(kw in title_lower for kw in ["fomc", "fed rate", "interest rate", "federal funds"]):
        return "FOMC - " + event_title + "\n\nNewsBlockHour = 20\nNewsBlockDuration = 120"

    elif any(kw in title_lower for kw in ["powell", "fed chair"]):
        return "POWELL - " + event_title + "\n\nSurveille le marche\nCoupe si ca bouge fort"

    elif any(kw in title_lower for kw in ["trump", "president trump"]):
        return "TRUMP - " + event_title + "\n\nATTENTION IMPREVISIBLE\nCoupe si annonce importante"

    elif impact == "High":
        return "IMPACT FORT - " + event_title + "\n\nSurveille le marche\nReste vigilant"

    elif impact == "Medium":
        return "IMPACT MOYEN - " + event_title + "\n\nRobot peut trader\nReste vigilant si surprise"

    else:
        return "IMPACT FAIBLE - " + event_title + "\n\nRobot tourne normalement"


def get_economic_news():
    try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return []

        events = response.json()
        result = []

        for event in events:
            if event.get("country") != "USD":
                continue

            if event.get("impact") not in ["High", "Medium", "Low"]:
                continue

            result.append({
                "title": event.get("title", ""),
                "date": event.get("date", ""),
                "time": event.get("time", ""),
                "impact": event.get("impact", "")
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
        message = "RECAP NEWS OR - DEMAIN\n\nAucune annonce USD demain\nNewsBlockHour = 0\nRobot tourne normalement"
    else:
        message = "RECAP NEWS OR - DEMAIN\n\n"

        for event in tomorrow_events:
            impact = event["impact"]

            if impact == "High":
                label = "[FORT]"
            elif impact == "Medium":
                label = "[MOYEN]"
            else:
                label = "[FAIBLE]"

            message += label + " " + event["time"] + " - " + event["title"] + "\n"
            message += get_robot_instructions(event["title"], impact)
            message += "\n\n---\n\n"

    send_telegram(message)


def send_startup_message():
    message = (
        "XAUBOT NEWS BOT ACTIF\n\n"
        "Toutes les news USD surveillees\n"
        "Recap chaque soir a 18h\n\n"
        "NFP - Journee off\n"
        "CPI - NewsBlockHour = 15\n"
        "FOMC - NewsBlockHour = 20\n"
        "Powell - Surveille\n"
        "Trump - Attention\n"
        "Fort - Surveille\n"
        "Moyen - Robot peut trader\n"
        "Faible - Aucune action"
    )
    send_telegram(message)


def main():
    print("XauBot News Bot demarre...")
    send_startup_message()

    schedule.every().day.at("18:00").do(send_daily_recap)

    send_daily_recap()
    print("Bot actif")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
