# AeroPass — plan prezentacji dla jury

**Format:** 9 slajdów, 5:00 prezentacji, 2:00 pytań. Deck: `AeroPass_pitch.pptx` (edytowalny) i `AeroPass_pitch.pdf` (wersja do pokazania). Układ nawiązuje do `skypass.pdf`: 16:9, białe tło, granatowy tekst, duże światło między blokami i niewiele tekstu. Wzór był pustym szablonem Pitch ze starą nazwą SkyPass, więc zachowaliśmy jego prostotę, lecz napisaliśmy treść od nowa.

## Jedno zdanie, które ma zostać w pamięci

**AeroPass zamienia zdjęcie z drona obsługiwanego przez człowieka w potwierdzony punkt na mapie sztabu.** Model pomaga opisać obraz, operator weryfikuje, sztab otrzymuje źródło i GPS. Dronem nadal steruje operator. Obecny kod jest lokalnym prototypem, który wymaga pilotażu na polskich materiałach.

## Przebieg co do sekundy

| Slajd | Czas | Co pokazujesz | Główna myśl |
|---|---:|---|---|
| 1. AeroPass | 0:00–0:20 | nazwa i zdjęcie lotnicze | zdjęcie staje się czytelną obserwacją |
| 2. Problem | 0:20–0:50 | obraz i trzy pytania | sam plik nie wystarcza sztabowi |
| 3. Przepływ | 0:50–1:25 | cztery kroki | używamy istniejącego DJI i laptopa |
| 4. Operator | 1:25–2:05 | **film 18 s** | model sugeruje, człowiek poprawia i zatwierdza |
| 5. Sztab | 2:05–2:40 | **film 15 s** | punkt ma GPS, obraz, źródło i operatora |
| 6. Istniejące narzędzia | 2:40–3:15 | porównanie z FlightHub 2 i TAK | przewaga musi przejść test porównawczy |
| 7. Dowody | 3:15–3:55 | wynik testowy i granice | znamy ograniczenia i mamy plan walidacji |
| 8. Pilotaż | 3:55–4:25 | materiały i mierniki | droga do wdrożenia zaczyna się od ćwiczeń |
| 9. Prośba | 4:25–5:00 | partner do walidacji | konkretna prośba do jury |

Przećwicz dwa razy z zegarkiem. Gdy filmy są gotowe, uruchamiaj je jednym kliknięciem. Na czas pokazu wyłącz powiadomienia i sprawdź wcześniej dźwięk, choć filmy powinny działać bez niego.

## Slajd 1 — AeroPass (20 s)

**Na slajdzie dokładnie:** `AeroPass`; `Obserwacje z lotu na mapie sztabu`; `Operator DJI · model na komputerze · zatwierdzony punkt GPS`.

**Powiedz:** „AeroPass pomaga zamienić zdjęcie z lotu w informację, którą można przekazać dalej. Operator już ma drona i wie, gdzie leci. My pomagamy opisać to, co widać na obrazie, połączyć obserwację z punktem GPS i pokazać ją sztabowi. Dronem nadal steruje człowiek.”

**Obraz:** LADI v2, zdjęcie referencyjne z USA. Podpis źródła jest w notatkach slajdu. Nie mów, że jest to powódź w Polsce ani materiał z Waszego lotu.

## Slajd 2 — Problem (30 s)

**Na slajdzie dokładnie:** `Obraz z lotu potrzebuje kontekstu`; `Co się stało?`; `Gdzie dokładnie?`; `Kto to potwierdził?`; `Sztab potrzebuje odpowiedzi z obrazem, czasem i źródłem.`

**Powiedz:** „Zdjęcie lotnicze może pokazać wiele szczegółów, ale dla osoby prowadzącej działania kluczowe są cztery rzeczy: co widać, gdzie jest zdarzenie, kiedy je obserwowano i kto potwierdził opis. Sam plik zdjęcia nie tworzy jeszcze takiej informacji. Tę lukę chcemy zamknąć.”

