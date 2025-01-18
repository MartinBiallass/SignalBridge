import requests
import json

# API-Endpunkt
url = "http://127.0.0.1:5000/api/process_signal_with_cases"

# Testdaten
payload = {
    "signal_text": "Test Signal",
    "user_options": {
        "manual_sl_tp": True,
        "manual_sl": 1.1100,
        "manual_tp": [1.1300, 1.1400]
    }
}

# Anfrage senden
response = requests.post(url, json=payload)

# Antwort anzeigen
print("Response Status Code:", response.status_code)
print("Response JSON:", response.json())
