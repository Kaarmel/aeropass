"""
Serwer panelu AeroPass (tylko biblioteka standardowa, działa bez internetu).
Serwuje katalog repo (panel/, stan/, wyniki/) i przyjmuje decyzje: POST /api/decyzja → dopisanie do stan/decyzje.json.

Uruchomienie z katalogu repo: python panel/serwer.py   →   http://localhost:8765/panel/
"""
import json
import threading
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

KATALOG = Path(__file__).resolve().parent.parent
DECYZJE = KATALOG / "stan" / "decyzje.json"
TYPY = {"decyzja": {"zatwierdzona", "odrzucona", "zmieniona"},
        "potwierdzenie_wykonania": {"zadysponowano", "w_drodze", "dotarlo", "niewykonane"}}
blokada = threading.Lock()


class Obsluga(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(KATALOG), **k)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):  # cisza w terminalu (panel odpytuje co 1,5 s)
        pass

    def do_POST(self):
        if self.path != "/api/decyzja":
            return self.send_error(404)
        try:
            d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            typ, wynik = d.get("typ", "decyzja"), d.get("wynik")
            if typ not in TYPY or wynik not in TYPY[typ] or not str(d.get("dotyczy", "")).startswith(("mel-", "lot-", "dec-")):
                raise ValueError("niepoprawna decyzja")
            with blokada:
                log = json.loads(DECYZJE.read_text(encoding="utf-8")) if DECYZJE.exists() else []
                try:  # czas z zegara misji (demo), a jeśli go brak, czas rzeczywisty
                    czas = json.loads((KATALOG / "stan" / "misja.json").read_text(encoding="utf-8"))["czas"]
                except Exception:
                    czas = datetime.now().astimezone().isoformat(timespec="seconds")
                wpis = {"id": f"dec-{len(log) + 1:04d}", "typ": typ, "dotyczy": d["dotyczy"], "czas": czas,
                        "kto": str(d.get("kto") or "dyżurny (demo)")[:80], "wynik": wynik,
                        "zmiana": (str(d["zmiana"])[:300] if d.get("zmiana") else None),
                        "uwagi": str(d.get("uwagi") or "")[:300], "symulowane": True}
                log.append(wpis)  # dziennik: tylko dopisujemy
                tmp = DECYZJE.with_suffix(".tmp")
                tmp.write_text(json.dumps(log, ensure_ascii=False), encoding="utf-8")
                tmp.replace(DECYZJE)
            body, kod = json.dumps(wpis, ensure_ascii=False).encode(), 200
        except Exception as e:
            body, kod = json.dumps({"blad": str(e)}, ensure_ascii=False).encode(), 400
        self.send_response(kod)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print("Panel AeroPass: http://localhost:8765/panel/  (Ctrl+C kończy)")
    ThreadingHTTPServer(("127.0.0.1", 8765), Obsluga).serve_forever()
