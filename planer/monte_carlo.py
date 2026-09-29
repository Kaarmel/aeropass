"""
Dowód na autonomię: porównanie strategii lotu w wielu losowych scenariuszach powodzi (Monte Carlo).

- Strategia A „przegląd wszystkiego”: dron przelatuje wszystkie utwardzone odcinki przy ciekach,
  zawsze do najbliższego jeszcze niesprawdzonego (bez korzystania z tego, co już wie).
- Strategia B „AeroPass”: po każdej obserwacji wybiera odcinek, który najbardziej przybliża
  ustalenie statusu wsi: liczba wsi o nieznanym statusie, na których najkrótszej możliwej trasie
  leży ten odcinek, podzielona przez koszt dolotu i przelotu.

Miara: % wsi, których status ze statusu „nieznany” stał się pewny („dostepna” albo „odcieta”)
w funkcji minut lotu, dla wozu ciężarowego PSP (drogi leśne pominięte).

Model lotu (założenia, do skalibrowania testem): platforma klasy DJI Matrice 30 bez dodatkowego
ładunku (41 min w laboratorium), liczymy ostrożnie 22 min użytecznych na baterię przy 12 m/s,
3 min wymiany baterii, lądowanie w najbliższej stacji dokującej. Stacje dobiera algorytm
(zachłanne pokrycie ≥99% km dróg przy ciekach; kandydaci: miejscowości doliny jako przybliżenie
lokalizacji remiz OSP). Jeden dron; obserwacja bezbłędna (błąd modelu AI raportowany osobno).

Uruchomienie z katalogu repo: python planer/monte_carlo.py [liczba_scenariuszy]
"""
import json
import random
import sys
from pathlib import Path

import networkx as nx

import scenariusz as sc
import siec

V = 12.0             # m/s, prędkość przelotowa (nie limit wiatru)
BUDZET_S = 22 * 60   # użyteczny czas na baterię (z rezerwą ok. 25–30%)
WYMIANA_S = 3 * 60   # wymiana baterii w stacji (założenie)
POKRYCIE_MIN = 0.99  # stacje dobieramy, aż pokryją ≥99% km dróg przy ciekach


class Swiat:
    def __init__(self):
        self.odc, self.wsie, self.G, self.wz = sc.wczytaj()
        self.po_id = {o["id"]: o for o in self.odc}
        self.utw = [(u, v, k, d["dl"]) for u, v, k, d in self.G.edges(keys=True, data=True) if not d["lesny"]]
        self.zagrozone = [o["id"] for o in self.odc if sc.zagrozony(o) and not o["lesny"]]
        self.stacje = self.rozmiesc_stacje()
        self.doki = [p for _, p in self.stacje]

    def rozmiesc_stacje(self):
        """Zachłanne pokrycie: dokładamy miejscowość, z której w jednym locie tam i z powrotem da się
        sprawdzić najwięcej jeszcze niepokrytych km dróg przy ciekach."""
        def pokrycie(d):
            out = set()
            for o in self.zagrozone:
                a, b = self.konce(o)
                if min(siec.hav(d, a) + siec.hav(b, d), siec.hav(d, b) + siec.hav(a, d)) + self.po_id[o]["dlugosc_m"] <= BUDZET_S * V:
                    out.add(o)
            return out
        km = lambda s: sum(self.po_id[o]["dlugosc_m"] for o in s)
        pok = {w["nazwa"]: (tuple(w["polozenie"]), pokrycie(tuple(w["polozenie"]))) for w in self.wsie}
        wszystko, wybrane, pokryte = km(self.zagrozone), [], set()
        while km(pokryte) < POKRYCIE_MIN * wszystko:
            n = max(pok, key=lambda n: km(pok[n][1] - pokryte))
            if not pok[n][1] - pokryte:
                break
            wybrane.append((n, pok[n][0]))
            pokryte |= pok[n][1]
        self.pokrycie_km = (round(km(pokryte) / 1000, 1), round(wszystko / 1000, 1))
        return wybrane

    def graf(self, stany, optymistyczny):
        ok = ("przejezdny", "nieznany") if optymistyczny else ("przejezdny",)
        H = nx.Graph()
        H.add_node(siec.ZEW)
        for u, v, k, dl in self.utw:
            if k.startswith("ZEW") or stany[k] in ok:
                if not H.has_edge(u, v) or H[u][v]["dl"] > dl:
                    H.add_edge(u, v, dl=dl, id=k)
        return H

    def status(self, stany):
        cp = nx.node_connected_component(self.graf(stany, False), siec.ZEW)
        co = nx.node_connected_component(self.graf(stany, True), siec.ZEW)
        return {w: "dostepna" if n in cp else ("odcieta" if n not in co else "nieznany") for w, n in self.wz.items()}

    def konce(self, oid):
        g = self.po_id[oid]["geometria"]
        return tuple(g[0]), tuple(g[-1])


