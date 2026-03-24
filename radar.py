import requests
import time
import os

# ==========================================
# ⚙️ KONFIGURACJA DOWÓDCY (WPISZ SWOJE DANE)
# ==========================================
HELIUS_API_KEY = "69fbb73f-0c33-4573-af91-0b01af1995b1"
TELEGRAM_BOT_TOKEN = "8625780354:AAG4H0wF-w2-xy--Lh_0ng8cEvORE15Ayxg"
TELEGRAM_CHAT_ID = "8530883329"

TARGET_FILE = "TARGET_LIST.txt"
CHECK_INTERVAL = 10  # Jak często sprawdzamy (w sekundach)

# Pamięć podręczna, żeby nie wysyłać powiadomień o starych transakcjach
seen_signatures = set()

def load_targets():
    """Wczytuje portfele z pliku TARGET_LIST.txt"""
    if not os.path.exists(TARGET_FILE):
        print(f"[!] Brak pliku {TARGET_FILE}. Utwórz go i wpisz adresy.")
        return []
    with open(TARGET_FILE, 'r') as f:
        targets = [line.split()[0].strip() for line in f if line.strip() and not line.startswith('#')]
    return targets

def send_telegram_alert(wallet, tx_type, signature, description):
    """Wysyła sformatowany alert na Twój telefon"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Skrócony adres dla czytelności
    short_wallet = f"{wallet[:4]}...{wallet[-4:]}"
    
    message = (
        f"🚨 <b>CEL ZAAKTYWOWANY!</b> 🚨\n\n"
        f"👤 <b>Portfel:</b> <code>{wallet}</code>\n"
        f"⚡ <b>Akcja:</b> {tx_type}\n"
        f"📝 <b>Szczegóły:</b> {description}\n\n"
        f"🔗 <a href='https://solscan.io/tx/{signature}'>Sprawdź na Solscan</a>\n"
        f"🦅 <a href='https://trade.padre.gg/'>Otwórz Padre.gg</a>"
    )
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        requests.post(url, json=payload)
        print(f"[TG] Wysłano alert dla portfela {short_wallet}!")
    except Exception as e:
        print(f"[BŁĄD TG] Nie udało się wysłać alertu: {e}")

def check_wallet_activity(wallet, is_prefill=False):
    """Odpytuje Helius API o najnowsze transakcje danego portfela"""
    url = f"https://api.helius.xyz/v0/addresses/{wallet}/transactions?api-key={HELIUS_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return
            
        transactions = response.json()
        
        for tx in transactions:
            sig = tx.get("signature")
            
            # Jeśli już widzieliśmy tę transakcję, ignorujemy
            if sig in seen_signatures:
                continue
                
            seen_signatures.add(sig)
            
            # Interesują nas tylko konkretne typy akcji (np. SWAP)
            tx_type = tx.get("type")
            source = tx.get("source", "")
            
            # Filtrujemy szum: Szukamy transakcji na giełdach (Raydium, Pump.fun)
            if tx_type == "SWAP" or source in ["RAYDIUM", "PUMP_FUN"]:
                desc = tx.get("description", "Brak opisu transakcji")
                if is_prefill:
                    print(f"[PAMIĘĆ] Zapisano w historii (brak alertu TG): {tx_type} na {source}")
                else:
                    print(f"[WYKRYTO] {wallet[:8]}... zrobił {tx_type} na {source}")
                    send_telegram_alert(wallet, tx_type, sig, desc)
                
    except Exception as e:
        print(f"[BŁĄD API] Problem z portfelem {wallet}: {e}")

def main():
    print("==================================================")
    print("🌪️ RADAR 'HURAGAN' URUCHOMIONY")
    print("📡 Oczekiwanie na ruch celów...")
    print("==================================================")
    
    targets = load_targets()
    print(f"[+] Wczytano {len(targets)} celów do obserwacji.")
    
    # Pre-fill (wypełniamy pamięć starymi transakcjami, żeby nie zalało Cię alertami na start)
    for wallet in targets:
        check_wallet_activity(wallet, is_prefill=True)
        
    print("[+] Pamięć zsynchronizowana. Rozpoczynam nasłuch w czasie rzeczywistym.\n")
    
    while True:
        targets = load_targets() # Przeładowujemy w locie, jakbyś dodał nowy portfel!
        for wallet in targets:
            check_wallet_activity(wallet)
            time.sleep(1) # Małe opóźnienie, żeby nie zablokowali nam darmowego API
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
