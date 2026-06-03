"""
Quick asset generator - creates placeholder face assets for testing.
"""

import pygame
import os
from pathlib import Path


def generate_test_eyes():
    """Generate placeholder eye images for all emotions/blink states."""
    pygame.init()
    
    eyes_dir = Path('assets/faces/eyes')
    eyes_dir.mkdir(parents=True, exist_ok=True)
    
    emotions = ['neutral', 'happy', 'sad', 'angry', 'focused', 'tired']
    blink_states = ['open', 'mid', 'closed']
    
    eye_colors = {
        'neutral': (70, 120, 180),    # Blue
        'happy': (100, 140, 200),     # Brighter blue
        'sad': (60, 100, 150),        # Darker blue
        'angry': (150, 80, 80),       # Reddish
        'focused': (80, 130, 200),    # Deep blue
        'tired': (100, 110, 130),     # Grayish
    }
    
    for emotion in emotions:
        for blink_state in blink_states:
            surface = pygame.Surface((250, 150), pygame.SRCALPHA)
            
            # Fill with skin tone
            surface.fill((220, 180, 160, 0))
            
            # Center positions for both eyes
            for eye_x in [65, 185]:
                center = (eye_x, 75)
                
                # Sclera (white)
                pygame.draw.ellipse(surface, (250, 248, 245), 
                                  (center[0]-45, center[1]-35, 90, 70))
                
                # Iris
                iris_color = eye_colors.get(emotion, (70, 120, 180))
                iris_scale = {
                    'open': 1.0,
                    'mid': 0.6,
                    'closed': 0.1
                }.get(blink_state, 1.0)
                
                iris_w = int(40 * iris_scale)
                iris_h = int(35 * iris_scale)
                
                if iris_h > 0 and iris_w > 0:
                    pygame.draw.ellipse(surface, iris_color,
                                      (center[0]-iris_w//2, center[1]-iris_h//2, 
                                       iris_w, iris_h))
                    
                    # Pupil
                    pupil_scale = {
                        'open': 0.45,
                        'mid': 0.35,
                        'closed': 0.0
                    }.get(blink_state, 0.45)
                    
                    pupil_r = max(1, int(20 * pupil_scale))
                    pygame.draw.circle(surface, (10, 10, 10), center, pupil_r)
                    
                    # Highlight (only visible when open)
                    if blink_state == 'open':
                        pygame.draw.circle(surface, (255, 255, 255), 
                                        (center[0]-10, center[1]-12), 6)
            
            # Eyelid shadows for mood
            if emotion == 'sad':
                pygame.draw.line(surface, (100, 80, 80), (30, 50), (220, 50), 2)
                pygame.draw.line(surface, (100, 80, 80), (30, 100), (220, 100), 2)
            elif emotion == 'angry':
                pygame.draw.line(surface, (150, 80, 80), (30, 40), (100, 55), 3)
                pygame.draw.line(surface, (150, 80, 80), (150, 55), (220, 40), 3)
            
            # Save
            filename = eyes_dir / f"{emotion}_{blink_state}.png"
            pygame.image.save(surface, filename)
            print(f"✓ Generated {filename.name}")


def generate_test_mouths():
    """Generate placeholder mouth images for phonemes."""
    pygame.init()
    
    mouth_dir = Path('assets/faces/mouth')
    mouth_dir.mkdir(parents=True, exist_ok=True)
    
    phonemes = ['neutral', 'a', 'e', 'i', 'o', 'u', 'm', 's']
    
    # Mouth shapes for different phonemes
    mouth_shapes = {
        'neutral': {'width': 100, 'height': 20, 'color': (180, 100, 100)},
        'a': {'width': 90, 'height': 45, 'color': (200, 110, 110)},
        'e': {'width': 95, 'height': 30, 'color': (190, 105, 105)},
        'i': {'width': 40, 'height': 35, 'color': (200, 110, 110)},
        'o': {'width': 50, 'height': 50, 'color': (190, 105, 105)},
        'u': {'width': 70, 'height': 40, 'color': (195, 108, 108)},
        'm': {'width': 110, 'height': 25, 'color': (185, 102, 102)},
        's': {'width': 80, 'height': 28, 'color': (190, 105, 105)},
    }
    
    for phoneme in phonemes:
        surface = pygame.Surface((180, 90), pygame.SRCALPHA)
        
        shape = mouth_shapes.get(phoneme, mouth_shapes['neutral'])
        center_x, center_y = 90, 45
        
        # Draw outer lip
        pygame.draw.ellipse(surface, shape['color'],
                          (center_x - shape['width']//2, 
                           center_y - shape['height']//2,
                           shape['width'], shape['height']))
        
        # Draw inner mouth (darker)
        inner_h = max(2, shape['height'] - 8)
        pygame.draw.ellipse(surface, (160, 80, 80),
                          (center_x - (shape['width']-10)//2,
                           center_y - inner_h//2,
                           shape['width']-10, inner_h))
        
        # Mouth outline
        pygame.draw.ellipse(surface, (140, 60, 60),
                          (center_x - shape['width']//2,
                           center_y - shape['height']//2,
                           shape['width'], shape['height']), 2)
        
        filename = mouth_dir / f"{phoneme}.png"
        pygame.image.save(surface, filename)
        print(f"✓ Generated {filename.name}")


if __name__ == '__main__':
    print("Generating test face assets...")
    generate_test_eyes()
    print()
    generate_test_mouths()
    print("\n✅ Test assets ready in assets/faces/")
