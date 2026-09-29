"""Uruchom: python testy/test_operator.py."""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ai.kamera import zapisz_kandydata, zatwierdz


with TemporaryDirectory() as tmp:
    katalog = Path(tmp)
    wynik = {"stan": "zalany", "wyniki": [{"typ": "zalany", "score": 0.8}, {"typ": "suchy", "score": 0.2}]}
    kandydat = zapisz_kandydata(Image.new("RGB", (16, 16)), wynik, katalog)
    assert not (katalog / "obserwacje_operatora.json").exists()
    dane = {"id": kandydat["id"], "typ": "drzewa", "liczba": 4, "lat": 49.21, "lon": 22.4,
            "operator": "OP-1", "zrodlo": "własne zdjęcie", "material": "demo"}
    try:
        zatwierdz({**dane, "lat": 190}, katalog)
        assert False, "niepoprawny GPS został zaakceptowany"
    except ValueError:
        pass
    wpis = zatwierdz(dane, katalog)
    assert wpis["typ"] == "drzewa" and wpis["liczba"] == 4
    assert wpis["sugestia"] == "zalany" and wpis["gps"] == [49.21, 22.4]
    assert (katalog / "obserwacje_operatora.json").exists()
    try:
        zatwierdz(dane, katalog)
        assert False, "zatwierdzono obserwację drugi raz"
    except ValueError:
        pass
print("OK: propozycja modelu wymaga decyzji operatora i poprawnego GPS")
