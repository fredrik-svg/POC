# Pi WebRTC Client (optional)
Denna mapp är en **stub** för en framtida Pi-klient med **WebRTC** (lägre latens) via Node.js.
För POC rekommenderas WebSocket-klienten i `pi-client/`.

Plan:
- Använd `wrtc`-paketet för PeerConnection på Node
- Skicka local audio (arecord) → Opus → Realtime API SDP/ICE
- Spela upp remote audio (speaker)
