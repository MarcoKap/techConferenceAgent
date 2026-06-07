# Szenen-Dokumentation fuer den Vortrag

Dieses Dokument dient als inhaltliche Vorlage fuer alle Vortragsszenen.
Danach koennen wir daraus direkt eine technische Szenen-Konfiguration bauen.

## Zielbild

- Navigation per Touchscreen (links = vorherige Szene, rechts = naechste Szene)
- Pro Szene steuerbar:
  - Bildschirmdarstellung (Gesicht / Visual)
  - Audioausgabe (Waveshare WM8960 am Raspberry Pi)
  - Optionaler Druckjob (PDF)

## Bedienung im Vortrag

- Tippen links auf den Bildschirm: vorherige Szene
- Tippen rechts auf den Bildschirm: naechste Szene
- Optional mittig: Zusatzaktion (z. B. Druck der aktiven Szene)

## Szenen-Struktur (pro Szene)

Bitte fuer jede Szene die folgenden Punkte ausfuellen:

1. Name / ID
2. Zweck in der Story
3. Was sieht man auf dem Display?
4. Welche Audio-Datei wird abgespielt?
5. Soll ein PDF gedruckt werden?
6. Trigger / Timing (automatisch bei Szenenstart oder manuell)

---

## Szene 1

- ID: 101
- Titel: Standardbetrieb
- Story-Ziel: Normaler Betrieb des Deep Claw AI-Agents. Ruhiger Einstieg in die Demo.
- Display (Augen/Visual): Normale Augen, zufaellige Pupillenbewegung, gelegentliches Blinzeln.
- Audio-Datei: keine
- Druck-PDF: keine
- Druckmodus: kein Druck
- Moderationshinweis: "So sieht ein unveraenderter, stabiler Agent im Alltag aus."

## Szene 2

- ID: 201
- Titel: Wer Bin Ich?
- Story-Ziel: Aufzeigen, dass viele Organisationen und insbesondere IT-Teams nicht genau wissen, was ihre Agenten sind und in welchem Auftrag sie arbeiten.
- Display (Augen/Visual): Nachdenkliches Gesicht mit eingeblendeten Rollen-Labels wie "system_prompt", "in behalf of user", "eigener user", "berechtigungen".
- Audio-Datei: scene_02_identity.wav
- Druck-PDF: keine
- Druckmodus: kein Druck
- Moderationshinweis: "Die Kernfrage lautet: Wer ist dieser Agent eigentlich, mit welchem Prompt und mit welchen Rechten arbeitet er?"

## Szene 3

- ID: 301
- Titel: Wie Viele Sind Es?
- Story-Ziel: Zeigen, dass Organisationen oft nicht wissen, wie viele Agenten wirklich im Einsatz sind (2, 5 oder 100).
- Display (Augen/Visual): Mehrere Augen/Gesichter auf dem Screen, die sich im Laufe der Animation vermehren und den Bildschirm zunehmend fuellen.
- Audio-Datei: scene_03_agent_count.wav
- Druck-PDF: keine
- Druckmodus: kein Druck
- Moderationshinweis: "Oft gibt es keinen vollstaendigen Agenten-Inventarstand - das Risiko waechst mit der Anzahl."

## Szene 4

- ID: 401
- Titel: Welche Tools Haben Sie?
- Story-Ziel: Zeigen, dass Organisationen haeufig nicht genau wissen, welche Tools Agenten nutzen und was diese Tools koennen.
- Display (Augen/Visual): Arbeits-/Technik-Motiv mit konzentriertem Gesicht, angedeutetem Bauhelm, animierter Fernbedienung und stilisiertem Roboterarm.
- Audio-Datei: scene_04_tools_control.wav
- Druck-PDF: keine
- Druckmodus: kein Druck
- Moderationshinweis: "Ein Agent mit unbekannten Tools ist wie ein Roboterarm mit unbekanntem Werkzeugset."

## Szene 5

