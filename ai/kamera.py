"""Lokalne porównanie scen z kamerki modelem CLIP: python ai/kamera.py."""

from io import BytesIO
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import torch
from PIL import Image, UnidentifiedImageError
from transformers import pipeline


HTML = Path(__file__).with_suffix(".html")
MODEL = "openai/clip-vit-base-patch32"
REVISION = "3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268"
OPISY = {
    "zalany": "a photo of a street flooded with water",
    "suchy": "a photo of a dry street with no flooding",
    "rzeka": "a photo of a river or lake",
    "wnetrze": "an indoor photo",
}


def decyzja(wyniki):
    """Wybór najbliższego opisu; pozostałe sceny są poza zakresem pokazu."""
    najlepszy = max(wyniki, key=lambda w: w["score"])["label"]
    return {OPISY["zalany"]: "zalany", OPISY["suchy"]: "suchy"}.get(najlepszy, "nieznany")


def analizuj(model, obraz):
    wyniki = model(obraz, candidate_labels=list(OPISY.values()))
    typy = {opis: typ for typ, opis in OPISY.items()}
    return {"stan": decyzja(wyniki),
            "wyniki": [{"typ": typy[w["label"]], "score": round(w["score"], 3)} for w in wyniki]}


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
            with Image.open(BytesIO(self.rfile.read(rozmiar))) as plik:
                if max(plik.size) > 2048:
                    raise ValueError("obraz większy niż 2048 px")
                obraz = plik.convert("RGB")
        except (ValueError, UnidentifiedImageError, OSError) as e:
            self.odpowiedz(400, {"blad": str(e)})
            return
        try:
            self.odpowiedz(200, analizuj(self.model, obraz))
        except Exception as e:
            self.odpowiedz(500, {"blad": f"błąd modelu: {e}"})


if __name__ == "__main__":
    urzadzenie = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Ładuję CLIP na {urzadzenie} (przy pierwszym uruchomieniu pobiera wagi)…", flush=True)
    Obsluga.model = pipeline("zero-shot-image-classification", model=MODEL, revision=REVISION, device=urzadzenie)
    print("AeroPass kamera: http://localhost:8767/  (Ctrl+C kończy)", flush=True)
    HTTPServer(("127.0.0.1", 8767), Obsluga).serve_forever()
