#!/usr/bin/env python3
"""
Raspberry Pi 5 → OpenAI Realtime (WebSocket) POC
- Spelar in mikrofon (16 kHz mono), skickar PCM som base64 till Realtime
- Tryck Enter för att avsluta ett yttrande och få svar (audio)
- Spelar upp svaret lokalt via 'sox'

Krav:
  sudo apt-get install -y sox portaudio19-dev
  pip install -r pi-client/requirements.txt
Miljö:
  cp pi-client/.env.example pi-client/.env  (fyll i OPENAI_API_KEY)
"""

import os, asyncio, base64, json, numpy as np, sounddevice as sd, subprocess, tempfile, sys
from websockets import connect
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
MODEL  = os.getenv("MODEL", "gpt-4o-realtime-preview").strip()
if not API_KEY:
    print("❌ OPENAI_API_KEY saknas i pi-client/.env")
    sys.exit(1)

WS_URL  = f"wss://api.openai.com/v1/realtime?model={MODEL}"
RATE = 16000
CHUNK = 1024  # frames per callback

def play_raw_pcm(raw_bytes: bytes, rate: int = RATE):
    """Spela upp 16-bit signed PCM mono via sox."""
    with tempfile.NamedTemporaryFile(suffix=".raw") as f:
        f.write(raw_bytes); f.flush()
        try:
            subprocess.run([
                "sox", "-t", "raw", "-b", "16", "-e", "signed-integer",
                "-r", str(rate), "-c", "1", f.name, "-d"
            ], check=True)
        except FileNotFoundError:
            print("⚠️  sox saknas. Installera: sudo apt-get install -y sox")

async def run_realtime():
    print("🔌 Ansluter till OpenAI Realtime ...")
    async with connect(
        WS_URL,
        extra_headers={
            "Authorization": f"Bearer {API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        },
        max_size=10*1024*1024  # ta höjd för audioströmmar
    ) as ws:
        # Initiera session med svenska instruktioner
        await ws.send(json.dumps({
            "type": "response.create",
            "response": {
                "modalities": ["audio"],
                "instructions": "Du är en svensk röstassistent. Svara kort, tydligt och på svenska."
            }
        }))

        loop = asyncio.get_running_loop()
        audio_out = bytearray()

        def callback(indata, frames, time, status):
            if status:
                # Du kan logga status här vid behov
                pass
            pcm16 = (indata[:, 0] * 32767).astype(np.int16).tobytes()
            b64 = base64.b64encode(pcm16).decode("ascii")
            pkt = {"type": "input_audio_buffer.append", "audio": b64}
            # Skicka till ws från PortAudio-tråd
            asyncio.run_coroutine_threadsafe(ws.send(json.dumps(pkt)), loop)

        with sd.InputStream(samplerate=RATE, channels=1, callback=callback, dtype='float32'):
            print("🎙  Tala när du vill. Tryck Enter för att få svar...")
            input()
            # Stäng bufferten för detta yttrande
            await ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
            await ws.send(json.dumps({"type": "response.create"}))

            # Ta emot audiodelar och spela upp när svaret är klart
            while True:
                raw = await ws.recv()
                try:
                    msg = json.loads(raw)
                except Exception:
                    # Hoppa över icke-JSON (om förekommer)
                    continue
                t = msg.get("type", "")
                if t == "output_audio.delta":
                    audio_out.extend(base64.b64decode(msg["audio"]))
                elif t == "output_audio.done":
                    print("🔊 Spelar upp svar ...")
                    play_raw_pcm(audio_out)
                    audio_out = bytearray()
                    print("✅ Klart. Tryck Enter för ny tur, Ctrl+C för att avsluta.")
                    input()
                    await ws.send(json.dumps({"type":"input_audio_buffer.reset"}))

if __name__ == "__main__":
    try:
        asyncio.run(run_realtime())
    except KeyboardInterrupt:
        print("\n👋 Avslutar.")
