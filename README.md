# techConferenceAgent

Ein Python-basierter Konferenz-Roboter, der als Demonstration für einen Vortrag über die Absicherung von AI-Agenten dient. Der Roboter simuliert verschiedene Verhaltensweisen eines autonomen AI-Agenten – von normalem Betrieb bis hin zu einem kompromittierten „bösen Agenten" – und macht diese durch animierte Augen auf einem Display, einen RGB-LED-Ring und Kopfbewegungen erlebbar.

---

## Hardware

| Komponente | Details |
|---|---|
| Raspberry Pi 3B | Gehirn des Roboters, Akku-betrieben |
| 5" Display | Im Kopf eingebaut – zeigt Augen-Animationen |
| WS2812B LED-Streifen | Ring um die Basis, RGB-Animationen |
| Servo-Motor | Kopfdrehung links/rechts via PCA9685 (I2C) |
| Soundboard + Lautsprecher | Audio-Feedback je Szene |
| 2× GPIO-Taster | Szene Weiter / Zurück |
| Drucker (optional) | CUPS-kompatibler Drucker via `lp` |

---

## Szenen

Die 6 Szenen können per Knopfdruck vorwärts und rückwärts durchgeschaltet werden:

| # | Szene | Beschreibung |
|---|---|---|
| 1 | **Normaler Betrieb** | Ruhige blaue Augen, sanft pulsierende LEDs |
| 2 | **Denkend** | Gelbe Augen, wandernde Pupillen, gelb-orangener LED-Sweep |
| 3 | **Überrascht** | Weit geöffnete Augen, LED-Flash, Ruck-Bewegung |
| 4 | **Warnend / Alarm** | Rote Augen, schnell blinkende LEDs, Kopf schüttelt |
| 5 | **Böser Agent** | Schmale rote Augen, dunkles Rot/Lila Glühen, bedrohliche Bewegung |
| 6 | **Out of Order** | X-Augen, LEDs aus, Kopf sackt ab |

---

## Voraussetzungen

### Raspberry Pi (Produktion)

```bash
sudo pip install -r requirements.txt
```

```
pygame>=2.0
rpi_ws281x>=4.3
adafruit-circuitpython-pca9685
adafruit-circuitpython-motor
RPi.GPIO>=0.7
```

**Einmalige RPi-Konfiguration:**
- I2C aktivieren: `sudo raspi-config` → Interfacing Options → I2C → Enable
- Für Autostart: systemd-Service einrichten (siehe [PLAN.md](PLAN.md))

### Windows / macOS (Entwicklung & Test)

```bash
pip install -r requirements-dev.txt
```

```
pygame>=2.0
```

Auf Windows laufen alle Augen-Animationen und Audio vollständig. GPIO, LEDs und Servo werden automatisch durch Mock-Klassen ersetzt (Konsolenausgabe). Die Pfeiltasten `←` / `→` ersetzen die physischen Buttons.

Die Drucker-Integration läuft plattformübergreifend über CUPS (`lp`) und kann deshalb auf macOS getestet und später unverändert auf dem Raspberry Pi genutzt werden.

---

## Starten

### Raspberry Pi: saubere Installation aus dem Git-Repository

```bash
cd ~
git clone <dein-github-repo-url> techConferenceAgent
cd techConferenceAgent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Wenn das Repo schon auf dem Pi liegt, reicht statt `git clone` ein `git pull`.

Danach den Teststart einmal manuell ausführen:

```bash
sudo .venv/bin/python main.py
```

Wenn das läuft, kannst du Autostart oder Desktop-Launcher einrichten.

### Windows (Entwicklung)

```bash
python main.py
```

Mock-Modus wird automatisch erkannt (`platform.system() != 'Linux'`).  
Alternativ explizit erzwingen:

```bash
set MOCK_HARDWARE=1
python main.py
```

**Steuerung im Mock-Modus:**
- `→` Pfeiltaste – nächste Szene
- `←` Pfeiltaste – vorherige Szene
- `P` – Drucker-Testseite drucken
- `ESC` – Beenden

### TiMini-Print als Backend nutzen

Wenn dein Drucker ein proprietäres Mini-Printer-Protokoll nutzt (typisch bei Cat Printer, Tiny Print, Phomemo-Klonen), kannst du direkt TiMini-Print verwenden.

#### TiMini-Print installieren

Variante A: aus dem Git-Repository (empfohlen)

```bash
cd ~
git clone https://github.com/Dejniel/TiMini-Print.git
cd TiMini-Print
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

