from flask import Blueprint, request, jsonify

api_app = Blueprint("api_app", __name__)

@api_app.route("/process_signal_with_tp", methods=["POST"])
def process_signal_with_tp():
    try:
        data = request.get_json()
        print("Received Data:", data)  # Debugging

        signal_text = data.get("signal_text", "")
        user_options = data.get("user_options", {})

        # Dummy parsed signal (ersetzbar durch echte Parsing-Logik)
        parsed_signal = {
            "symbol": "EURUSD",
            "action": "Buy",
            "entry_price": data.get("entry_price", 1.12345),
            "stop_loss": data.get("stop_loss", 1.12000),
            "take_profits": []
        }

        # Verarbeite Take-Profit-Level
        tp_levels = user_options.get("take_profit_levels", [])
        lot_size = user_options.get("lot_size", 0.1)

        remaining_lot = lot_size
        for i, tp in enumerate(tp_levels):
            tp_percentage = tp.get("tp_percentage", 0) / 100
            tp_strategy = tp.get("strategy", "Default")
            offset_pips = tp.get("offset_pips", 0)

            # Berechnung der Teil-Lotgröße
            if i == len(tp_levels) - 1:  # Letzter Take-Profit-Level
                tp_lot = remaining_lot  # Weisen Sie die verbleibende Lotgröße zu
            else:
                tp_lot = round(lot_size * tp_percentage, 5)
                if tp_lot > remaining_lot:
                    tp_lot = remaining_lot  # Verhindere Überschuss

            remaining_lot -= tp_lot

            # Berechnung des Take-Profit-Preises
            tp_price = round(
                parsed_signal["entry_price"] + (offset_pips * 0.0001), 5
            )

            parsed_signal["take_profits"].append({
                "level": i + 1,
                "lot_size": tp_lot,
                "price": tp_price,
                "strategy": tp_strategy
            })

        # Entferne Debugging-Fehlerprüfung für verbleibende Lotgröße
        if remaining_lot > 0 and len(tp_levels) > 0:
            parsed_signal["take_profits"][-1]["lot_size"] += remaining_lot  # Füge Restlot zur letzten Position hinzu

        return jsonify({"processed_signal": parsed_signal})
    except Exception as e:
        print("Error:", e)  # Debugging
        return jsonify({"error": str(e)}), 400
