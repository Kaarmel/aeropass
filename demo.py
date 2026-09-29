"""
AeroPass — demo całego przepływu jedną komendą:
alarm IMGW → „można latać” → propozycja lotu → zgoda operatora (w panelu) → autonomiczny zwiad
(najpierw odcinki rozstrzygające) → status wsi dla wozu ciężkiego i terenowego → meldunki →
sprawdzenie objazdów leśnych dla odciętych wsi → decyzje w panelu.

Prawdziwe: sieć dróg i wsie (OSM), progi alarmowe wodowskazów i wiatr (IMGW), logika planera i meldunków.
Symulowane: poziom wody ponad progiem, porywy wiatru, przelot drona, stan odcinków (scenariusz/prawda),
obrazy z drona (zastępcze zdjęcia z FloodNet, jeśli są wyniki modelu).

Uruchomienie z katalogu repo:
    python panel/serwer.py            # w osobnym terminalu, panel: http://localhost:8765/panel/
    python demo.py [--tempo 3] [--auto]
--tempo: ile minut symulacji na sekundę; --auto: start drona zatwierdzany automatycznie po 3 s.
"""
import argparse
import itertools
import json
import random
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "planer"))
import meldunek  # noqa: E402
import monte_carlo as mc  # noqa: E402
import scenariusz as sc  # noqa: E402
import siec  # noqa: E402

START = datetime.fromisoformat("2026-09-30T06:00:00+02:00")
ZIARNO = 38  # scenariusz demo: 8 wsi odciętych dla wozu ciężkiego, w tym Wetlina; 1 z objazdem leśnym
STAN = Path("stan")
NIEPRZEJEZDNE = meldunek.NIEPRZEJEZDNE


