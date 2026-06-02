# Plan: Conference Robot – AI Agent Simulation

## TL;DR

Python-basiertes Steuerungssystem für einen Konferenz-Roboter auf Raspberry Pi 3B.  
Pygame rendert animierte Augen/Mund auf dem 5"-Display. `rpi_ws281x` steuert den WS2812B-LED-Ring, ein PCA9685-Board steuert den Servo für die Kopfdrehung, zwei GPIO-Taster navigieren durch 6 vordefinierte Szenen. Ein zentraler `SceneManager` orchestriert alle Subsysteme über Threads.

---

## Hardware

| Komponente | Details |
|---|---|
| Raspberry Pi 3B | 1 GB RAM, ARMv7, Akku-betrieben |
| Display | 5" DSI/HDMI, eingebaut im Kopf |
| LED-Streifen | WS2812B (NeoPixel), ring-förmig um die Basis |
| Motor | Servo für Kopfdrehung (links/rechts), gesteuert via PCA9685 (I2C) |
| Audio | Soundboard + Lautsprecher (ALSA / pygame.mixer) |
| Eingabe | 2× physische GPIO-Taster (Szene Weiter / Zurück) |

---

## Die 6 Szenen

| # | ID | Name | Augen | LEDs | Servo | Audio |
|---|---|---|---|---|---|---|
| 1 | `normal_operation` | Normaler Betrieb | Blau-grün, ruhiges Blinken | Blau/Weiß, langsames Pulsieren | Mitte, leichtes Schwanken | – |
| 2 | `thinking` | Denkend | Gelb, wandernde Pupille | Gelb-Orange langsamer Sweep | Langsames Links-Rechts | `thinking.wav` |
| 3 | `surprised` | Überrascht | Weiß/Gelb, weit geöffnet, Pupillen zucken | Flash Weiß → schnelles Pulsieren | Ruck-Bewegung | `surprised.wav` |
| 4 | `warning` | Warnend / Alarm | Orange-Rot, pulsierend | Rot schnell blinkend | Shake (Links-Rechts) | `warning_alarm.wav` |
| 5 | `evil_agent` | Böser Agent | Rot, schmal/böse, Glühen | Dunkles Rot/Lila glühen | Langsames bedrohliches Sweep | `evil_agent.wav` |
| 6 | `out_of_order` | Out of Order | Grau, X-Augen | Aus / sehr dunkel | Droop (sackt ab) | `out_of_order.wav` |

---

## Software-Architektur

### Entry Point
- `main.py` – Initialisiert alle Controller, startet Threads, Hauptloop wartet auf Button-Events und delegiert an `SceneManager`

### Core Module
- `config.py` – Alle Konstanten (GPIO-Pins, I2C-Adresse, LED-Anzahl, Display-Auflösung, Servo-Winkel, `IS_MOCK` Flag)
- `scene_manager.py` – Zustandsmaschine: `current_scene_index`, `next()` / `prev()`, löst Transition aus (stoppt laufende Animationen, startet neue Szene)

### Hardware-Controller (je eigener Thread)

| Datei | Beschreibung |
|---|---|
| `hardware/button_handler.py` | RPi.GPIO, Entprellung (50ms), Events → Queue |
| `hardware/led_controller.py` | rpi_ws281x, Animations-Funktionen: `idle_pulse`, `thinking_swipe`, `alarm_flash`, `evil_glow`, `error_off`, `surprised_burst` |
| `hardware/servo_controller.py` | Adafruit PCA9685 via I2C, Positions-Profile: `center`, `slow_sweep`, `nod`, `shake`, `droop` |
| `hardware/audio_controller.py` | pygame.mixer, `play_scene_audio(scene_id)`, Loop/Einmalig-Flag |

### Display-Rendering

| Datei | Beschreibung |
|---|---|
| `display/display_manager.py` | pygame Fullscreen, Animation-Loop ~30fps, delegiert an Renderer |
| `display/eye_renderer.py` | Augen mit Parametern: Farbe, Form (`normal` / `wide` / `narrow` / `x` / `angry`), Öffnungsgrad, Pupillenbewegung |
| `display/mouth_renderer.py` | Optionaler Mund (Linie/Kurve je nach Emotion) |

### Szenen-Definitionen
- `scenes/scene_definitions.py` – Liste von `SceneConfig`-Dataclasses, je mit:
  - `display`: `eye_color`, `eye_shape`, `pupil_animation`, `mouth_type`
  - `leds`: `animation_name`, `color_primary`, `color_secondary`, `speed`
  - `servo`: `angle_profile`, `movement`
  - `audio`: `filename` oder `None`, `loop: bool`

---

## Dateistruktur

```
techConferenceAgent/
├── main.py
├── config.py
├── scene_manager.py
├── display/
│   ├── display_manager.py
│   ├── eye_renderer.py
│   └── mouth_renderer.py
├── hardware/
│   ├── __init__.py                  ← Factory: echte vs. Mock-Controller
│   ├── button_handler.py
│   ├── led_controller.py
│   ├── servo_controller.py
│   ├── audio_controller.py
│   └── mock/
│       ├── mock_button_handler.py   ← Pfeiltasten statt GPIO
│       ├── mock_led_controller.py   ← Konsole / pygame-Overlay
│       ├── mock_servo_controller.py ← Konsolenausgabe
│       └── mock_audio_controller.py ← pygame.mixer (identisch)
├── scenes/
│   └── scene_definitions.py
├── assets/
│   ├── audio/
│   │   ├── thinking.wav
│   │   ├── surprised.wav
│   │   ├── warning_alarm.wav
│   │   ├── evil_agent.wav
│   │   └── out_of_order.wav
│   └── fonts/
├── requirements.txt           ← RPi (alle Deps)
└── requirements-dev.txt       ← Windows Dev (nur pygame)
```

