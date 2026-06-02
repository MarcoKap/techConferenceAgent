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

---

## Starten

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
- `ESC` – Beenden

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
        └── DisplayManager
              ├── EyeRenderer
              └── MouthRenderer
```

Alle Hardware-Controller laufen in eigenen Threads. Beim Szenen-Wechsel stoppt der `SceneManager` laufende Animationen via `threading.Event` und startet die neuen parallel.

---

## Weiterentwicklung

Details zu Implementierungsphasen, Szenen-Parametern und technischen Hinweisen: [PLAN.md](PLAN.md)
