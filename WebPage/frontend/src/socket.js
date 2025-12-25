const WS_URL = "ws://127.0.0.1:8000/ws";

export function getSocket() {
  return new WebSocket(WS_URL);
}
