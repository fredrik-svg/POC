# AI Realtime POC (Alt 3) — Raspberry Pi 5 ↔ OpenAI Realtime

En superenkel **proof-of-concept** för röst-till-röst direkt mot **OpenAI Realtime API** från **Raspberry Pi 5**.
Valfri **mini-backend** följer med för att hantera uppladdning av dokument till **OpenAI Vector Stores** (RAG).

## Ladda ner projektet

1. Se till att du har **Git** installerat (`sudo apt-get install git` på Debian-baserade system).
2. Klona repot och gå in i katalogen:
   ```bash
   git clone https://github.com/openai/ai-realtime-poc.git
   cd ai-realtime-poc
   ```
   <small>Byt ut URL:en ovan om du använder en egen fork.</small>

Fortsätt därefter med instruktionerna nedan för respektive komponent.

## Arkitektur
```
[Pi 5] -- WebSocket --> OpenAI Realtime (röst in/ut)
                           \--(valfritt HTTP)--> mini-backend (FastAPI)
                                      └─ Response API + File Search (Vector Stores)
```

## Förutsättningar
- Raspberry Pi 5 med Raspberry Pi OS 64-bit.
- En OpenAI API-nyckel med Realtime-åtkomst.
- (Valfritt) En server/miljö för mini-backend (kan köras lokalt också).

---

## 1) Raspberry Pi 5 — röstklient

### Installera system- och Pythonberoenden
```bash
sudo apt-get update && sudo apt-get install -y python3-pip portaudio19-dev sox
python3 -m pip install -r pi-client/requirements.txt
```

### Konfigurera miljövariabler
Kopiera `.env.example` till `.env` och fyll i din nyckel:
```bash
cp pi-client/.env.example pi-client/.env
# EDITERA: OPENAI_API_KEY=...
```

### Kör klienten
```bash
python3 pi-client/pi_realtime_client.py
```
- Tryck **Enter** för att signalera att du är klar med ett yttrande och vill ha svar.
- Modellen svarar med ljud som spelas upp via **sox**.

### (Valfritt) Köra som systemd-tjänst
1. Uppdatera sökvägen i `pi-client/systemd/ai-voice-client.service` om du lägger projektet på annan plats.  
2. Installera:
```bash
sudo cp pi-client/systemd/ai-voice-client.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ai-voice-client
```

---

## 2) Mini-backend (valfri) — Vector Stores / RAG
Backend låter kunden skapa ett Vector Store och ladda upp filer.

### Installera
```bash
python3 -m pip install -r backend-minimal/requirements.txt
cp backend-minimal/.env.example backend-minimal/.env
# EDITERA: OPENAI_API_KEY=...
```

### Starta
```bash
uvicorn backend-minimal.app:app --host 0.0.0.0 --port 8080 --reload
```

### Endpoints
- `POST /vector-stores` (form field `name`) → `{ id: "vs_..." }`
- `POST /vector-stores/{vs_id}/files` (multipart `file`) → associerar fil med vector store

> I din huvudapp kan du sedan anropa OpenAI **Responses API** med `file_search={"vector_store_ids":[vs_id]}` för att använda kundens dokument i svar.

---

## 3) Säkerhet (POC → Produktion)
- **POC:** Nyckel i `.env` på Pi/backenden.
- **Prod:** Dölj nyckel bakom din backend. Låt Pi använda **JWT/mTLS** mot backenden, och låt backenden prata med OpenAI.
- Lägg in rate limits, loggning och per-tenant-isolering för vector stores.

---

## 4) Tips
- Justera modellen via `MODEL` i `.env` (exempelvärde: `gpt-4o-realtime-preview`).
- Om du får ljudproblem: testa annan mik/högtalare, kontrollera `arecord -l`/`aplay -l`.

Lycka till! 🎙️