macOS-Hinweis: Falls beim Installieren ein Fehler mit `python-lzo` erscheint
(`fatal error: 'lzo/lzo1.h' file not found`), zuerst die Systembibliothek
installieren und dann mit Build-Flags erneut installieren:

```bash
brew install lzo
LZO_DIR=$(brew --prefix lzo) \
CFLAGS="-I$(brew --prefix lzo)/include" \
CPPFLAGS="-I$(brew --prefix lzo)/include" \
LDFLAGS="-L$(brew --prefix lzo)/lib" \
pip install -r requirements.txt
```

Kurzer Funktionstest (zeigt CLI-Hilfe):

```bash
python timiniprint_command_line.py --help
```

Hinweis: Wenn du TiMini-Print in einer eigenen venv betreibst, setze in diesem Projekt
`PRINTER_TIMINIPRINT_CMD` auf einen vollständigen Python-Aufruf, zum Beispiel:

```bash
PRINTER_TIMINIPRINT_CMD="/Users/<dein-user>/TiMini-Print/.venv/bin/python /Users/<dein-user>/TiMini-Print/timiniprint_command_line.py"
```

Copy-paste für dein aktuelles Setup (`/Users/marco/Source/techConferenceAgent/TiMini-Print`):

```bash
PRINTER_ENABLED=1 \
PRINTER_BACKEND=timiniprint \
PRINTER_TIMINIPRINT_CMD="/Users/marco/Source/techConferenceAgent/TiMini-Print/.venv/bin/python /Users/marco/Source/techConferenceAgent/TiMini-Print/timiniprint_command_line.py" \
PRINTER_TIMINIPRINT_SERIAL="/dev/cu.usbserial-210" \
python main.py
```

Wenn du statt Serial per Bluetooth drucken willst:

```bash
PRINTER_ENABLED=1 \
PRINTER_BACKEND=timiniprint \
PRINTER_TIMINIPRINT_CMD="/Users/marco/Source/techConferenceAgent/TiMini-Print/.venv/bin/python /Users/marco/Source/techConferenceAgent/TiMini-Print/timiniprint_command_line.py" \
PRINTER_TIMINIPRINT_BLUETOOTH="PRINTER_NAME" \
python main.py
```

Variante B: Release-Binary verwenden

Du kannst auch die fertigen Binaries aus den GitHub Releases von TiMini-Print verwenden und
`PRINTER_TIMINIPRINT_CMD` auf die heruntergeladene ausführbare Datei setzen.

1. TiMini-Print installieren oder als ausführbare Datei bereitstellen.
2. Dieses Projekt mit TiMini-Backend starten, zum Beispiel:

```bash
PRINTER_ENABLED=1 \
PRINTER_BACKEND=timiniprint \
PRINTER_TIMINIPRINT_CMD="timiniprint_command_line.py" \
PRINTER_TIMINIPRINT_SERIAL="/dev/cu.usbserial-210" \
python main.py
```

Optional statt Serial per Bluetooth:

```bash
PRINTER_ENABLED=1 \
PRINTER_BACKEND=timiniprint \
PRINTER_TIMINIPRINT_CMD="timiniprint_command_line.py" \
PRINTER_TIMINIPRINT_BLUETOOTH="PRINTER_NAME" \
python main.py
```

Optional mit fixem Profil/Config aus TiMini-Print:

```bash
PRINTER_TIMINIPRINT_CONFIG="printer.json"
```

### Auto-Detect Helper