def dolot(swiat, poz, oid):
    a, b = swiat.konce(oid)
    da, db = siec.hav(poz, a), siec.hav(poz, b)
    return (da, b) if da <= db else (db, a)  # (odległość dolotu, punkt wyjścia po przelocie)


def symuluj(swiat, prawda, strategia, obserwuj=None, po_kroku=None):
    """obserwuj(oid) -> stan (domyślnie prawda); po_kroku(t_min, oid, poz, stany, status) — do demo."""
    stany = sc.stan_poczatkowy(swiat.odc)
    st = swiat.status(stany)
    nieznane0 = [w for w, s in st.items() if s == "nieznany"]
    if not nieznane0:
        return [(0.0, 1.0)], 0
    t, poz, bateria = 0.0, swiat.doki[0], BUDZET_S  # start z pierwszej (najlepiej pokrywającej) stacji
    krzywa = [(0.0, 0.0)]
    do_sprawdzenia = set(swiat.zagrozone)
    niewidoczne = set()  # poza zasięgiem stacji: zostają nieznane
    while do_sprawdzenia:
        oid = None
        if strategia == "B":
            # trasy planujemy z pominięciem odcinków, których dron i tak nie sprawdzi
            O = swiat.graf({**stany, **{k: "zablokowany" for k in niewidoczne}}, True)
            odl, sciezki = nx.single_source_dijkstra(O, siec.ZEW, weight="dl")
            licznik = {}
            for w in (w for w, s in st.items() if s == "nieznany"):
                sc_ = sciezki.get(swiat.wz[w])
                if not sc_:  # osiągalna tylko przez odcinki poza zasięgiem stacji
                    continue
                for a, b in zip(sc_, sc_[1:]):
                    k = O[a][b]["id"]
                    if stany.get(k) == "nieznany" and k in do_sprawdzenia:
                        licznik[k] = licznik.get(k, 0) + 1
            if licznik:
                oid = max(licznik, key=lambda o: licznik[o] / (dolot(swiat, poz, o)[0] + swiat.po_id[o]["dlugosc_m"] + 1))
        if oid is None:  # A zawsze; B, gdy nic już nie rozstrzyga: najbliższy niesprawdzony
            oid = min(do_sprawdzenia, key=lambda o: dolot(swiat, poz, o)[0])
        d_dolot, wyjscie = dolot(swiat, poz, oid)
        przelot = (d_dolot + swiat.po_id[oid]["dlugosc_m"]) / V
        powrot = min(siec.hav(wyjscie, dk) for dk in swiat.doki) / V
        if przelot + powrot > bateria:
            # wróć do najbliższej stacji, wymień baterię; jeśli stamtąd odcinek jest za daleko,
            # przeleć do stacji, z której go sięgniesz (kolejna wymiana baterii)
            dk = min(swiat.doki, key=lambda d: siec.hav(poz, d))
            t += siec.hav(poz, dk) / V + WYMIANA_S
            poz, bateria = dk, BUDZET_S

            def koszt_z(d):
                dd, wy = dolot(swiat, d, oid)
                return (dd + swiat.po_id[oid]["dlugosc_m"]) / V + min(siec.hav(wy, d2) for d2 in swiat.doki) / V

            osiagalne = [d for d in swiat.doki if koszt_z(d) <= BUDZET_S]
            if not osiagalne:  # poza zasięgiem całej sieci stacji
                do_sprawdzenia.discard(oid)
                niewidoczne.add(oid)
                continue
            if koszt_z(poz) > BUDZET_S:
                cel = min(osiagalne, key=lambda d: siec.hav(poz, d))
                t += siec.hav(poz, cel) / V + WYMIANA_S
                poz = cel
            d_dolot, wyjscie = dolot(swiat, poz, oid)
            przelot = (d_dolot + swiat.po_id[oid]["dlugosc_m"]) / V
        t += przelot
        bateria -= przelot
        poz = wyjscie
        stany[oid] = obserwuj(oid) if obserwuj else prawda[oid]
        do_sprawdzenia.discard(oid)
        st = swiat.status(stany)
        znane = sum(st[w] != "nieznany" for w in nieznane0) / len(nieznane0)
        krzywa.append((t / 60, znane))
        if po_kroku:
            po_kroku(t / 60, oid, poz, stany, st)
        if znane == 1.0:
            break
    return krzywa, len(nieznane0)


