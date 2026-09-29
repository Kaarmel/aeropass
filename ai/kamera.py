"""Lokalne demo modelu na klatkach z kamery: python ai/kamera.py."""

import base64
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "wyniki" / "best.pt"
HTML = Path(__file__).with_suffix(".html")


def decyzja(wykrycia):
    """Progi z sekcji 7 notatnika treningowego; brak wykrycia = nieznany."""
    if any(d["name"] == "flooded_road" and d["conf"] >= 0.4 for d in wykrycia):
        return "zalany"
    if any(d["name"] == "road_non_flooded" and d["conf"] >= 0.5 for d in wykrycia):
        return "przejezdny"
    return "nieznany"


def analizuj(model, klatka):
    wynik = model.predict(klatka, imgsz=640, conf=0.25, verbose=False)[0]
    wykrycia = [{"name": model.names[int(c)], "conf": round(float(p), 3)}
                for c, p in zip(wynik.boxes.cls, wynik.boxes.conf)]
    ok, obraz = cv2.imencode(".jpg", wynik.plot())
    if not ok:
        raise ValueError("nie można zakodować wyniku")
    return {"stan": decyzja(wykrycia), "wykrycia": wykrycia,
            "obraz": base64.b64encode(obraz).decode("ascii")}


class Obsluga(BaseHTTPRequestHandler):
    model = None

    def log_message(self, *args):
        pass

    def odpowiedz(self, kod, dane):
        body = json.dumps(dane, ensure_ascii=False).encode("utf-8")
        self.send_response(kod)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/":
            return self.send_error(404)
        body = HTML.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/analiza":
            return self.send_error(404)
        try:
            rozmiar = int(self.headers.get("Content-Length", "0"))
            if self.headers.get("Content-Type") != "image/jpeg" or not 0 < rozmiar <= 5_000_000:
                raise ValueError("wyślij klatkę JPEG do 5 MB")
            klatka = cv2.imdecode(np.frombuffer(self.rfile.read(rozmiar), dtype=np.uint8), cv2.IMREAD_COLOR)
            if klatka is None or max(klatka.shape[:2]) > 2048:
                raise ValueError("niepoprawna klatka lub obraz większy niż 2048 px")
            self.odpowiedz(200, analizuj(self.model, klatka))
        except (ValueError, cv2.error) as e:
            self.odpowiedz(400, {"blad": str(e)})
        except Exception as e:
            self.odpowiedz(500, {"blad": f"błąd modelu: {e}"})


if __name__ == "__main__":
    if not MODEL.exists():
        raise SystemExit(f"Brak modelu: {MODEL}")
    Obsluga.model = YOLO(str(MODEL))
    print("AeroPass kamera: http://localhost:8767/  (Ctrl+C kończy)", flush=True)
    HTTPServer(("127.0.0.1", 8767), Obsluga).serve_forever()
