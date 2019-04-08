# Temat pracy: Rozszerzona rzeczywistość we wspomaganiu obsługi urządzeń

## Specyfikacja
Projekt ma na celu usprawnienie obsługi, konserwacji lub nauki obsługi urządzenia za pomocą technik rozszerzonej rzeczywistości. Użytkownik końcowy powinien mieć do dyspozycji kamerę oraz ekran i połączone z nimi urządzenie, na którym będzie uruchomiony skrypt analizujący i modyfikujący obraz z kamery.

## Scenariusze użycia

1. Pracownik musi przeprowadzić konserwację maszyny (urządzenie analizowane). Ma ze sobą urządzenie analizujące, kamera patrzy na urządzenie i je wykrywa. Pobierane są z brokera informacje które je dotyczą. Pokazywane są krok po kroku czynności, które powinny zostać przeprowadzone, aby konwerserwacja była poprawna. Analogiczną sytuacją jest awaria - zanim zostanie wezwany serwis, możliwe jest przeprowadzenie działań diagnostycznych nawet przez niewykwalifikowanego pracownika, jeśli będzie podążał za wskazówkami pokazywanymi na obrazie. Dzięki śledzeniu obiektu możliwe jest wskazanie każdego elementu za pomocą strzałki, chmurki z komentarzem bądź animacji obiektu 3D naniesionego na obraz.
2. Pracownik musi przejść trening z obsługi maszyny. Po znalezieniu maszyny na obrazie z kamery i uruchomieniu odpowiedniego programu możliwe jest pokazanie krok po kroku w jaki sposób maszynę się obsługuje, czego nie robić oraz na co zwracać uwagę. Można pokazać film instruktażowy, a następnie za pomocą strzałek, chmurek z komentarzem bądź animacji obiektów 3D kierować użytkownika krok po kroku.

### Opis słowny architektury
Z projektu można wydzielić 3 części:

1. Broker - "centrum dowodzenia". Powinno być w stanie połączyć się z urządzeniem analizującym jak i analizowanym. Jest pośrednikiem pomiędzy nimi.
2. Urządzenie analizowane - do testów stworzono proste urządzenie oparte na układzie Arduino Leonardo. Powinno ono mieć dostęp do sieci (w tym wypadku WiFi poprzez moduł ESP8266). W tym urządzeniu uruchomiony będzie program analizujący stan elementów peryferyjnych - guzik, LED, switch, potencjometr. Wgrany program powinien również być w stanie połączyć się poprzez protokół MQTT z brokerem i przesłać stan każdego z wymienionych elementów.
3. Urządzenie analizujące - złożone z kamery, ekranu i urządzenia do wykonywania analizy i obróbki obrazu. Po znalezieniu maszyny na obrazie, łączy się z brokerem subskrybując temat z nim związany, oraz pozwala na uruchomienie programu obsługi. Dla testów urządzenie analizujące składa się z RaspberryPi z podłączoną doń kamerą internetową. Przesyła on poprzez ZeroMQ obraz odbierany przez laptop, na którym odbywa się obróbka i pokazanie obrazu. Jeśli czas pozwoli (przed obroną) stworzona zostanie aplikacja na telefon z systemem Android, która powinna wykonywać wszystkie procesy. 

**Notka: Docelowo w brokerze powinny być dane, punkty kluczowe, deskryptory i programu obsługi każdego urządzenia, a "analizatory" jedynie przy uruchomieniu pobierać je z bazy, natomiast do prototypowania wygodniej jest je trzymać w programie razem z obróbką obrazu.**


### Dodanie nowego urządzenia do systemu
Każde urządzenie będzie musiało zostać sfotografowane oraz przejść przez proces ekstrakcji punktów kluczowych oraz dekryptorów, które zostaną zapisane. Skonfigurowane muszą zostać również pobierane parametry, oraz programy obsługi.

### Analiza obrazu
Obraz z kamery zostaje przekazany do skryptu. Każdy kadr przechodzi przez podobny proces co zdjęcia urządzeń, a następnie jest przeszukiwany pod kątem obecności jednego z urządzeń za pomocą dopasowania punktów kluczowych (*Feature matching*). **(THO: co jeśli pojawi się więcej niż jeden)** Rozpoznanie urządzenia powinno zwracać jego ID.

### Modyfikacje obrazu
Podstawową formą modyfikacji obrazu z kamery jest naniesienie na obraz tabelki z parametrami maszyny. Powinno się to odbywać w czasie rzeczywistym, byćmoże z dodatkowymi informacjami w postaci min/maks wartość danego parametru, wykres, data ostatniej konserwacji itd.

Dla programów obsługi powinna być możliwość tworzenia poradnika w jaki sposób korzystać z urządzenia za pomocą sekwencji obrazków, ikon, obiektów 3d bądź animacji nakłądanych na obraz.

### Programy obsługi
Rozumie się przez to nawiązanie komunikacji z urządzeniem, pobranie jego parametrów i pokazanie ich na ekranie, bądź pół interaktwyny pokaz związany z jego obsługą lub konserwacją.

