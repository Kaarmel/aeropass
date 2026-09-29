"""
Serwer panelu AeroPass (tylko biblioteka standardowa, działa bez internetu).
Serwuje katalog repo (panel/, stan/, wyniki/) i przyjmuje decyzje: POST /api/decyzja → dopisanie do stan/decyzje.json.
Przyciski symulacji: POST /api/sterowanie {akcja: start|reset|pauza|wznow|tempo} uruchamia demo.py jako proces potomny.

Uruchomienie z katalogu repo: python panel/serwer.py   →   http://localhost:8765/panel/
"""
import json
import subprocess
import sys
import threading
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

KATALOG = Path(__file__).resolve().parent.parent
DECYZJE = KATALOG / "stan" / "decyzje.json"
TYPY = {"decyzja": {"zatwierdzona", "odrzucona", "zmieniona"},
        "potwierdzenie_wykonania": {"zadysponowano", "w_drodze", "dotarlo", "niewykonane"}}
blokada = threading.Lock()
demo = {"proc": None, "ziarno": 56, "strategia": "B", "przygotuj": False}


def uruchom_demo(ziarno, strategia, tempo, reczne, przygotuj):
    """Jeden proces demo naraz: nowy start lub reset kończy poprzedni."""
    zatrzymaj_demo()
    cmd = [sys.executable, "demo.py", "--ziarno", str(ziarno), "--strategia", strategia, "--tempo", str(tempo),
           "--reczne", json.dumps(reczne)] + (["--przygotuj"] if przygotuj else [])
    log = open(KATALOG / "stan" / "demo.log", "w")
    demo.update(proc=subprocess.Popen(cmd, cwd=KATALOG, stdout=log, stderr=subprocess.STDOUT),
                ziarno=ziarno, strategia=strategia, przygotuj=przygotuj)


def zatrzymaj_demo():
    p = demo["proc"]
    if p and p.poll() is None:
        p.terminate()
        try:
            p.wait(timeout=3)
        except subprocess.TimeoutExpired:
            p.kill()


def sterowanie():
    try:
        s = json.loads((KATALOG / "stan" / "sterowanie.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        s = {}
    p = demo["proc"]
    out = {"dziala": bool(p and p.poll() is None and not demo["przygotuj"]), "ziarno": demo["ziarno"],
           "strategia": demo["strategia"], "pauza": bool(s.get("pauza")), "tempo": s.get("tempo", 3)}
    if p and p.poll() not in (None, 0):  # np. brak networkx w środowisku, z którego uruchomiono serwer
        out["blad"] = (KATALOG / "stan" / "demo.log").read_text(encoding="utf-8", errors="replace")[-400:]
    return out


class Obsluga(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(KATALOG), **k)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):  # cisza w terminalu (panel odpytuje co 1,5 s)
        pass

    def odpowiedz(self, obj, kod=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(kod)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] == "/api/sterowanie":
            return self.odpowiedz(sterowanie())
        super().do_GET()

    def steruj(self):
        try:
            d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            akcja = d.get("akcja")
            if akcja in ("start", "reset"):
                ziarno, strategia = int(d.get("ziarno", 56)), d.get("strategia", "B")
                tempo = min(max(float(d.get("tempo", 3)), 0.1), 120)
                reczne = {str(k): str(v) for k, v in (d.get("reczne") or {}).items()}
                if strategia not in ("A", "B") or not 0 <= ziarno < 10**6:
                    raise ValueError("niepoprawny scenariusz")
                uruchom_demo(ziarno, strategia, tempo, reczne, przygotuj=akcja == "reset")
            elif akcja in ("pauza", "wznow", "tempo"):
                s = sterowanie()
                plik = KATALOG / "stan" / "sterowanie.json"
                tmp = plik.with_suffix(".tmp")
                tmp.write_text(json.dumps({"pauza": akcja == "pauza" or (akcja == "tempo" and s["pauza"]),
                                           "tempo": min(max(float(d.get("tempo", s["tempo"])), 0.1), 120)}), encoding="utf-8")
                tmp.replace(plik)
            else:
                raise ValueError("nieznana akcja")
            self.odpowiedz(sterowanie())
        except Exception as e:
            self.odpowiedz({"blad": str(e)}, 400)

    def do_POST(self):
        if self.path == "/api/sterowanie":
            return self.steruj()
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
    (KATALOG / "stan").mkdir(exist_ok=True)
    if not (KATALOG / "stan" / "misja.json").exists():
        uruchom_demo(56, "B", 3, {}, przygotuj=True)  # pierwszy start: pusta mapa scenariusza z prezentacji
    try:
        ThreadingHTTPServer(("127.0.0.1", 8765), Obsluga).serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        zatrzymaj_demo()