**Dowód kontekstu:** KG PSP opisuje rozwijanie użycia BSP w działaniach ratowniczych, w tym wnioski po powodzi. Potrzebę konkretnego formatu meldunku trzeba potwierdzić w rozmowach z dyżurnymi, więc nie twierdź, że PSP zamówiła AeroPass.

## Slajd 3 — Przepływ (35 s)

**Na slajdzie dokładnie:** `Jedna obserwacja, dwa stanowiska`; `01 Operator DJI — prowadzi lot i robi zdjęcie`; `02 Komputer — porównuje obraz z opisami`; `03 Operator — weryfikuje i wskazuje GPS`; `04 Sztab — widzi potwierdzony punkt`.

**Powiedz:** „Pilot używa swojego kontrolera i własnych procedur. Po przekazaniu zdjęcia na laptop model pokazuje propozycje opisów. Operator wybiera poprawny opis lub wpisuje własny, na przykład liczbę powalonych drzew. Wskazuje położenie obserwowanego miejsca, które nie musi być pozycją drona. Dopiero po zatwierdzeniu sztab widzi punkt z obrazem i źródłem.”

**Ważna precyzja:** DJI Matrice 30 jest przykładem istniejącego sprzętu z kamerą i kontrolerem, lecz nie twierdź, że każdy zastęp PSP/OSP ma ten model. Obecny prototyp nie pobiera zdjęć ani GPS automatycznie z DJI. Nie mów, że DJI „nie ma autonomii”: projekt po prostu nie opiera się na autonomicznym locie.

## Slajd 4 — Film operatora (40 s, w tym 18 s filmu)

**Na slajdzie dokładnie:** `Człowiek wybiera opis zdarzenia`; w dużym polu `WIDEO 1`; obok trzy krótkie zdania o sugestiach, korekcie i zatwierdzeniu.

**Nagraj 18 sekund bez montażowej sztuczki:**

1. 0–4 s: otwórz `http://localhost:8767/` i wybierz zdjęcie. Na nagraniu pokaż jego źródło. Możesz użyć `dane/ladi/obrazy/test-17-011.jpg` jako materiału **demonstracyjnego**; nie przedstawiaj go jako polski lot.
2. 4–8 s: pokaż listę propozycji CLIP. Przeczytaj „względne dopasowanie”, nie „80% prawdopodobieństwa zalania”.
3. 8–13 s: zmień ocenę w polu operatora na tę, którą człowiek naprawdę widzi. Jeżeli pokazujesz `Powalone drzewa`, liczbę wpisuje człowiek, bo model jej nie liczy.
4. 13–18 s: wpisz operatora, źródło i **testowy** GPS, zaznacz `Materiał demonstracyjny`, kliknij `Zatwierdź i pokaż sztabowi`.

**Powiedz po filmie:** „Sztab nie dostaje surowego wyniku modelu. Dostaje ocenę potwierdzoną przez operatora. Procenty przy CLIP są jedynie rankingiem opisów, bez kalibracji do ryzyka.”

**Nie wpisuj testowego GPS tak, jakby był rzeczywistym miejscem zdjęcia.** Materiał w filmie ma być jawnie oznaczony jako demo. W realnym pilotażu operator wskaże punkt na podstawie kontrolera lub mapy, a później sprawdzimy dokładność tej czynności.

## Slajd 5 — Film panelu sztabu (35 s, w tym 15 s filmu)

**Na slajdzie dokładnie:** `Punkt GPS z dowodem na mapie`; w dużym polu `WIDEO 2`; obok `Rodzaj zdarzenia`, `GPS miejsca`, `Obraz i źródło`, `Operator i czas`, `GeoJSON / KML`.

**Nagraj 15 sekund:**

