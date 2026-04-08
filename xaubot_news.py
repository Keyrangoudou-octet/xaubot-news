import requests
import schedule
import time
from datetime import datetime, timedelta
TELEGRAM_TOKEN = "8710635829:AAG2rL4hQ5XBf17F5mn7nhiIViAO6824WRg"
CHAT_ID = "5111483159"
def send_telegram(message):
url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
try:
response = requests.post(url, json=payload, timeout=10)
if response.status_code == 200:
print("Message envoye")
else:
print("Erreur: " + response.text)
except Exception as e:
print("Exception: " + str(e))
def get_robot_instructions(event_title, event_time, impact):
title_lower = event_title.lower()
if any(kw in title_lower for kw in ["non-farm", "nfp", "payroll"]):
return "NFP DETECTE - " + event_title + "\n\nCOUPE LE ROBOT TOUTE LA JOURNEE !\nDesactive Algo
Trading ce matin\nNe relance que lundi matin\nMouvement possible : 100-200 pips"
elif any(kw in title_lower for kw in ["cpi", "consumer price"]):
return "CPI DETECTE - " + event_title + "\n\nBLOQUE LE ROBOT !\nInstructions MT5
:\nNewsBlockHour = 15\nNewsBlockDuration = 90\nMouvement possible : 50-80 pips"
elif any(kw in title_lower for kw in ["fomc", "fed rate", "interest rate", "federal funds"]):
return "FOMC DETECTE - " + event_title + "\n\nBLOQUE LE ROBOT A PARTIR DE 19h30 !\nInstructions
MT5 :\nNewsBlockHour = 20\nNewsBlockDuration = 120\nMouvement possible : 80-150 pips"
elif any(kw in title_lower for kw in ["powell", "fed chair"]):
return "POWELL SPEAKS - " + event_title + "\n\nSURVEILLE LE MARCHE !\nRobot peut trader mais
reste vigilant\nSi ca bouge fort -> coupe Algo Trading\nMouvement possible : 30-80 pips"
elif any(kw in title_lower for kw in ["trump speaks", "president trump"]):
return "TRUMP SPEAKS - " + event_title + "\n\nATTENTION IMPREVISIBLE !\nSurveille le marche de
pres\nSi annonce importante -> coupe Algo Trading\nMouvement possible : 50-150 pips"
elif impact == "High":
return "IMPACT FORT - " + event_title + "\n\nSurveille le marche !\nRobot peut trader mais
reste vigilant\nMouvement possible : 20-50 pips"
elif impact == "Medium":
return "IMPACT MOYEN - " + event_title + "\n\nRobot peut trader normalement\nPas besoin de
couper\nReste vigilant si surprise"
else:
return "IMPACT FAIBLE - " + event_title + "\n\nRobot tourne normalement\nAucune action requise"
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
message = "RECAP NEWS OR - DEMAIN\n\nAucune annonce USD demain !\nRobot peut trader
normalement.\nNewsBlockHour = 0"
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
message += get_robot_instructions(event["title"], event["time"], event["impact"])
message += "\n\n--------------------\n\n"
send_telegram(message)
def send_startup_message():
message = "XAUBOT NEWS BOT ACTIF !\n\nSurveillance de toutes les news USD\nRecap quotidien :
chaque soir a 18h\n\nPriorites :\nNFP - Journee off\nCPI - NewsBlockHour = 15\nFOMC -
NewsBlockHour = 20\nPowell Speaks - Surveille\nTrump Speaks - Attention danger\nImpact Fort -
Surveille\nImpact Moyen - Robot peut trader\nImpact Faible - Aucune action\n\nBonne chance sur
le challenge !"
send_telegram(message)
def main():
print("XauBot News Bot demarre...")
send_startup_message()
schedule.every().day.at("18:00").do(send_daily_recap)
send_daily_recap()
print("Bot actif - recap a 18h chaque soir")
while True:
schedule.run_pending()
time.sleep(60)
if __name__ == "__main__":
main()
