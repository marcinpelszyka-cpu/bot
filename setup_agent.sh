#!/bin/bash
echo "======================================================="
echo "🌪️ Rozpoczynam inicjalizację bazy dla NemoClaw i Radaru..."
echo "======================================================="

# 1. Sprawdzenie wymagań (Go i Node do budowy darmowego Agenta)
if ! command -v go &> /dev/null
then
    echo "[!] Brak krytycznego języka Golang do kompilacji Agenta! Maszyna z .devcontainer nie zbudowała się poprawnie."
    exit 1
fi
echo "[+] Maszyna chmurowa posiada wbudowane Golang & Node.js."

# 2. Tworzenie czystego środowiska Pythona (radaru) i instalacja zależności
echo "[ ] Inicjowanie środowiska Python venv..."
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
echo "[+] Zależności radaru zainstalowane."

# 3. Konfiguracja pliku .env pod Twoje API (Nemotron 120B Nvidii)
ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
    echo "TUTAJ_WKLEJ_SWOJ_KLUCZ_NVIDIA" > $ENV_FILE
    echo "OPENROUTER_API_KEY=\"TUTAJ_ZASTAP_KLUCZEM_NVIDIA_LUB_INNYM\"" >> $ENV_FILE
    echo "[+] Utworzono szablon .env na dane dostępowe do darmowego modelu!"
else
    echo "[+] Plik .env już istnieje w kontenerze."
fi

echo "======================================================="
echo "✅ Instalacja chmury GitHub Codespaces dla projektu 'Huragan' zakończona!"
echo ""
echo "🔥 Aby odpalić swój detektor (Radar):"
echo "  ./venv/bin/python3 radar.py"
echo ""
echo "🧠 OTWÓRZ plik .env po lewej stronie i wklej swój darmowy stamtąd NVIDIA_API_KEY!"
echo "======================================================="
