# Klasy:
1. AugumentAPI
1. Detector
1. Layer
1. Machine
1. MQTTClient


## AugumentAPI
Klasa główna, spina wszystkie inne

## Detector
#### Konstruktor:
Detector(machine) -> detector

#### Metody:
 - detect(image) -> ret, matrix

## Layer
Obsługuje nakładanie dodatków na obraz; stworzenie nowej instancji powoduje dodanie jej do statycznego pola "Layer.all". Każdy (Layer x).draw() jest wywoływany co klatkę w odpowiedniej kolejności przed wyświetleniem klatki.
#### Pola:
 - name - nazwa warstwy
 - order - kolejność rysowania (1 - pierwsze)

#### Metody:
 - draw(img) - funkcja rysująca
 - draw_* - funkcje częściowe rysujące