1. 0–4 s: otwórz `http://localhost:8765/panel/`, pokaż nową kartę `Obserwacje operatora`.
2. 4–9 s: kliknij punkt na mapie; pokaż rodzaj zdarzenia, operatora, czas, GPS i odnośnik do zdjęcia.
3. 9–15 s: kliknij `Eksport GeoJSON`, aby wykazać możliwość przekazania geodanych do innego narzędzia.

**Powiedz:** „To jest własny panel sztabu w prototypie. Nie ogłaszamy integracji z ATAK ani z produkcyjnymi systemami PSP. Eksport GIS jest działającą granicą integracyjną, którą trzeba sprawdzić z odbiorcą.”

**Jeśli powstanie i zostanie zweryfikowany most do ATAK**, możesz w tym miejscu zamienić film panelu na prawdziwe nagranie odbioru punktu w ATAK. Sam kod eksperymentalnego mostu lub wysłana ramka UDP nie dowodzą działania na urządzeniu PSP.

## Slajd 6 — Istniejące narzędzia (35 s)

**Na slajdzie dokładnie:** `Obecne narzędzia i AeroPass`; `DJI FlightHub 2 / TAK — zdjęcia, mapa i adnotacje już istnieją`; `AeroPass dziś — lokalna weryfikacja przez operatora, zapis źródła i GPS, eksport GIS`; `Hipoteza: ustrukturyzowany meldunek powodziowy pomaga sztabowi szybciej ustalić sytuację`.

**Powiedz:** „Nie twierdzimy, że pierwsi umieszczamy zdjęcie na mapie. FlightHub 2 ma adnotacje i alerty AI, a TAK obsługuje zdjęcia z pozycją. Nasz prototyp skupia się na uporządkowanym meldunku o przeszkodzie podczas powodzi: model sugeruje, operator poprawia, a sztab widzi zatwierdzony punkt ze źródłem. Musimy wykazać, że ta czynność daje wartość względem narzędzi już używanych.”

**Pokaż kod tylko na pytanie jury:** `ai/kamera.py` (analiza i zapis), `ai/kamera.html` (formularz operatora), `panel/index.html` (widok sztabu), `testy/test_operator.py` (zatwierdzenie, GPS, brak duplikatu). Nie otwieraj podczas 5 minut długiego pliku źródłowego.

**Wniosek biznesowy:** zdjęcie, punkt na mapie i prosty alert AI są już dostępne u dużych dostawców. W pilotażu trzeba porównać pracę z AeroPass z obecnym obiegiem w tej samej jednostce i wykazać korzyść, której obecne narzędzie nie daje. Nie deklaruj przewagi cenowej ani technicznej bez pomiaru.

## Slajd 7 — Dowody i granice (40 s)

**Na slajdzie dokładnie:** `Wynik modelu ma wyraźne granice`; duże `41 / 47`; `zalanych zdjęć FloodNet wykrył badawczy YOLO`; `CLIP w pokazie`; `Wynik to względne dopasowanie do opisów. Skuteczność na polskich ujęciach pozostaje nieznana.`; mały dopisek o 1 500 zdjęciach LADI bez treningu.

**Powiedz:** „Mamy wcześniejszy test innego modelu, YOLO, na FloodNet: wykrył 41 z 47 zdjęć oznaczonych jako zalana droga. Kolejne sześć pozostawił bez rozstrzygnięcia. W tej ograniczonej próbie żadne zalane zdjęcie nie zostało oznaczone jako suche. To dane z Teksasu i nie są walidacją działania w Polsce. Dzisiejszy pokaz używa CLIP, który nie ma jeszcze takiego testu terenowego. Zebraliśmy też 1 500 obrazów LADI jako bibliotekę referencyjną; nie trenowaliśmy na nich modelu.”

**Czego nie mówić:** „Model ma 87% skuteczności w PSP”, „zero błędów”, „1 500 zdjęć treningowych”, „80% pewności zdarzenia”. Wynik 41/47 dotyczy YOLO i konkretnego testu, nie CLIP w interfejsie operatora.

