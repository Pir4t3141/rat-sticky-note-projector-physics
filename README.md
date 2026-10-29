# Rat Sticky-Note Projector Physics

🇬🇧 [English](#-english) | 🇩🇪 [Deutsch](#-deutsch)

---

<a name="-english"></a>
# 🇬🇧 English

A physics simulation that is projected onto a wall or screen with a projector. A camera watches the wall and detects **blue sticky notes**. Every note becomes an obstacle, and the falling balls bounce off it.

> **Windows only.** The project uses DirectShow (`CAP_DSHOW`) and `pygrabber` to access the camera.

## What you need

- A Windows PC or laptop with Python 3 installed
- A projector (connected to the PC)
- A USB webcam (or the laptop's built-in camera)
- A white wall or screen
- **Blue** sticky notes (other colors are not detected)

## Setup, step by step

### 1. Download the project

```bash
git clone https://github.com/Pir4t3141/rat-sticky-note-projector-physics.git
cd rat-sticky-note-projector-physics/src
```

### 2. Install the required libraries

```bash
pip install pygame opencv-python numpy pygrabber
```

### 3. Find your camera index

The program needs to know which camera to use. Run:

```bash
python camera_grabber.py
```

It prints a list like this:

```
--- Connected Cameras On Windows 11 ---
Index 0 : Integrated Webcam
Index 1 : USB Camera
```

Remember the number of the camera you want to use (usually the external USB camera).

### 4. Set the camera index in the code

Open `main.py` and go to line 84 (should look like this:)

```python
cam_index = 0
```

Change `0` to the index from step 3, and save the file.

### 5. Set up the projector and camera

1. Connect the projector and set the display mode to **Duplicate** or **Extend** (Windows key + P). Make sure the simulation window ends up on the projector image. The window uses the full resolution of the main display.
2. Point the projector at the wall.
3. Place the camera so that it sees the **entire projected image** plus a bit of margin. It does not have to be exactly in front of the wall, because the calibration corrects the perspective.
4. **Do not move the camera or the projector** after this. Otherwise the notes will be detected in the wrong place.
5. Dim the room a little, but keep it bright enough that the camera clearly sees the blue notes.

### 6. Start the program

```bash
python main.py
```

Two windows open:

- the **Pygame window** (the simulation, shown by the projector). It is plain grey until the calibration is finished.
- the **`res` window** (the camera image, stays on the laptop screen).

### 7. Calibrate (click the 4 corners)

In the `res` window, you see the camera image. Click the **4 corners of the projected image** with the mouse, **in this order**:

1. top left
2. top right
3. bottom right
4. bottom left

Each click shows a red dot. After the 4th click, the console prints `CALIBRATION SUCCESSFUL!` and the simulation starts.

> If you misclick, close the program (ESC) and start again. The calibration cannot be redone while it is running.

### 8. Play

- Stick **blue sticky notes** onto the wall. They show up as transparent green rectangles in the simulation.
- Press **SPACE** to drop a ball. Every press creates one ball.
- Move, add or remove notes while the simulation is running. The obstacles update live.
- Press **ESC** to quit.

## Controls

| Key | Action |
|---|---|
| `SPACE` | Spawn one ball |
| `ESC` | Quit the program |
| Mouse (4 clicks in the `res` window) | Calibration at startup |

## Optional settings (in `main.py`)

| What | Where | Effect |
|---|---|---|
| Camera | `cam_index = 0` | Which camera is used |
| Automatic balls | the line `# spawn_balls(1)` in the main loop | Remove the `#` to spawn a ball every frame (about 60 per second) |
| Ball size | `ball_radius = 10` | Size of the balls |
| Gravity | `gravity = 0.25` | How fast the balls fall |
| Bounciness | `bounciness = 0.85` | How strongly balls bounce (1.0 = perfect bounce) |
| Note color | `lower_blue` / `upper_blue` in `vision_processing_thread` | HSV range that counts as "blue" |

## Troubleshooting

| Problem | Solution |
|---|---|
| The program crashes right at start or the `res` window stays black | Wrong camera index. Run `camera_grabber.py` again and change `cam_index`. Also close other programs that use the camera (Zoom, Teams, ...). |
| `ModuleNotFoundError` | A library is missing. Run the `pip install` command from step 2 again. |
| Notes are not detected | Make sure the notes are **blue**. Improve the lighting, or adjust the HSV range (`lower_blue` / `upper_blue`). |
| Obstacles appear in the wrong place | The calibration was wrong or the camera/projector was moved. Restart and calibrate again, clicking the corners in the correct order. |
| The projected image itself is detected as a note | Make the room darker or the projector less bright, or narrow the HSV range. |
| Nothing happens when pressing SPACE | Click into the Pygame window first so that it has focus. |
| Simulation is on the wrong screen | Check the display settings (Windows key + P) and make the projector the main display. |

## How it works

1. The **camera** continuously records the wall (in a background thread).
2. A second background thread converts the image to HSV, filters for **blue**, and finds the outlines of the notes. Each note becomes a rotated rectangle.
3. The **calibration** (4 clicks) computes a perspective transformation, so that a position in the camera image is converted to the matching position in the projected image.
4. The **physics** (gravity, friction, bouncing off walls and rotated rectangles) runs at 60 FPS in the Pygame window.

---

<a name="-deutsch"></a>
# 🇩🇪 Deutsch

Eine Physiksimulation, die mit einem Beamer auf eine Wand oder Leinwand projiziert wird. Eine Kamera beobachtet die Wand und erkennt **blaue Haftnotizen**. Jede Notiz wird zu einem Hindernis, von dem die herunterfallenden Bälle abprallen.

> **Nur für Windows.** Das Projekt nutzt DirectShow (`CAP_DSHOW`) und `pygrabber`, um auf die Kamera zuzugreifen.

## Was du brauchst

- Einen Windows-PC oder -Laptop mit installiertem Python 3
- Einen Beamer (am PC angeschlossen)
- Eine USB-Webcam (oder die eingebaute Laptop-Kamera)
- Eine weiße Wand oder Leinwand
- **Blaue** Haftnotizen (andere Farben werden nicht erkannt)

## Einrichtung Schritt für Schritt

### 1. Projekt herunterladen

```bash
git clone https://github.com/Pir4t3141/rat-sticky-note-projector-physics.git
cd rat-sticky-note-projector-physics/src
```

### 2. Benötigte Bibliotheken installieren

```bash
pip install pygame opencv-python numpy pygrabber
```

### 3. Kamera-Index herausfinden

Das Programm muss wissen, welche Kamera es benutzen soll. Starte:

```bash
python camera_grabber.py
```

Es gibt eine Liste wie diese aus:

```
--- Connected Cameras On Windows 11 ---
Index 0 : Integrated Webcam
Index 1 : USB Camera
```

Merke dir die Nummer der Kamera, die du verwenden willst (meistens die externe USB-Kamera).

### 4. Kamera-Index im Code eintragen

Öffne `main.py` und gehe zu Zeile 84 (sollte so aussehen:)

```python
cam_index = 0
```

Ändere die `0` auf den Index aus Schritt 3 und speichere die Datei.

### 5. Beamer und Kamera aufbauen

1. Schließe den Beamer an und stelle den Anzeigemodus auf **Duplizieren** oder **Erweitern** (Windows-Taste + P). Achte darauf, dass das Simulationsfenster auf dem Beamerbild erscheint. Das Fenster nutzt die volle Auflösung des Hauptbildschirms.
2. Richte den Beamer auf die Wand aus.
3. Stelle die Kamera so auf, dass sie das **gesamte projizierte Bild** plus etwas Rand sieht. Sie muss nicht genau vor der Wand stehen, weil die Kalibrierung die Perspektive korrigiert.
4. **Bewege danach weder Kamera noch Beamer.** Sonst werden die Notizen an der falschen Stelle erkannt.
5. Dunkle den Raum etwas ab, aber nicht so stark, dass die Kamera die blauen Notizen nicht mehr gut sieht.

### 6. Programm starten

```bash
python main.py
```

Es öffnen sich zwei Fenster:

- das **Pygame-Fenster** (die Simulation, wird vom Beamer gezeigt). Es ist grau, bis die Kalibrierung abgeschlossen ist.
- das **`res`-Fenster** (das Kamerabild, bleibt auf dem Laptop-Bildschirm).

### 7. Kalibrieren (4 Ecken anklicken)

Im `res`-Fenster siehst du das Kamerabild. Klicke mit der Maus die **4 Ecken des projizierten Bildes** an, und zwar **in dieser Reihenfolge**:

1. oben links
2. oben rechts
3. unten rechts
4. unten links

Jeder Klick zeigt einen roten Punkt. Nach dem 4. Klick steht in der Konsole `CALIBRATION SUCCESSFUL!` und die Simulation startet.

> Bei einem Fehlklick das Programm mit ESC beenden und neu starten. Die Kalibrierung kann während des Betriebs nicht wiederholt werden.

### 8. Spielen

- Klebe **blaue Haftnotizen** an die Wand. In der Simulation erscheinen sie als transparente grüne Rechtecke.
- Drücke **LEERTASTE**, um einen Ball fallen zu lassen. Jeder Druck erzeugt einen Ball.
- Du kannst Notizen während der Simulation verschieben, hinzufügen oder entfernen. Die Hindernisse werden live aktualisiert.
- Drücke **ESC**, um das Programm zu beenden.

## Steuerung

| Taste | Aktion |
|---|---|
| `LEERTASTE` | Einen Ball erzeugen |
| `ESC` | Programm beenden |
| Maus (4 Klicks im `res`-Fenster) | Kalibrierung beim Start |

## Optionale Einstellungen (in `main.py`)

| Was | Wo | Wirkung |
|---|---|---|
| Kamera | `cam_index = 0` | Welche Kamera benutzt wird |
| Automatische Bälle | die Zeile `# spawn_balls(1)` in der Hauptschleife | `#` entfernen, um in jedem Frame einen Ball zu erzeugen (ca. 60 pro Sekunde) |
| Ballgröße | `ball_radius = 10` | Größe der Bälle |
| Schwerkraft | `gravity = 0.25` | Wie schnell die Bälle fallen |
| Elastizität | `bounciness = 0.85` | Wie stark die Bälle abprallen (1.0 = perfekter Abprall) |
| Notizfarbe | `lower_blue` / `upper_blue` in `vision_processing_thread` | HSV-Bereich, der als „blau“ gilt |

## Fehlerbehebung

| Problem | Lösung |
|---|---|
| Das Programm stürzt direkt beim Start ab oder das `res`-Fenster bleibt schwarz | Falscher Kamera-Index. `camera_grabber.py` erneut ausführen und `cam_index` ändern. Außerdem andere Programme schließen, die die Kamera nutzen (Zoom, Teams, ...). |
| `ModuleNotFoundError` | Eine Bibliothek fehlt. Den `pip install`-Befehl aus Schritt 2 erneut ausführen. |
| Notizen werden nicht erkannt | Prüfen, ob die Notizen **blau** sind. Beleuchtung verbessern oder den HSV-Bereich (`lower_blue` / `upper_blue`) anpassen. |
| Hindernisse erscheinen an der falschen Stelle | Die Kalibrierung war falsch oder Kamera/Beamer wurden bewegt. Neu starten und neu kalibrieren, dabei die Ecken in der richtigen Reihenfolge anklicken. |
| Das projizierte Bild selbst wird als Notiz erkannt | Den Raum abdunkeln oder den Beamer weniger hell stellen, oder den HSV-Bereich enger einstellen. |
| Beim Drücken der Leertaste passiert nichts | Zuerst in das Pygame-Fenster klicken, damit es den Fokus hat. |
| Simulation läuft auf dem falschen Bildschirm | Anzeigeeinstellungen prüfen (Windows-Taste + P) und den Beamer als Hauptbildschirm festlegen. |

## So funktioniert es

1. Die **Kamera** nimmt die Wand laufend auf (in einem Hintergrund-Thread).
2. Ein zweiter Hintergrund-Thread wandelt das Bild in HSV um, filtert nach **Blau** und findet die Umrisse der Notizen. Jede Notiz wird zu einem gedrehten Rechteck.
3. Die **Kalibrierung** (4 Klicks) berechnet eine Perspektiv-Transformation, damit eine Position im Kamerabild in die passende Position im projizierten Bild umgerechnet wird.
4. Die **Physik** (Schwerkraft, Reibung, Abprallen an Wänden und gedrehten Rechtecken) läuft mit 60 FPS im Pygame-Fenster.