---

## Cross-Platform Dev-Strategie (Windows ↔ Raspberry Pi)

### Plattform-Erkennung in `config.py`

```python
import platform, os

IS_MOCK = platform.system() != 'Linux' or os.getenv('MOCK_HARDWARE') == '1'
```

### Mock-Implementierungen

| Echte Hardware | Windows-Mock |
|---|---|
| `RPi.GPIO` (Buttons) | Pfeiltasten `←` `→` via pygame KeyEvents |
| `rpi_ws281x` (LEDs) | Print in Konsole + optionaler pygame-Overlay-Balken |
| `adafruit-pca9685` (Servo) | Print in Konsole (Winkel / Bewegung) |
| `pygame.mixer` (Audio) | Identisch – läuft nativ auf Windows |

### Factory Pattern in `hardware/__init__.py`

```python
from config import IS_MOCK

if IS_MOCK:
    from hardware.mock.mock_led_controller import MockLedController as LedController
    from hardware.mock.mock_servo_controller import MockServoController as ServoController
    from hardware.mock.mock_button_handler import MockButtonHandler as ButtonHandler
    from hardware.mock.mock_audio_controller import MockAudioController as AudioController
else:
    from hardware.led_controller import LedController
    from hardware.servo_controller import ServoController
    from hardware.button_handler import ButtonHandler
    from hardware.audio_controller import AudioController
```

### Deployment-Workflow

1. Entwickeln & debuggen auf Windows – Pfeiltasten steuern Szenen, pygame-Vollbild zeigt Augen
2. Per `rsync` / `scp` auf den RPi übertragen
3. `sudo pip install -r requirements.txt` auf dem RPi
4. `sudo python main.py` starten (root wegen rpi_ws281x DMA)

---

## Abhängigkeiten

### `requirements.txt` (Raspberry Pi)

```
pygame>=2.0
rpi_ws281x>=4.3
adafruit-circuitpython-pca9685
adafruit-circuitpython-motor
RPi.GPIO>=0.7
```

### `requirements-dev.txt` (Windows / Mac / Linux Dev)

```
pygame>=2.0
```

---

## Implementierungsphasen

### Phase 1 – Grundstruktur
1. Dateistruktur mit leeren Stubs anlegen
2. `config.py` mit allen Hardware-Konstanten befüllen
3. `requirements.txt` und `requirements-dev.txt` erstellen

### Phase 2 – Hardware-Controller *(alle unabhängig, parallel umsetzbar)*
4. `button_handler.py` + `mock_button_handler.py` – GPIO, Entprellung, Event-Queue
5. `led_controller.py` + `mock_led_controller.py` – WS2812B Init + Animations-Funktionen
6. `servo_controller.py` + `mock_servo_controller.py` – PCA9685 I2C + Positions-Profile
7. `audio_controller.py` + `mock_audio_controller.py` – pygame.mixer play/stop

### Phase 3 – Display *(unabhängig von Phase 2)*
8. `eye_renderer.py` – Pygame-Zeichenfunktionen für Augen/Pupillen je Emotion
9. `mouth_renderer.py` – Optionaler Mund
10. `display_manager.py` – Fullscreen-Loop, ruft Renderer auf *(braucht 8+9)*

### Phase 4 – Orchestrierung *(braucht alle vorherigen)*
11. `scene_definitions.py` – 6 Szenen als `SceneConfig`-Dataclasses
12. `scene_manager.py` – `transition()`-Methode koordiniert alle Controller
13. `main.py` – Initialisierung + Hauptloop mit Button-Events

### Phase 5 – Assets & Feintuning
14. Audio-Dateien einbinden
15. Animationsgeschwindigkeiten, Servo-Winkel und Farben anpassen

---

## Verifikation

1. Auf Windows: `python main.py` – Pfeiltasten navigieren, pygame zeigt Augen, Konsole loggt LEDs/Servo
2. Umgebungsvariable `MOCK_HARDWARE=1` erzwingt Mock-Modus auch auf Linux
3. Auf RPi: `sudo python main.py` (root wegen rpi_ws281x DMA)
4. Button-Navigation: Weiter/Zurück durch alle 6 Szenen
5. Jede Szene einzeln auf LED-Animation, Augen, Servo und Audio prüfen

---

## Wichtige technische Hinweise

- **rpi_ws281x braucht root** wegen DMA-Zugriff → `sudo python main.py`
- **I2C aktivieren** via `raspi-config` → Interfacing Options → I2C → Enable
- **Pygame Fullscreen über SSH**: `export DISPLAY=:0` vor dem Start setzen
- **Audio vs. WS2812B**: Wenn Audio über HDMI läuft, LED-Strip auf DMA-Kanal 5 (GPIO 18) konfigurieren – GPIO 12 (PWM0) teilt sich Ressourcen mit Audio
- **Threading**: `threading.Event` für sauberes Stoppen laufender Animationen beim Szenen-Wechsel
- **Autostart**: `systemd`-Service mit `ExecStart=/usr/bin/python /home/pi/techConferenceAgent/main.py`