## Slajd 8 — Pilotaż (30 s)

**Na slajdzie dokładnie:** `Pilotaż z jednostką PSP lub OSP`; `Materiały z ćwiczeń`; `Zdjęcia z posiadanego sprzętu DJI, opisane przez operatorów.`; `Mierzymy w praktyce`; `Czas od zdjęcia do punktu`; `Zgodność ocen operatorów`; `Błędy i przypadki „nie wiem”`; `Jakość lokalizacji GPS`.

**Powiedz:** „Następny etap to ćwiczenie z jednostką, która już używa drona. Ten sam materiał przejdzie przez jej obecny obieg i przez AeroPass. Zmierzymy czas przygotowania potwierdzonej obserwacji, błędy modelu, zgodność ludzi i dokładność wskazanego punktu. Dopiero taki pilotaż pokaże, czy wnosimy wartość ponad istniejące narzędzia.”

**Co mierzyć technicznie:** od momentu wyboru pliku do zatwierdzenia; czy operator poprawił model; zgodność z niezależną oceną; brakujące źródło i GPS; czas otwarcia punktu w panelu. Nie obiecuj ROI ani skrócenia czasu akcji na podstawie symulacji czterech dronów.

## Slajd 9 — Prośba (35 s)

**Na slajdzie dokładnie:** `Szukamy partnera do walidacji`; `AeroPass porządkuje dane z lotu, który operator i tak wykonuje.`; `Pierwszy cel: wiarygodny, potwierdzony punkt dla sztabu.`

**Powiedz:** „Szukamy partnera z PSP albo OSP do wspólnego ćwiczenia oraz wsparcia walidacji na polskich zdjęciach. Chcemy sprawdzić proces z operatorem i dyżurnym, a potem dopasować eksport do ich faktycznego obiegu danych. Fundusze przeznaczylibyśmy na zbiór z ćwiczeń, ocenę jakości modelu i integrację. Nie potrzebujemy budować nowego drona. Pierwszy dowód wartości to punkt, któremu sztab może zaufać, bo wie, kto go potwierdził i skąd pochodzi obraz.”

**Jeśli jury wymaga kwoty:** wpisz ją dopiero po policzeniu kosztów pilotażu, sprzętu już posiadanego przez partnera, czasu operatorów, danych i integracji. W tej wersji nie ma fikcyjnego budżetu ani wyceny rynku.

## Pytania jury: 2 minuty

**„Czy to działa z naszym DJI?”** — „Dzisiaj przyjmujemy zdjęcie i GPS ręcznie z pracy operatora. To pozwala przetestować wartość bez ingerowania w drona. Bezpośredni import to dalszy etap, zależny od sprzętu i procedur partnera.”

**„Czy model potrafi policzyć drzewa?”** — „Jeszcze nie. CLIP sugeruje tylko opis sceny związany z zalaniem. Liczbę drzew wpisuje operator. Nie pokazujemy przykładowych 80/20% jako prawdopodobieństw bez kalibracji.”

**„Czy model jest bezpieczny?”** — „Nie ma walidacji na polskich lotach. Dlatego surowy wynik nie trafia na mapę jako potwierdzony fakt, a przejezdność drogi nie jest wyznaczana z pojedynczej klatki. Pilot obejmie niezależną ocenę obrazów i błędów.”

**„A ATAK albo nasze systemy?”** — „Dziś działa eksport GeoJSON i KML. Nie mamy potwierdzonej integracji produkcyjnej. Najpierw ustalimy z partnerem format, uprawnienia i procedurę odbioru.”

