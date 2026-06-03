#!/usr/bin/env python3
"""Live test preview for photorealistic face rendering."""

import pygame
import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'display'))
from photorealistic_face_renderer import create_face_renderer


def main():
    pygame.init()
    
    WIDTH, HEIGHT = 1000, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🎭 Photorealistic Face - Live Test")
    clock = pygame.time.Clock()
    
    renderer = create_face_renderer(width=400, height=200)
    
    emotion = 'neutral'
    emotions = ['neutral', 'happy', 'sad', 'angry', 'focused', 'tired']
    emotion_idx = 0
    time_elapsed = 0.0
    
    emotions_text = {
        'neutral': "Neutral",
        'happy': "Happy 😊",
        'sad': "Sad 😢",
        'angry': "Angry 😠",
        'focused': "Focused 🎯",
        'tired': "Tired 😴",
    }
    
    font_large = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 32)
    
    print("""
╔════════════════════════════════════════════╗
║  🎭 Photorealistic Face - Live Test       ║
╚════════════════════════════════════════════╝

⌨️  Controls:
  LEFT/RIGHT   - Change emotion
  SPACE        - Reset time
  Q            - Quit
""")
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        time_elapsed += dt
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_LEFT:
                    emotion_idx = (emotion_idx - 1) % len(emotions)
                    emotion = emotions[emotion_idx]
                    print(f"→ {emotions_text[emotion]}")
                elif event.key == pygame.K_RIGHT:
                    emotion_idx = (emotion_idx + 1) % len(emotions)
                    emotion = emotions[emotion_idx]
                    print(f"→ {emotions_text[emotion]}")
                elif event.key == pygame.K_SPACE:
                    time_elapsed = 0.0
        
        screen.fill((40, 40, 50))
        
        # Left face
        face1 = pygame.Surface((400, 200), pygame.SRCALPHA)
        face1.fill((220, 180, 160, 0))
        renderer.render(face1, emotion=emotion, t=time_elapsed,
                       eye_position=(100, 100), mouth_position=(120, 150))
        screen.blit(face1, (50, 100))
        
        # Right face (offset animation)
        face2 = pygame.Surface((400, 200), pygame.SRCALPHA)
        face2.fill((220, 180, 160, 0))
        renderer.render(face2, emotion=emotion, t=time_elapsed + 2.0,
                       eye_position=(100, 100), mouth_position=(120, 150))
        screen.blit(face2, (500, 100))
        
        # UI text
        emotion_text = font_large.render(emotions_text[emotion], True, (255, 255, 255))
        screen.blit(emotion_text, (300, 20))
        
        time_text = font_small.render(f"Time: {time_elapsed:.2f}s", True, (200, 200, 200))
        screen.blit(time_text, (350, 70))
        
        pygame.display.flip()
    
    pygame.quit()
    print("✅ Done!")


if __name__ == '__main__':
    main()