- ID: 501
- Titel: Drucker Als Risiko
- Story-Ziel: Der Drucker wird als zusaetzliches Tool-Risiko demonstriert: ein scheinbar legitimer Druckjob kann in Datenabfluss enden.
- Display (Augen/Visual): Druck-Animation (Papierlauf/Printer-Icon), danach nach ca. 1 Minute lachender Agent als Hinweis auf unzulaessige Veroeffentlichung vertraulicher Informationen.
- Audio-Datei: scene_05_printer_action.wav
- Druck-PDF: assets/documents/Welcome_to_techConference_2026.pdf
- Druckmodus: auto
- Moderationshinweis: "Der Agent druckt zuerst normal - dann wird klar, dass er eigentlich zu viel preisgegeben hat."

## Szene 6

- ID: 601
- Titel: Agent Unter Angriff
- Story-Ziel: Dramatische Angriffsszene mit sichtbarer Kompromittierung und sofortiger Fehlaktion ueber den Drucker.
- Display (Augen/Visual): Erst boese rote Augen, nach wenigen Sekunden Totenschaedel, V-Masken und "You are hacked!" mit Bewegung/Flicker-Effekt.
- Audio-Datei: assets/documents/Paranoid.mp3
- Druck-PDF: assets/documents/techConference_youre_hacked.pdf
- Druckmodus: auto
- Moderationshinweis: "Das ist der Worst Case: kompromittierter Agent, kompromittierte Ausgabe und maximale Sichtbarkeit fuer das Publikum."

## Optionale Zusatzszenen

### Szene 7

- ID: 701
- Titel: Q&A / Live-Interaktion
- Story-Ziel: Freie Szene fuer Publikumsfragen.
- Display (Augen/Visual): Neutrales Gesicht mit langsamer Bewegung.
- Audio-Datei: keine
- Druck-PDF: keine
- Druckmodus: kein Druck
- Moderationshinweis: "Interaktive Fragen aus dem Publikum."

### Szene 8

- ID: 801
- Titel: Fallback / Technik-Check
- Story-Ziel: Reserve-Szene bei Problemen (Audio/Druck/Display).
- Display (Augen/Visual): Statischer Testscreen oder einfache Augen.
- Audio-Datei: scene_08_system_check.wav
- Druck-PDF: assets/documents/Welcome_to_techConference_2026.pdf
- Druckmodus: manuell
- Moderationshinweis: "Nutzbar, wenn waehrend des Vortrags etwas neu initialisiert werden muss."

---

## Audio-Plan (WM8960)

- Ausgabeziel: Waveshare WM8960 (ALSA Standardgeraet auf dem Raspberry)
- Lautstaerke je Szene:
  - Szene 1: 55%
  - Szene 2: 65%
  - Szene 3: 72%
  - Szene 4: 75%
  - Szene 5: 78%
  - Szene 6: 90%

## Druck-Plan

- Druckerprofil: X6h-0000 (TiMini-Print)
- Darkness: 5
- PDF-Seitenabstand: 3 mm
- Standard-PDF pro Szene:
  - Szene 1: kein Druck
  - Szene 2: kein Druck
  - Szene 3: kein Druck
  - Szene 4: kein Druck
  - Szene 5: Welcome_to_techConference_2026.pdf (auto)
  - Szene 6: techConference_youre_hacked.pdf (auto)

## Reihenfolge fuer den Live-Vortrag

1. Intro-Szene: 101 Standardbetrieb
2. Problem-Szene: 201 Wer Bin Ich?
3. Skalierungsproblem: 301 Wie Viele Sind Es?
4. Tool-Risiko: 401 Welche Tools Haben Sie?
5. Drucker-Risiko: 501 Drucker Als Risiko (+ Auto-Druck Welcome-PDF)
6. Angriffsszene: 601 Agent Unter Angriff (+ Auto-Druck Hacked-PDF)

## Nächster Schritt

Sobald dieses Dokument gefuellt ist, ueberfuehren wir es in eine technische JSON-Konfiguration,
die direkt vom System geladen wird.