def zapisz(nazwa, obj):
    tmp = STAN / (nazwa + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    tmp.replace(STAN / nazwa)  # zapis atomowy: panel nigdy nie czyta połowy pliku


def alarm():
    hydro = {h["stacja"]: h for h in json.load(open("dane/imgw/hydro_podkarpackie.json", encoding="utf-8"))}
    k = hydro["Kalnica"]
    prog = int(k["stan_alarmowy"])
    return {"zrodlo": f"IMGW hydro {k['id_stacji']} ({k['stacja']}, rzeka {k['rzeka']})",
            "stan_cm": prog + 11, "prog_alarmowy_cm": prog, "prog_ostrzegawczy_cm": int(k["stan_ostrzegawczy"]),
            "stan_rzeczywisty_cm": int(k["stan_wody"]), "pomiar_rzeczywisty": k["stan_wody_data_pomiaru"],
            "zweryfikowany": True, "uwaga": "progi prawdziwe (IMGW), poziom wody symulowany"}


def mozna_latac(czas):
    syn = {s["stacja"]: s for s in json.load(open("dane/imgw/synop_podkarpackie.json", encoding="utf-8"))}
    w = float(syn["Lesko"]["predkosc_wiatru"])
    porywy = w + 3  # IMGW synop nie podaje porywów: wartość symulowana (docelowo czujnik na stacji)
    poziom = "zielone" if w <= 7 and porywy <= 10 else ("zolte" if w <= 9 and porywy <= 12 else "czerwone")
    return {"poziom": poziom, "wiatr_ms": w, "porywy_ms": porywy, "opad": False, "przestrzen": "ok",
            "powod": f"wiatr {w:g} m/s (IMGW Lesko, prawdziwy), porywy {porywy:g} m/s (symulowane), brak stref R",
            "czas": czas.isoformat(timespec="seconds")}


class Demo:
    def __init__(self, tempo, auto):
        self.tempo, self.auto = tempo, auto
        sc.zapisz(ZIARNO)  # statyczne stan/odcinki.json i stan/wsie.json
        self.sw = mc.Swiat()
        self.prawda = sc.losuj_prawde(self.sw.odc, random.Random(ZIARNO))
        self.statyczne = {o["id"]: o for o in json.load(open(STAN / "odcinki.json", encoding="utf-8"))}
        self.wsie = {w["id"]: w for w in json.load(open(STAN / "wsie.json", encoding="utf-8"))}
        self.stany = sc.stan_poczatkowy(self.sw.odc)  # wiedza systemu (wszystkie klasy, także leśne)
        self.dyn, self.meldunki, self.zdarzenia = {}, {}, []
        self.status = {w: {"ciezarowy": "nieznany", "terenowy": "nieznany"} for w in self.wsie}
        self.nr_mel, self.t0, self.ostatni_t = itertools.count(1), 0.0, 0.0
        wszystkie_przejezdne = {o["id"]: "przejezdny" for o in self.sw.odc if not o["lesny"]}
        self.normalnie = {w: siec.trasa(self.sw.G, self.sw.wz[w], wszystkie_przejezdne) or [] for w in self.wsie}
        obrazy = self._obrazy()
        self.obrazy = {k: itertools.cycle(v) if v else None for k, v in obrazy.items()}
        for f in ("meldunki.json", "zmiany.json", "loty.json", "zdarzenia.json"):
            zapisz(f, [] if f != "zmiany.json" else {})
        zapisz("decyzje.json", [])
        self.lot = {"id": "lot-001", "dron": "dok-" + siec._slug(self.sw.stacje[0][0]), "typ": "zwiad_drog",
                    "status": "propozycja", "symulowane": True}

    def _obrazy(self):
        p = Path("wyniki/predykcje_demo.json")
        if not p.exists():
            return {"zalany": [], "przejezdny": []}
        d = json.load(open(p, encoding="utf-8"))
        # tylko zdjęcia, na których model trafił (zastępcze ilustracje stanu symulowanego; metryka błędów jest osobno)
        return {"zalany": [x for x in d if x["prawda"] == "zalany" and x["stan"] == "zalany"],
                "przejezdny": [x for x in d if x["prawda"] == "przejezdny" and x["stan"] == "przejezdny"]}

    def zegar(self, t_min):
        return START + timedelta(minutes=self.t0 + t_min)

    def zdarzenie(self, t_min, typ, tekst):
        self.zdarzenia.append({"czas": self.zegar(t_min).isoformat(timespec="seconds"), "typ": typ, "tekst": tekst})
        zapisz("zdarzenia.json", self.zdarzenia[-60:])
        print(f"[{self.zegar(t_min):%H:%M}] {tekst}")

    def misja(self, t_min, etap, poz=None):
        ust = sum(s["ciezarowy"] != "nieznany" for s in self.status.values())
        km = sum(self.statyczne[o]["dlugosc_m"] for o, d in self.dyn.items()) / 1000
        zapisz("misja.json", {"czas": self.zegar(t_min).isoformat(timespec="seconds"), "minuta_lotu": round(t_min, 1),
                              "etap": etap, "dron": {"polozenie": list(poz) if poz else None, "lot": self.lot["id"]},
                              "stacje": [{"nazwa": n, "polozenie": list(p)} for n, p in self.sw.stacje],
                              "alarm": self.alarm, "mozna_latac": self.lot.get("mozna_latac"),
                              "postep": {"wsie_ustalone": ust, "wsie_razem": len(self.wsie), "km_sprawdzone": round(km, 1)},
                              "symulowane": True})

    def obserwuj(self, oid):
        s = self.prawda[oid]
        pula = self.obrazy.get("przejezdny" if s == "przejezdny" else "zalany")
        foto = next(pula) if pula else None
        self._foto = foto
        return s

    def widok(self, ids):
        return {o: {**self.statyczne[o], **self.dyn.get(o, {"stan": self.stany[o], "czas_obserwacji": None, "zrodlo": None})} for o in ids}

    def po_kroku(self, t_min, oid, poz, stany_ciez, st_ciez):
        teraz = self.zegar(t_min)
        s = self.stany[oid] = stany_ciez[oid]
        foto = getattr(self, "_foto", None)
        self.dyn[oid] = {"stan": s, "przejezdny_dla": ["osobowy", "ciezarowy", "terenowy"] if s == "przejezdny" else [],
                         "zweryfikowany": True, "pewnosc": 0.9, "czas_obserwacji": teraz.isoformat(timespec="seconds"),
                         "zrodlo": {"typ": "dron", "lot": self.lot["id"],
                                    "obraz": f"wyniki/{foto['plik']}" if foto else None,
                                    "model": {"stan": foto["stan"], "pewnosc": foto["pewnosc"]} if foto else None,
                                    "uwaga": "obraz zastępczy z FloodNet" if foto else "obserwacja symulowana"},
                         "symulowane": True}
        if s in NIEPRZEJEZDNE and not self.statyczne[oid]["lesny"]:
            self.zdarzenie(t_min, "odcinek", f"{self.statyczne[oid]['droga']} ({oid}): {meldunek.OPIS_STANU[s]}")
        self.odswiez(t_min, st_ciez)
        self.misja(t_min, "zwiad", poz)
        zapisz("zmiany.json", self.dyn)
        opoznienie = (t_min - self.ostatni_t) * 60 / (self.tempo * 60)
        self.ostatni_t = t_min
        time.sleep(min(opoznienie, 2.0))

    def odswiez(self, t_min, st_ciez=None):
        teraz = self.zegar(t_min)
        st_ciez = st_ciez or siec.status_wsi(self.sw.G, self.sw.wz, self.stany, "ciezarowy")
        st_ter = siec.status_wsi(self.sw.G, self.sw.wz, self.stany, "terenowy")
        for w in self.wsie:
            nowy = {"ciezarowy": st_ciez[w], "terenowy": st_ter[w]}
            if nowy == self.status[w]:
                continue
            self.status[w] = nowy
            wies = self.wsie[w]
            wies.update({"status": nowy["ciezarowy"], "status_pewnosc": 0.9 if nowy["ciezarowy"] != "nieznany" else 0.0,
                         "status_czas": teraz.isoformat(timespec="seconds"),
                         "dojazd": {"osobowy": nowy["ciezarowy"] == "dostepna", "ciezarowy": nowy["ciezarowy"] == "dostepna",
                                    "terenowy": nowy["terenowy"] == "dostepna"}, "symulowane": True})
            if nowy["ciezarowy"] == "nieznany" and nowy["terenowy"] == "nieznany":
                continue
            trasy = {k: siec.trasa(self.sw.G, self.sw.wz[w], self.stany, k) for k in ("ciezarowy", "terenowy")}
            przyczyny = [o for o in self.normalnie[w] if self.stany.get(o) in NIEPRZEJEZDNE]
            ids = przyczyny + (trasy["ciezarowy"] or []) + (trasy["terenowy"] or [])
            m = meldunek.zbuduj(wies, nowy, trasy, przyczyny, self.widok(ids), teraz, next(self.nr_mel))
            self.meldunki[w] = m
            self.zdarzenie(t_min, "meldunek", m["tekst"].split("\n")[0] + " — " + m["rekomendacja"]["dzialanie"][:90])
        zapisz("wsie.json", list(self.wsie.values()))
        zapisz("meldunki.json", sorted(self.meldunki.values(), key=lambda m: (m["priorytet"], -(self.wsie[m["wies"]].get("mieszkancy_rejestr") or 0))))

    def czekaj_na_zgode(self):
        self.lot["status"] = "propozycja"
        zapisz("loty.json", [self.lot])
        self.zdarzenie(0, "lot", "Propozycja lotu lot-001: zwiad dróg przy ciekach, najpierw odcinki rozstrzygające. Czeka na zgodę operatora.")
        self.misja(0, "czeka_na_zgode")
        t = time.time()
        while True:
            dec = [d for d in json.load(open(STAN / "decyzje.json", encoding="utf-8")) if d.get("dotyczy") == "lot-001"]
            if dec:
                break
            if self.auto and time.time() - t > 3:
                dec = [{"id": "dec-0001", "typ": "decyzja", "dotyczy": "lot-001", "czas": self.zegar(0).isoformat(timespec="seconds"),
                        "kto": "operator (demo, automatycznie)", "wynik": "zatwierdzona", "zmiana": None, "uwagi": "", "symulowane": True}]
                zapisz("decyzje.json", dec)
                break
            time.sleep(0.5)
        if dec[-1]["wynik"] != "zatwierdzona":
            self.zdarzenie(0, "lot", f"Lot odrzucony przez: {dec[-1]['kto']}. Koniec demo.")
            sys.exit(0)
        self.lot.update({"status": "w_locie", "zatwierdzil": {"kto": dec[-1]["kto"], "czas": dec[-1]["czas"]}})
        zapisz("loty.json", [self.lot])
        self.zdarzenie(0, "lot", f"Start zatwierdzony ({dec[-1]['kto']}). Dron startuje ze stacji {self.sw.stacje[0][0]}.")

    def objazdy_lesne(self, t_min, poz):
        """Dla wsi odciętych dla wozu ciężkiego: sprawdź najkrótszy możliwy objazd dla terenowego."""
        self.lot = {**self.lot, "id": "lot-002", "typ": "zwiad_drog", "status": "w_locie", "powod": "objazdy leśne do wsi odciętych"}
        zapisz("loty.json", [self.lot])
        for w in [w for w, s in self.status.items() if s["ciezarowy"] == "odcieta"]:
            for _ in range(20):
                if self.status[w]["terenowy"] != "nieznany":
                    break
                O = siec._podgraf(self.sw.G, self.stany, "terenowy", optymistyczny=True)
                try:
                    sciezka = siec.nx.shortest_path(O, siec.ZEW, self.sw.wz[w], weight="dl")
                except siec.nx.NetworkXNoPath:
                    break
                nieznane = [O[a][b]["id"] for a, b in zip(sciezka, sciezka[1:]) if self.stany.get(O[a][b]["id"]) == "nieznany"]
                if not nieznane:
                    break
                for oid in nieznane:
                    d_dolot, wyj = mc.dolot(self.sw, poz, oid)
                    t_min += (d_dolot + self.statyczne[oid]["dlugosc_m"]) / mc.V / 60
                    poz = wyj
                    stany = dict(self.stany)
                    stany[oid] = self.obserwuj(oid)
                    self.po_kroku(t_min, oid, poz, stany, None)
                    if stany[oid] in NIEPRZEJEZDNE:
                        break
        return t_min

    def uruchom(self):
        self.alarm = alarm()
        self.zdarzenie(0, "alarm", f"ALARM: {self.alarm['zrodlo']} — {self.alarm['stan_cm']} cm przy progu alarmowym {self.alarm['prog_alarmowy_cm']} cm (poziom symulowany). Zagrożenie zweryfikowane.")
        self.lot["mozna_latac"] = mozna_latac(self.zegar(0))
        self.zdarzenie(0, "pogoda", f"Można latać: {self.lot['mozna_latac']['poziom'].upper()} — {self.lot['mozna_latac']['powod']}")
        self.czekaj_na_zgode()
        krzywa, _ = mc.symuluj(self.sw, self.prawda, "B", obserwuj=self.obserwuj, po_kroku=self.po_kroku)
        t_min, poz = krzywa[-1][0], None
        poz = self.sw.doki[0]
        self.zdarzenie(t_min, "lot", "Zwiad dróg zakończony. Sprawdzam objazdy leśne dla wsi odciętych.")
        t_min = self.objazdy_lesne(t_min, poz)
        self.lot["status"] = "zakonczony"
        zapisz("loty.json", [self.lot])
        ciez = [s["ciezarowy"] for s in self.status.values()]
        self.zdarzenie(t_min, "koniec", f"Koniec misji po {t_min:.0f} min lotu: {ciez.count('dostepna')} wsi dostępnych, {ciez.count('odcieta')} odciętych dla wozu ciężkiego, {ciez.count('nieznany')} nieustalonych.")
        self.misja(t_min, "koniec", poz)
        # pełny plik w formacie FORMAT.md na koniec
        zapisz("odcinki.json", [{**o, **self.dyn.get(o["id"], {})} for o in self.statyczne.values()])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tempo", type=float, default=3.0, help="minuty symulacji na sekundę")
    ap.add_argument("--auto", action="store_true", help="start drona zatwierdzany automatycznie")
    a = ap.parse_args()
    Demo(a.tempo, a.auto).uruchom()
