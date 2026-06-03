#!/usr/bin/env python3
"""Headless test - validate face rendering."""

import sys
from pathlib import Path
import os

os.environ['SDL_VIDEODRIVER'] = 'dummy'

sys.path.insert(0, str(Path(__file__).parent / 'display'))
from photorealistic_face_renderer import create_face_renderer, BlinkingController, EyeAssetsManager, MouthAssetsManager

import pygame


def main():
    print("""
╔════════════════════════════════════════════╗
║  🧪 Photorealistic Face Test Suite        ║
╚════════════════════════════════════════════╝
""")
    
    try:
        # Test 1: Asset directory
        print("✓ Checking assets...")
        assets_dir = Path('assets/faces')
        eyes_count = len(list((assets_dir / 'eyes').glob('*.png')))
        mouth_count = len(list((assets_dir / 'mouth').glob('*.png')))
        assert eyes_count >= 18, f"Need 18 eye images, found {eyes_count}"
        assert mouth_count >= 8, f"Need 8 mouth images, found {mouth_count}"
        print(f"  ✓ Assets: {eyes_count} eyes, {mouth_count} mouths")
        
        # Test 2: Blinking controller
        print("✓ Testing BlinkingController...")
        controller = BlinkingController()
        for emotion in ['neutral', 'happy', 'sad', 'angry', 'focused', 'tired']:
            openness = controller.get_eyelid_openness(emotion, 0.5)
            dilation = controller.get_pupil_dilation(emotion)
            assert 0.0 <= openness <= 1.0
            assert 0.8 <= dilation <= 1.2
        print("  ✓ All emotions work")
        
        # Test 3: Asset managers
        print("✓ Testing Asset Managers...")
        eye_mgr = EyeAssetsManager()
        mouth_mgr = MouthAssetsManager()
        
        eye = eye_mgr.blend_eyes('happy', 0.8)
        assert eye.get_size() == (250, 150)
        print("  ✓ Eye rendering works")
        
        mouth = mouth_mgr.load_mouth('a')
        assert mouth.get_size() == (180, 90)
        print("  ✓ Mouth rendering works")
        
        # Test 4: Face renderer
        print("✓ Testing Face Renderer...")
        pygame.init()
        renderer = create_face_renderer(width=800, height=200)
        surface = pygame.Surface((800, 200), pygame.SRCALPHA)
        
        for emotion in ['neutral', 'happy', 'sad']:
            for t in [0.0, 0.5, 1.0]:
                renderer.render(surface, emotion=emotion, t=t)
        print("  ✓ Rendering works for all emotions")
        
        print("""
╔════════════════════════════════════════════╗
║  ✅ ALL TESTS PASSED!                     ║
╚════════════════════════════════════════════╝

System ready for:
  • Audio synchronization
  • Video-KI integration
  • Scene manager integration
""")
        return 0
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
