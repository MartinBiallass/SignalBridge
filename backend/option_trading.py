import re
import time
from threading import Timer

class OptionTradeManager:
    def __init__(self):
        self.active_trades = {}

    def parse_signal(self, signal_text):
        """
        Parst das Signal und extrahiert Kauf/Verkauf sowie die Laufzeit
        """
        trade_info = {}
        
        # Kauf/Verkauf erkennen
        if "BUY" in signal_text.upper():
            trade_info['type'] = 'BUY'
        elif "SELL" in signal_text.upper():
            trade_info['type'] = 'SELL'
        else:
            return None  # Kein gültiges Signal
        
        # Laufzeit extrahieren (z. B. "30 min", "1 hour")
        time_match = re.search(r'(\d+)\s*(min|hour|h)', signal_text, re.IGNORECASE)
        if time_match:
            duration = int(time_match.group(1))
            unit = time_match.group(2).lower()
            
            if "hour" in unit or "h" in unit:
                duration *= 60  # In Minuten umwandeln
            
            trade_info['duration'] = duration
        else:
            return None  # Keine gültige Zeitangabe
        
        return trade_info
    
    def open_trade(self, trade_id, signal_text):
        """
        Öffnet einen Trade basierend auf dem Signal
        """
        trade_data = self.parse_signal(signal_text)
        if not trade_data:
            print("❌ Ungültiges Signal: ", signal_text)
            return
        
        self.active_trades[trade_id] = trade_data
        print(f"✅ Neuer {trade_data['type']} Trade eröffnet für {trade_data['duration']} Minuten")
        
        # Timer setzen für automatisches Schließen
        Timer(trade_data['duration'] * 60, self.close_trade, [trade_id]).start()
    
    def close_trade(self, trade_id):
        """
        Schließt den Trade automatisch nach Ablauf der Zeit
        """
        if trade_id in self.active_trades:
            print(f"🔴 Trade {trade_id} automatisch geschlossen nach {self.active_trades[trade_id]['duration']} Minuten")
            del self.active_trades[trade_id]
        else:
            print(f"⚠️ Trade {trade_id} bereits geschlossen oder nicht gefunden.")

# Beispielhafte Nutzung
trade_manager = OptionTradeManager()

# Test-Signale
trade_manager.open_trade("T1", "BUY EURUSD 30 min")
trade_manager.open_trade("T2", "SELL GBPUSD 1 hour")
