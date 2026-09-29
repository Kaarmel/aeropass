# AeroPass

> *(Jedno zdanie, do uzupełnienia.)* Propozycja: Sztab powiatowy podczas powodzi musi zdecydować, do której odciętej wsi wysłać pomoc najpierw. AeroPass: dron sam sprawdza drogi, od których zależy dojazd do wsi, i zbiera od mieszkańców zgłoszenia przez Wi-Fi, bez sieci komórkowej.

*(Tu wstawić GIF z demo.)*

Projekt na Dual Use Hackathon 2026 (Carpathian Drone Summit, Jasionka).

## Co jest prawdziwe, co symulowane, co jest koncepcją

| Element | Status |
|---|---|
| Progi alarmowe wodowskazów IMGW (Cisna, Terka, Kalnica) | **prawdziwe** (API IMGW, `dane/imgw/`) |
| Poziom wody w scenariuszu powodzi | symulowane |
| Sieć dróg, mosty, wsie doliny Solinki i Wetlinki | **prawdziwe** (OpenStreetMap, `dane/osm/`) |
| Wybór odcinków krytycznych i plan lotu | **prawdziwy kod** na prawdziwym grafie |
| Przelot drona i obrazy z przelotu | symulowane (obrazy zastępcze z FloodNet) |
| Segmentacja zalanych dróg | *(do uzupełnienia: model i metryka na zbiorze testowym FloodNet)* |
| Portal Wi-Fi ze zgłoszeniami | *(do uzupełnienia)* |
| Panel sztabu, meldunek, zatwierdzanie, dziennik decyzji | *(do uzupełnienia)* |
| Stacja dokująca, loty poza zasięgiem wzroku, latający BTS operatora | koncepcja |

## Jak uruchomić

*(Do uzupełnienia: jedna komenda, np. `python demo.py`.)*

Prototyp planera:

```bash
python3 -m venv ~/.venvs/skyroad && source ~/.venvs/skyroad/bin/activate
pip install networkx
python planer/krytyczne_odcinki.py
```

## Wyniki

*(Do uzupełnienia: metryka FloodNet, wykres porównania strategii lotu, zmierzony zasięg Wi-Fi.)*

## Format danych

Patrz [FORMAT.md](FORMAT.md).

## Użycie AI i zasobów zewnętrznych

Wymóg regulaminu (IX). Uzupełniać na bieżąco:

- **Narzędzia AI:** Claude (Anthropic): analiza zadania, koncepcja, dokumentacja, *(części kodu — uzupełnić, które)*.
- **Biblioteki:** networkx (BSD-3-Clause) *(dopisywać kolejne)*.
- **Dane:**
  - IMGW-PIB, dane publiczne, © Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy *(dokładną formułę źródła sprawdzić w warunkach IMGW)*.
  - OpenStreetMap: © OpenStreetMap contributors, licencja ODbL 1.0.
  - FloodNet: CDLA-Permissive 1.0. Rahnemoonfar i in., „FloodNet: A High Resolution Aerial Imagery Dataset for Post Flood Scene Understanding”, IEEE Access 9, 2021, doi:10.1109/ACCESS.2021.3090981.

## Zespół

*(Do uzupełnienia.)*

## Licencja

Kod: **AGPL-3.0** (patrz [LICENSE](LICENSE)), bo model korzysta z Ultralytics YOLO (AGPL-3.0). Dane zewnętrzne pozostają na swoich licencjach (wyżej).