**„DJI FlightHub 2 już to robi. Po co AeroPass?”** — „Tak, FlightHub 2 ma mapę, adnotacje i alerty AI. Właśnie dlatego pilotaż porówna ten sam przepływ na obecnym narzędziu i w AeroPass. Naszą hipotezą jest wartość jawnej korekty modelu przez operatora i jednolitego meldunku o zdarzeniu powodziowym dla sztabu. Jeśli nie wykażemy poprawy, nie będziemy twierdzić, że potrzebny jest osobny produkt.”

**„Ile czasu/oszczędności?”** — „Jeszcze tego nie zmierzyliśmy z operatorem. Czasy ze starej symulacji lotów są badawczym porównaniem planera, a nie wynikiem tego procesu. Miernik w pilotażu to czas do potwierdzonego punktu.”

**„Jaka licencja?”** — „Repozytorium jest AGPL-3.0, bo zawiera komponent Ultralytics YOLO. Jeśli wdrożenie wymaga modelu zamkniętego, trzeba rozważyć licencję Enterprise lub inny stos zgodny z wymaganiami odbiorcy. Prototypu nie przedstawiamy jako gotowego kontraktu komercyjnego.”

**„Co z danymi z akcji?”** — „Obecny pokaz działa lokalnie i zapisuje zdjęcia na komputerze. Przed użyciem w jednostce trzeba uzgodnić uprawnienia, retencję materiałów, sposób audytu i zasady przekazywania do innych systemów. Prototyp nie jest wdrożeniem produkcyjnym.”

## Źródła i oznaczenia na slajdach

- [KG PSP: Bezzałogowe Statki Powietrzne w PSP](https://www.gov.pl/web/kgpsp/bezzalogowe-statki-powietrzne-w-panstwowej-strazy-pozarnej) — kontekst użytkownika, bez tezy o zakupie AeroPass.
- [DJI Matrice 30: specyfikacja](https://enterprise.dji.com/matrice-30/specs) — przykład istniejącego sprzętu z kamerą i kontrolerem. Oferta nie zależy od konkretnego modelu.
- [DJI FlightHub 2](https://enterprise.dji.com/flighthub-2) oraz [TAK](https://tak.gov/solutions/recreation) — istniejące funkcje map, adnotacji, obrazów i alertów, do których trzeba porównać AeroPass.
- [FloodNet Supervised v1.0](https://github.com/BinaLab/FloodNet-Supervised_v1.0) oraz `wyniki/metryki_decyzji.json` — test YOLO na zdjęciach z Teksasu.
- [MIT Lincoln Laboratory LADI v2](https://huggingface.co/datasets/MITLL/LADI-v2-dataset) — zdjęcia na slajdach 1–2, CC BY 4.0; baza 1 500 obrazów w repo bez treningu.
- [Ultralytics: licencja AGPL-3.0 i Enterprise](https://github.com/ultralytics/ultralytics/blob/main/README.md) — odpowiedź o licencji.

## Kontrola przed wejściem

1. Otwórz `AeroPass_pitch.pdf`, przejdź przez wszystkie 9 stron i sprawdź czy rzutnik mieści 16:9. PPTX służy do edycji; PDF to stabilny zapas.
2. Uruchom `python panel/serwer.py` i `python ai/kamera.py` w środowisku z zależnościami. Sprawdź `http://localhost:8765/panel/` oraz `http://localhost:8767/`.
3. Nagraj dwa filmy, obejrzyj je do końca i wstaw do dużych pustych pól na slajdach 4–5. Zachowaj na dysku obok PPTX oryginalne MP4. Jeśli nie są gotowe, pokaż te same czynności na żywo; nie odtwarzaj fikcyjnego nagrania.
4. W formularzu oznacz materiał testowy jako `Materiał demonstracyjny`. Nie przedstawiaj testowego GPS jako położenia zdjęcia.
5. Sprawdź, że nigdzie nie padają deklaracje: autonomiczny lot, produkcyjna integracja z DJI/ATAK, potwierdzona przejezdność z obrazu albo zwalidowana skuteczność CLIP w Polsce.
