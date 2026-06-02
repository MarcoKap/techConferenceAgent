#!/usr/bin/env python3
"""Preview the new 3D eyes with different configurations."""

import sys
import math
import pygame
from dataclasses import dataclass

from display.eye_renderer import EyeRenderer
from config import BACKGROUND_COLOR


@dataclass
class DisplayConfig:
    """Simplified display config for testing."""
    eye_color: tuple
    eye_shape: str  # "normal", "wide", "angry", "narrow", "x"
    pupil_animation: str  # "still", "wander", "jitter", "idle", "glow"


def run_preview():
    """Display 3D eyes with different styles."""
    pygame.init()
    
    # Screen
    width, height = 1280, 960
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("3D Eyes Preview - Phase 1")
    clock = pygame.time.Clock()
    
    renderer = EyeRenderer(width, height)
    
    # Test configurations
    configs = [
        ("Blue Neutral", DisplayConfig((0, 150, 255), "normal", "wander")),
        ("Green Wide", DisplayConfig((100, 200, 100), "wide", "idle")),
        ("Red Angry", DisplayConfig((255, 100, 100), "angry", "jitter")),
        ("Yellow Glow", DisplayConfig((255, 200, 50), "normal", "glow")),
    ]
    
    config_idx = 0
    t = 0.0
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_LEFT:
                    config_idx = (config_idx - 1) % len(configs)
                elif event.key == pygame.K_RIGHT:
                    config_idx = (config_idx + 1) % len(configs)
        
        # Clear background
        screen.fill(BACKGROUND_COLOR)
        
        # Get current config
        name, cfg = configs[config_idx]
        
        # Render eyes
        renderer.draw(screen, cfg, t)
        
        # Draw info
        font = pygame.font.Font(None, 36)
        info_text = f"{name} | Eye: {cfg.eye_shape} | Anim: {cfg.pupil_animation} | [← →] to switch | [ESC] to quit"
        text_surface = font.render(info_text, True, (200, 200, 200))
        screen.blit(text_surface, (10, 10))
        
        # Update time
        t += 0.016  # ~60 FPS
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    run_preview()
