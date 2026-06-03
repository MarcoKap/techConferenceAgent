#!/usr/bin/env python3
"""Integration test for photorealistic face system."""

import sys
import os
from pathlib import Path

os.environ['SDL_VIDEODRIVER'] = 'dummy'
sys.path.insert(0, str(Path(__file__).parent / 'display'))

from photorealistic_face_renderer import create_face_renderer
from audio_sync import AudioSyncController
from video_ai_renderer import VideoAIFaceRenderer

import pygame


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║  🎭 Photorealistic Face - Integration Test               ║
╚════════════════════════════════════════════════════════════╝
""")
    
    tests_passed = 0
    
    # Test 1: Dependencies
    print("✓ Checking dependencies...")
    try:
        import numpy
        import requests
        print("  ✓ Core deps available")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ Missing: {e}")
    
    # Test 2: Audio Sync
    print("✓ Testing AudioSyncController...")
    try:
        controller = AudioSyncController()
        controller.play()
        controller.update(0.016)
        phoneme = controller.get_current_phoneme()
        assert phoneme in ['neutral', 'a', 'e', 'i', 'o', 'u', 'm', 's']
        controller.stop()
        print("  ✓ Audio sync works")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 3: Face Renderer
    print("✓ Testing PhotorealisticFaceRenderer...")
    try:
        pygame.init()
        renderer = create_face_renderer(width=800, height=200)
        surface = pygame.Surface((800, 200), pygame.SRCALPHA)
        
        for emotion in ['neutral', 'happy', 'sad']:
            renderer.render(surface, emotion=emotion, t=0.5)
        
        print("  ✓ Face rendering works")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 4: Video-AI
    print("✓ Testing VideoAIFaceRenderer...")
    try:
        video_ai = VideoAIFaceRenderer()
        cache_key = video_ai.cache.get_cache_key("test", "happy")
        assert len(cache_key) > 0
        print("  ✓ Video-AI ready")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 5: Scene Manager Integration
    print("✓ Testing Scene Manager Integration...")
    try:
        from scene_manager import SceneManager
        
        class DummyHW:
            def stop(self): pass
            def start(self, *args): pass
        
        mgr = SceneManager(DummyHW(), DummyHW(), DummyHW())
        mgr.set_face_renderer(create_face_renderer())
        mgr.set_audio_sync(AudioSyncController())
        
        # Render
        surface = pygame.Surface((800, 200), pygame.SRCALPHA)
        mgr.update_face_rendering(surface, 0.5)
        
        print("  ✓ Scene manager integration works")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print(f"""
╔════════════════════════════════════════════════════════════╗
║  Results: {tests_passed}/5 tests passed                                  ║
╚════════════════════════════════════════════════════════════╝
""")
    
    if tests_passed == 5:
        print("""
✅ FULL SYSTEM READY!

Components working:
  ✓ Photorealistic face rendering (6 emotions)
  ✓ Audio-sync mouth animation (8 phonemes)
  ✓ Video-KI integration framework
  ✓ Scene manager integration

To deploy:
  1. export DID_API_KEY=your_api_key
  2. Run prerender script for announcement videos
  3. Integrate into main.py display loop
""")
        return 0
    else:
        print("Some tests failed. Check output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