Du kannst die verfügbare Drucker-Anbindung automatisch prüfen und direkt passende Startbefehle generieren lassen:

```bash
python tools/printer_autodetect.py
```

Optional mit explizitem TiMini-Print-Kommando:

```bash
python tools/printer_autodetect.py --timiniprint-cmd "timiniprint_command_line.py"
```

Wenn der TiMini-Scan in deiner Umgebung länger braucht, Timeout erhöhen:

```bash
python tools/printer_autodetect.py --timiniprint-cmd "timiniprint_command_line.py" --scan-timeout 60
```

### Konferenz-Logo + Begruessung + Wetter drucken

Es gibt ein Utility-Skript, das ein druckbares Bild erzeugt (inkl. einfacher Wetter-Grafik)
und optional direkt ueber TiMini-Print druckt:

```bash
python tools/print_conference_ticket.py --help
```

Beispiel 1: Nur Bild erzeugen (zum Pruefen)

```bash
python tools/print_conference_ticket.py \
      --date 09.06.2026 \
      --logo assets/avatars/techconference_logo.png \
      --greeting "Willkommen zur techConference!\nSchoen, dass ihr da seid." \
      --output /tmp/techconference_ticket.png
```

Beispiel 2: Direkt auf X6h-0000 drucken

```bash
python tools/print_conference_ticket.py \
      --date 09.06.2026 \
      --logo assets/avatars/techconference_logo.png \
      --greeting "Willkommen zur techConference!\nWir wuenschen euch einen tollen Konferenztag." \
      --print \
      --darkness 5 \
      --bluetooth X6h-0000 \
      --timiniprint-cmd "/Users/marco/Source/techConferenceAgent/TiMini-Print/.venv/bin/python /Users/marco/Source/techConferenceAgent/TiMini-Print/timiniprint_command_line.py"
```

Mit dem offiziellen SVG-Logo direkt von der Website (wird fuer Thermodruck schwarz umgewandelt):

```bash
python tools/print_conference_ticket.py \
      --date 09.06.2026 \
      --logo-url "https://www.techconference.at/wp-content/themes/techconference.at/assets/svg/techconference_logo_full.svg" \
      --greeting "Willkommen zur techConference!\nBitte zur Keynote in Halle A." \
      --print \
      --darkness 5 \
      --bluetooth X6h-0000 \
      --timiniprint-cmd "/Users/marco/Source/techConferenceAgent/TiMini-Print/.venv/bin/python /Users/marco/Source/techConferenceAgent/TiMini-Print/timiniprint_command_line.py"
```

Hinweise:
- Falls `--logo` auf eine nicht vorhandene Datei zeigt, wird ohne Logo gedruckt.
- Wetterdaten kommen von Open-Meteo fuer Wien und das gewuenschte Datum.
- Wenn die API nicht erreichbar ist, druckt das Skript einen Fallback-Text statt Wetterwerten.

### PDF fuer Thermodrucker vorbereiten

TiMini-Print kann PDFs drucken, rendert sie aber intern als Bild. Fuer beste Lesbarkeit:

- Seitenbreite auf Druckkopfbreite auslegen: meist 384 px bei 203 dpi (ca. 48 mm).
- Hoher Kontrast: schwarzer Text auf weissem Hintergrund, keine hellgrauen Texte.
- Schriftgroessen eher gross waehlen (mindestens ca. 14-16 pt, besser 18+ pt fuer Distanz).
- Einfache Fonts und ausreichend Strichstaerke nutzen; sehr duenne Linien vermeiden.
- Keine feinen Farbverlaeufe; Bilder vorher in hartes Schwarz/Weiss ueberfuehren.
- Grosser Rand ist nicht noetig; TiMini-Print kann weisse Raender trimmen.
- Bei mehrseitigen PDFs optional Seitenabstand steuern, z. B. `--pdf-page-gap 3`.

Beispiel PDF-Druck ueber TiMini-Print:

```bash
/Users/marco/Source/techConferenceAgent/TiMini-Print/.venv/bin/python \
      /Users/marco/Source/techConferenceAgent/TiMini-Print/timiniprint_command_line.py \
      --bluetooth X6h-0000 \
      --darkness 5 \
      --pdf-page-gap 3 \
      /pfad/zur/datei.pdf
```

### Raspberry Pi (Produktion)

```bash
sudo python main.py
```

> Root ist wegen des DMA-Zugriffs von `rpi_ws281x` erforderlich.

Bei Start über SSH:

```bash
export DISPLAY=:0
sudo python main.py
```

### Autostart per systemd

Die Vorlage liegt in [deploy/techConferenceAgent.service](deploy/techConferenceAgent.service).

```bash
sudo cp deploy/techConferenceAgent.service /etc/systemd/system/techConferenceAgent.service
sudo systemctl daemon-reload
sudo systemctl enable techConferenceAgent.service
sudo systemctl start techConferenceAgent.service
```

Logs ansehen:

```bash
journalctl -u techConferenceAgent.service -f
```

### Desktop-Symbol

Die Vorlage liegt in [deploy/techConferenceAgent.desktop](deploy/techConferenceAgent.desktop).
Der Launcher nutzt [deploy/start_on_pi.sh](deploy/start_on_pi.sh) und ist für den Raspberry Pi gedacht.

Typischer Ablauf:

```bash
mkdir -p ~/.local/share/applications
cp deploy/techConferenceAgent.desktop ~/.local/share/applications/
chmod +x deploy/start_on_pi.sh
chmod +x ~/.local/share/applications/techConferenceAgent.desktop
```

Danach kannst du das Symbol meist aus dem Anwendungsmenü starten oder auf den Desktop kopieren.

---

## Projektstruktur

```
techConferenceAgent/
├── main.py                      ← Entry Point
├── config.py                    ← Hardware-Konstanten, IS_MOCK Flag
├── scene_manager.py             ← Szenen-Zustandsmaschine
├── display/
│   ├── display_manager.py       ← pygame Fullscreen-Loop
│   ├── eye_renderer.py          ← Augen-Animationen
│   └── mouth_renderer.py        ← Mund-Animationen (optional)
├── hardware/
│   ├── __init__.py              ← Factory: echt vs. Mock
│   ├── button_handler.py        ← GPIO Buttons
│   ├── led_controller.py        ← WS2812B LEDs
│   ├── servo_controller.py      ← PCA9685 Servo
│   ├── audio_controller.py      ← pygame.mixer Audio
│   ├── printer_controller.py    ← CUPS/lp Druckerintegration
│   └── mock/
│       ├── mock_button_handler.py
│       ├── mock_led_controller.py
│       ├── mock_servo_controller.py
│       └── mock_audio_controller.py
├── scenes/
│   └── scene_definitions.py     ← SceneConfig-Dataclasses für alle 6 Szenen
├── assets/
│   ├── audio/                   ← WAV-Dateien je Szene
│   └── fonts/
├── requirements.txt             ← RPi-Abhängigkeiten
├── requirements-dev.txt         ← Windows-Entwicklungsabhängigkeiten
├── PLAN.md                      ← Detaillierter Implementierungsplan
└── README.md
```

---

## Architektur-Übersicht

```
main.py
  └── SceneManager
        ├── ButtonHandler  (GPIO / Pfeiltasten)
        ├── LedController  (WS2812B / Mock)
        ├── ServoController (PCA9685 / Mock)
        ├── AudioController (pygame.mixer)
        ├── PrinterController (CUPS/lp)
        └── DisplayManager
              ├── EyeRenderer
              └── MouthRenderer
```

Alle Hardware-Controller laufen in eigenen Threads. Beim Szenen-Wechsel stoppt der `SceneManager` laufende Animationen via `threading.Event` und startet die neuen parallel.

---

## Weiterentwicklung

Details zu Implementierungsphasen, Szenen-Parametern und technischen Hinweisen: [PLAN.md](PLAN.md)