def na_siatke(krzywa, minuty):
    wynik, i = [], 0
    for m in minuty:
        while i + 1 < len(krzywa) and krzywa[i + 1][0] <= m:
            i += 1
        wynik.append(krzywa[i][1])
    return wynik


def main(n):
    swiat = Swiat()
    minuty = list(range(0, 481, 5))
    wyniki = {"A": [], "B": []}
    czasy = {"A": {"90": [], "100": []}, "B": {"90": [], "100": []}}
    for s in range(n):
        prawda = sc.losuj_prawde(swiat.odc, random.Random(1000 + s))
        for strat in ("A", "B"):
            krzywa, _ = symuluj(swiat, prawda, strat)
            wyniki[strat].append(na_siatke(krzywa, minuty))
            for prog in ("90", "100"):
                t = next((m for m, f in krzywa if f >= int(prog) / 100), None)
                czasy[strat][prog].append(t)
        print(f"scenariusz {s + 1}/{n}", end="\r", flush=True)

    def med(xs):
        xs = sorted(x if x is not None else float("inf") for x in xs)
        m = xs[len(xs) // 2]
        return None if m == float("inf") else round(m)

    podsum = {
        "liczba_scenariuszy": n,
        "zalozenia": {"predkosc_ms": V, "uzyteczne_min": BUDZET_S / 60, "wymiana_min": WYMIANA_S / 60,
                      "stacje": [n for n, _ in swiat.stacje], "pokrycie_km": swiat.pokrycie_km, "klasa_pojazdu": "ciezarowy",
                      "P_ZERWANY_MOST": sc.P_ZERWANY_MOST, "P_ZALANY_PRZY_POTOKU": sc.P_ZALANY_PRZY_POTOKU,
                      "obserwacja": "bezbłędna (błąd modelu AI raportowany osobno)"},
        "odcinki_przy_ciekach": len(swiat.zagrozone),
        "km_przy_ciekach": round(sum(swiat.po_id[o]["dlugosc_m"] for o in swiat.zagrozone) / 1000, 1),
        "mediana_min_do_90proc": {k: med(v["90"]) for k, v in czasy.items()},
        "mediana_min_do_100proc": {k: med(v["100"]) for k, v in czasy.items()},
        "symulowane": True,
    }
    Path("wyniki").mkdir(exist_ok=True)
    json.dump(podsum, open("wyniki/monte_carlo.json", "w"), ensure_ascii=False, indent=2)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
    for strat, kolor, etykieta in (("B", "#1f6feb", "AeroPass: najpierw odcinki rozstrzygające"),
                                   ("A", "#9a9a9a", "Przegląd wszystkich dróg przy ciekach")):
        kol = list(zip(*wyniki[strat]))
        sr = [100 * sum(c) / len(c) for c in kol]
        p10 = [100 * sorted(c)[int(0.1 * (len(c) - 1))] for c in kol]
        p90 = [100 * sorted(c)[int(0.9 * (len(c) - 1))] for c in kol]
        ax.fill_between(minuty, p10, p90, color=kolor, alpha=0.15, linewidth=0)
        ax.plot(minuty, sr, color=kolor, linewidth=2.2, label=etykieta)
    ax.set_xlabel(f"Minuty lotu (1 dron, {len(swiat.stacje)} stacje dokujące, wymiany baterii wliczone)")
    ax.set_ylabel("% wsi z ustalonym dojazdem")
    ax.set_ylim(0, 101)
    ax.set_xlim(0, minuty[-1])
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right", frameon=False)
    ax.set_title(f"Dolina Solinki i Wetlinki: {n} symulowanych powodzi (średnia, pas 10–90%)", fontsize=10)
    fig.tight_layout()
    fig.savefig("wyniki/monte_carlo.png")
    print("\n" + json.dumps(podsum, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 40)
