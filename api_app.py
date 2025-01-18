from flask import Blueprint, request, jsonify

api_app = Blueprint("api_app", __name__)

def calculate_lot_size(account_balance, risk_mode, risk_value, stop_loss_pips, pip_value):
    """Berechnet die Lotgröße basierend auf dem Risikomanagement."""
    try:
        if risk_mode == "fixed_lots":
            return risk_value  # Feste Lotgröße
        elif risk_mode == "fixed_cash":
            return round(risk_value / (stop_loss_pips * pip_value), 5)
        elif risk_mode == "percent":
            risk_amount = (risk_value / 100) * account_balance
            return round(risk_amount / (stop_loss_pips * pip_value), 5)
        else:
            raise ValueError("Ungültiger Risikomodus")
    except Exception as e:
        print("Fehler bei der Lotgrößenberechnung:", e)
        return 0

@api_app.route("/process_signal_with_cases", methods=["POST"])
def process_signal_with_cases():
    try:
        data = request.get_json()
        print("Received Data:", data)  # Debugging
        signal_text = data.get("signal_text", "")
        user_options = data.get("user_options", {})

        # Dummy parsed signal (ersetzbar durch echte Parsing-Logik)
        parsed_signal = {
            "symbol": "EURUSD",
            "action": "Sell",
            "entry_price": 1.12345,
            "stop_loss": 1.12000,
            "take_profits": [1.12500, 1.12600],
            "pip_value": 10,  # Beispielhafter Pip-Wert (kann später dynamisch ermittelt werden)
            "stop_loss_pips": 50  # Beispielhafte Anzahl an Pips für SL
        }

        # Manuelle SL/TP-Optionen anwenden
        if user_options.get("manual_sl_tp"):
            manual_sl = user_options.get("manual_sl")
            manual_tp = user_options.get("manual_tp")

            if manual_sl:
                parsed_signal["stop_loss"] = manual_sl
            if manual_tp:
                parsed_signal["take_profits"] = manual_tp

        # Risikomanagement anwenden
        risk_mode = user_options.get("risk_mode", "percent")
        risk_value = user_options.get("risk_value", 0.5)  # Standardwert: 0.5%
        account_balance = user_options.get("account_balance", 1000)  # Standardwert: 1000

        lot_size = calculate_lot_size(
            account_balance,
            risk_mode,
            risk_value,
            parsed_signal["stop_loss_pips"],
            parsed_signal["pip_value"]
        )

        parsed_signal["lot_size"] = lot_size

        return jsonify({"processed_signal": parsed_signal})
    except Exception as e:
        print("Error:", e)  # Debugging
        return jsonify({"error": str(e)}), 400
