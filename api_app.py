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
            "entry_price": 1.1234,
            "stop_loss": 1.1200,
            "take_profits": [1.1250, 1.1260]
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
