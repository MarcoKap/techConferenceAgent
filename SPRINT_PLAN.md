# ⚡ SPRINT: Hybrid Photorealistic Face - 24h Lieferung

## 🎯 Ziel bis Morgen
- ✅ Halbwegs realistische 2D Augen + Mund (lokal)
- ✅ Audio-Sync für Ippenbewegungen
- ✅ Video-KI Vorrendering Setup (cachen)
- ✅ Integration & Tests

## 📅 Timeline: ~12h intensive Arbeit

### Phase 1: Assets Quick-Start (2h)
```
□ Einfache aber realistische Eye-Assets (3 Blinkstates statt 5)
□ Mund-Assets (8 Phoneme: neutral, a, e, i, o, u, m, s)
□ Verwende hochwertige Stock-Fotos oder AI-generiert
□ PNG mit Transparenz, Größe: 250x150px (eyes), 180x90px (mouth)
```

### Phase 2: Simplified Renderer (4h)
```
□ PhotorealisticFaceRenderer (simplified)
  - Eye blinking (einfache 3-state interpolation)
  - Mouth phoneme switching
  - Emotion-based variations
□ BlinkingController (4 basic patterns)
□ Audio → Phoneme Converter (librosa)
□ NO complex asset loading, keep it simple
```

### Phase 3: Audio Sync (2h)
```
□ librosa für Audio-Analyse
□ Einfache Frequency-basierte Phoneme-Erkennung
□ Mouth-Animation synchronized mit Audio
□ Phoneme: A (0-500Hz), E (500-1k), I (1k-2k), O (2k-3k), U (3k-4k), etc.
```

### Phase 4: Video-KI Prerendering (2h)
```
□ D-ID API Setup (oder HeyGen als Fallback)
□ Script zum Vorrendern von Szenen-Videos
□ Caching-System (videos/cache/)
□ Integration in Scene Manager
□ Video-Playback in pygame (ffmpeg-python oder opencv)
```

### Phase 5: Integration & Tests (2h)
```
□ Scene Manager update
□ Test alle Kombinationen
□ Performance-Check
□ Deploy ready
```

---

## 🔧 Technologie-Stack (minimal)

```
pygame       - Graphics
librosa      - Audio analysis
opencv-python - Video playback
requests     - D-ID API calls
ffmpeg       - Video processing
```

---

## 📊 Asset-Requirements

### Minimal Set (Um schnell zu sein):
- 3 Eye images (normal, happy, sad) × 3 blink states = 9 images
- 8 Mouth phonemes (neutral, a, e, i, o, u, m, s) = 8 images
- 2 Avatar images (für Video-KI) = 2 images

**Total: ~19 Images zum Sammeln/Erstellen**

---

## 💨 Pragmatische Shortcuts

1. **Keine komplexe Asset-Interpolation** - einfaches Blending
2. **3 Blink-States statt 5** - schneller zu sammeln
3. **Einfache Audio-Analyse** - keine ML-Modelle
4. **Caching statt Live-Generation** - Videos vorrendern lassen
5. **Minimal UI** - alles via Code-Config

---

## 🚀 Start jetzt!

Ready? Ich starte mit Phase 1!
