import requests
import schedule
import time
from datetime import datetime, timedelta
import pytz

# ============================================

# CONFIGURATION

# ============================================

TELEGRAM_TOKEN = “8710635829:AAG2rL4hQ5XBf17F5mn7nhiIViAO6824WRg”
CHAT_ID = “5111483159”

# ============================================

# ENVOYER UN MESSAGE TELEGRAM

# ============================================

def send_telegram(message):
url = f”https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage”
payload = {
“chat_id”: CHAT_ID,
“text”: message,
“parse_mode”: “HTML”
}
try:
response = requests.post(url, json=payload, timeout=10)
if response.status_code == 200:
print(f”✅ Message envoyé”)
else:
print(f”❌ Erreur: {response.text}”)
except Exception as e:
print(f”❌ Exception: {e}”)

# ============================================

# INSTRUCTIONS ROBOT SELON LE TYPE DE NEWS

# ============================================

def get_robot_instructions(event_title, event_time):
title_lower = event_title.lower()

```
# NFP — 1er vendredi du mois
if any(kw in title_lower for kw in ['non-farm', 'nfp', 'payroll']):
    return f"""🔴 <b>NFP DÉTECTÉ — {event_title}</b>
```

⛔ <b>COUPE LE ROBOT TOUTE LA JOURNÉE !</b>

📋 <b>Instructions MT5 :</b>
→ Désactive <b>Algo Trading</b> ce matin
→ Ne relance que lundi matin

⚠️ Mouvement possible : 100-200 pips”””

```
# CPI
elif any(kw in title_lower for kw in ['cpi', 'consumer price']):
    broker_hour = 15  # 14h30 réel + 1h broker
    return f"""🔴 <b>CPI DÉTECTÉ — {event_title}</b>
```

⏸️ <b>BLOQUE LE ROBOT DE 14h30 À 16h00 !</b>

📋 <b>Instructions MT5 ce matin :</b>
<code>NewsBlockHour = {broker_hour}</code>
<code>NewsBlockDuration = 90</code>

✅ Le robot reprendra automatiquement à 16h00
⚠️ Mouvement possible : 50-80 pips”””

```
# FOMC / Fed Rate Decision
elif any(kw in title_lower for kw in ['fomc', 'fed rate', 'interest rate', 'federal funds']):
    broker_hour = 20  # 20h réel = 20h broker
    return f"""🔴 <b>FOMC DÉTECTÉ — {event_title}</b>
```

⏸️ <b>BLOQUE LE ROBOT À PARTIR DE 19h30 !</b>

📋 <b>Instructions MT5 ce matin :</b>
<code>NewsBlockHour = {broker_hour}</code>
<code>NewsBlockDuration = 120</code>

✅ Le robot reprendra automatiquement à 22h00
⚠️ Mouvement possible : 80-150 pips”””

```
# Autres news USD importantes
else:
    return f"""🟡 <b>NEWS USD — {event_title}</b>
```

✅ Le robot peut continuer à trader
→ Impact modéré, pas besoin de couper
→ Surveille si grosse surprise”””

# ============================================

# RÉCUPÉRER LES NEWS ÉCONOMIQUES

# ============================================

def get_economic_news():
try:
url = “https://nfs.faireconomy.media/ff_calendar_thisweek.json”
response = requests.get(url, timeout=10)

```
    if response.status_code != 200:
        return []

    events = response.json()

    # Keywords pour l'or
    gold_keywords = [
        'non-farm', 'payroll', 'nfp',
        'fed', 'fomc', 'interest rate', 'federal funds',
        'cpi', 'consumer price',
        'gdp', 'unemployment', 'powell',
        'pce', 'inflation'
    ]

    result = []
    for event in events:
        if event.get('impact') != 'High':
            continue
        if event.get('country') != 'USD':
            continue

        title = event.get('title', '').lower()
        is_relevant = any(kw in title for kw in gold_keywords)

        if is_relevant:
            result.append({
                'title': event.get('title', ''),
                'date': event.get('date', ''),
                'time': event.get('time', ''),
                'impact': event.get('impact', ''),
            })

    return result

except Exception as e:
    print(f"Erreur news: {e}")
    return []
```

# ============================================

# ENVOYER LE RÉCAP DU SOIR

# ============================================

def send_daily_recap():
print(f”📊 Envoi récap… {datetime.now()}”)

```
events = get_economic_news()

# Filtrer les events de demain
tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
tomorrow_events = [e for e in events if tomorrow in e.get('date', '')]

if not tomorrow_events:
    message = """📅 <b>RÉCAP NEWS OR — DEMAIN</b>
```

✅ Aucune annonce majeure USD demain !
🤖 Le robot peut trader normalement.

<code>NewsBlockHour = 0</code>”””
else:
message = “📅 <b>⚠️ RÉCAP NEWS OR — DEMAIN</b>\n\n”
for event in tomorrow_events:
message += get_robot_instructions(event[‘title’], event[‘time’])
message += “\n\n━━━━━━━━━━━━━━━━━━━━\n\n”

```
send_telegram(message)
```

# ============================================

# MESSAGE DE DÉMARRAGE

# ============================================

def send_startup_message():
message = “”“🤖 <b>XAUBOT NEWS BOT ACTIF !</b>

✅ Surveillance des news USD en cours
📅 Récap quotidien : <b>chaque soir à 20h</b>

<b>Je t’alerterai pour :</b>
🔴 NFP → Journée off
🔴 CPI → NewsBlockHour = 15
🔴 FOMC → NewsBlockHour = 20

🥇 Bonne chance sur le challenge FXIFY !”””

```
send_telegram(message)
```

# ============================================

# MAIN

# ============================================

def main():
print(“🚀 XauBot News Bot démarré…”)

```
send_startup_message()

# Récap chaque soir à 20h
schedule.every().day.at("20:00").do(send_daily_recap)

# Test immédiat au démarrage
send_daily_recap()

print("⏰ Bot actif — récap à 20h chaque soir")

while True:
    schedule.run_pending()
    time.sleep(60)
```

if **name** == “**main**”:
main()
