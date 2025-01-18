from flask import Blueprint, request, jsonify

api_app = Blueprint("api_app", __name__)

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
            "take_profits": [1.12500, 1.12600]
        }

        # Manuelle SL/TP-Optionen anwenden
        if user_options.get("manual_sl_tp"):
            manual_sl = user_options.get("manual_sl")
            manual_tp = user_options.get("manual_tp")

            if manual_sl:
                parsed_signal["stop_loss"] = manual_sl
            if manual_tp:
                parsed_signal["take_profits"] = manual_tp

        return jsonify({"processed_signal": parsed_signal})
    except Exception as e:
        print("Error:", e)  # Debugging
        return jsonify({"error": str(e)}), 400


@api_app.route("/calculate_lot_size", methods=["POST"])
def calculate_lot_size():
    try:
        data = request.get_json()
        print("Received Data:", data)  # Debugging

        # Eingaben
        account_balance = data.get("account_balance", 0)
        risk_mode = data.get("risk_mode", "")
        risk_value = data.get("risk_value", 0)
        fixed_lot_size = data.get("fixed_lot_size", 0.01)
        stop_loss_pips = data.get("stop_loss_pips", 0)
        pip_value = data.get("pip_value", 10)  # Annahme: $10 pro Lot

        if not account_balance or not risk_mode:
            raise ValueError("Account balance and risk mode are required.")

        # Berechnungslogik
        lot_size = 0
        if risk_mode == "fixed_lot":
            lot_size = fixed_lot_size
        elif risk_mode == "fixed_amount":
            if stop_loss_pips <= 0 or pip_value <= 0:
                raise ValueError("Stop-loss pips and pip value must be greater than 0.")
            lot_size = round(risk_value / (stop_loss_pips * pip_value), 5)
        elif risk_mode == "percent":
            if stop_loss_pips <= 0 or pip_value <= 0:
                raise ValueError("Stop-loss pips and pip value must be greater than 0.")
            risk_amount = account_balance * (risk_value / 100)
            lot_size = round(risk_amount / (stop_loss_pips * pip_value), 5)
        elif risk_mode == "pip_value":
            if pip_value <= 0:
                raise ValueError("Pip value must be greater than 0.")
            lot_size = round(risk_value / pip_value, 5)
        else:
            raise ValueError("Invalid risk mode provided.")

        # Ergebnis zurückgeben
        return jsonify({
            "account_balance": account_balance,
            "risk_mode": risk_mode,
            "risk_value": risk_value,
            "stop_loss_pips": stop_loss_pips,
            "pip_value": pip_value,
            "calculated_lot_size": lot_size
        })
    except Exception as e:
        print("Error:", e)  # Debugging
        return jsonify({"error": str(e)}), 400
