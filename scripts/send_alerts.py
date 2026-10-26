"""Free personal garden alert sender; credentials only from GitHub Actions secrets."""
import datetime as dt
import json
import os
from zoneinfo import ZoneInfo
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

PROJECT = os.environ.get('PROJECT_ID', 'garden-guardian-e6178')
TOKEN = os.environ['FCM_DEVICE_TOKEN']
SERVICE_ACCOUNT = json.loads(os.environ['FCM_SERVICE_ACCOUNT_JSON'])
TIMEZONE = ZoneInfo('America/Los_Angeles')
now = dt.datetime.now(TIMEZONE)


def send(title, body):
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT, scopes=['https://www.googleapis.com/auth/firebase.messaging'])
    credentials.refresh(Request())
    payload = {'message': {'token': TOKEN, 'notification': {'title': title, 'body': body},
                           'webpush': {'fcm_options': {'link': 'https://flowerladyky.github.io/garden-guardian/'}}}}
    response = requests.post(f'https://fcm.googleapis.com/v1/projects/{PROJECT}/messages:send',
                             json=payload, headers={'Authorization': f'Bearer {credentials.token}'}, timeout=25)
    response.raise_for_status()
    print('Sent:', title)


url = 'https://api.open-meteo.com/v1/forecast'
response = requests.get(url, params={
    'latitude': 36.43, 'longitude': -119.69,
    'hourly': 'temperature_2m', 'temperature_unit': 'fahrenheit',
    'timezone': 'America/Los_Angeles', 'forecast_days': 3}, timeout=25)
response.raise_for_status()
forecast = response.json()['hourly']
upcoming = [(dt.datetime.fromisoformat(t).replace(tzinfo=TIMEZONE), temp)
            for t, temp in zip(forecast['time'], forecast['temperature_2m'])]
next36 = [(t, v) for t, v in upcoming if now <= t <= now + dt.timedelta(hours=36) and v is not None]
if not next36:
    raise RuntimeError('No future hourly forecast data; no alerts sent')
low = min(v for _, v in next36)
high = max(v for _, v in next36)
if low <= 36:
    send('❄️ Garden Guardian: Cold warning',
         f'Forecast near Laton may drop to {low:.0f}°F within 36 hours. Protect potted portulaca and other frost-sensitive plants.')
if high >= 100:
    send('☀️ Garden Guardian: Heat warning',
         f'Forecast near Laton may reach {high:.0f}°F within 36 hours. Check pots for dryness and protect heat-sensitive plants.')

# Morning checklists: a starter rotation, NOT synced to locally stored app tasks.
# Uses local hour to avoid duplicate care reminders on evening runs.
if 6 <= now.hour < 12:
    if now.weekday() == 0:
        send('🌿 Weekly plant check', 'Check soil moisture for your portulaca and bush lily; water only if needed. Inspect black anemones for stress.')
    if now.day == 1:
        send('🌱 Monthly garden care', 'Inspect plants for pests, drainage problems, and seasonal pruning needs. Check individual plant care notes before fertilizing.')
print('Completed checks at', now.isoformat(), 'low', low, 'high', high)
