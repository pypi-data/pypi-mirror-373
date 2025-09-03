#!/usr/bin/env python3
"""
Test script to verify SimulStreaming integration with WhisperLiveKit.
This tests the basic integration without requiring actual SimulStreaming dependencies.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'whisperlivekit'))

from whisperlivekit.parse_args import parse_args
from whisperlivekit.core import TranscriptionEngine
from whisperlivekit.whisper_streaming_custom.backends import SIMULSTREAMING_AVAILABLE

def test_argument_parsing():
    """Test that SimulStreaming arguments are parsed correctly."""
    print("Testing argument parsing...")
    
    # Mock sys.argv for testing
    import sys
    original_argv = sys.argv
    
    try:
        # Test basic SimulStreaming arguments
        sys.argv = [
            'test_script.py',
            '--backend', 'simulstreaming',
            '--model', 'large-v3',
            '--frame-threshold', '20',
            '--beams', '3',
            '--audio-max-len', '25.0',
            '--init-prompt', 'Technical meeting:',
        ]
        
        args = parse_args()
        
        # Verify arguments were parsed correctly
        assert args.backend == 'simulstreaming'
        assert args.model == 'large-v3'
        assert args.frame_threshold == 20
        assert args.beams == 3
        assert args.audio_max_len == 25.0
        assert args.init_prompt == 'Technical meeting:'
        
        print("✓ Argument parsing test passed")
        
    finally:
        sys.argv = original_argv

def test_backend_availability():
    """Test backend availability detection."""
    print("Testing backend availability...")
    
    print(f"SimulStreaming available: {SIMULSTREAMING_AVAILABLE}")
    
    if SIMULSTREAMING_AVAILABLE:
        print("✓ SimulStreaming dependencies detected")
    else:
        print("⚠ SimulStreaming dependencies not available (this is expected if not installed)")

def test_transcription_engine_config():
    """Test TranscriptionEngine configuration with SimulStreaming parameters."""
    print("Testing TranscriptionEngine configuration...")
    
    config = {
        'backend': 'faster-whisper',  # Use a safe backend for testing
        'model': 'tiny',
        'lan': 'en',
        'frame_threshold': 30,
        'beams': 2,
        'audio_max_len': 20.0,
        'init_prompt': 'Test prompt',
    }
    
    try:
        # Reset the singleton for testing
        TranscriptionEngine._instance = None
        TranscriptionEngine._initialized = False
        
        engine = TranscriptionEngine(**config)
        
        # Verify that SimulStreaming parameters are stored
        assert hasattr(engine.args, 'frame_threshold')
        assert engine.args.frame_threshold == 30
        assert hasattr(engine.args, 'beams')
        assert engine.args.beams == 2
        assert hasattr(engine.args, 'audio_max_len')
        assert engine.args.audio_max_len == 20.0
        assert hasattr(engine.args, 'init_prompt')
        assert engine.args.init_prompt == 'Test prompt'
        
        print("✓ TranscriptionEngine configuration test passed")
        
    except Exception as e:
        print(f"✗ TranscriptionEngine configuration test failed: {e}")
        raise

def test_simulstreaming_backend_import():
    """Test that SimulStreaming backend can be imported without errors."""
    print("Testing SimulStreaming backend import...")
    
    try:
        from whisperlivekit.whisper_streaming_custom.backends import SimulStreamingASR
        from whisperlivekit.whisper_streaming_custom.online_asr import SimulStreamingOnlineProcessor
        
        print("✓ SimulStreaming classes imported successfully")
        
        # Test that we get proper error messages when dependencies are missing
        if not SIMULSTREAMING_AVAILABLE:
            try:
                asr = SimulStreamingASR(lan='en', modelsize='large-v3')
                print("✗ Expected ImportError was not raised")
                assert False, "Should have raised ImportError"
            except ImportError as e:
                print(f"✓ Proper ImportError raised: {e}")
        else:
            print("✓ SimulStreaming dependencies available for full testing")
            
    except Exception as e:
        print(f"✗ SimulStreaming backend import test failed: {e}")
        raise

def test_help_message():
    """Test that help message includes SimulStreaming options."""
    print("Testing help message...")
    
    import sys
    from io import StringIO
    from whisperlivekit.parse_args import parse_args
    
    original_argv = sys.argv
    original_stdout = sys.stdout
    
    try:
        sys.argv = ['test_script.py', '--help']
        sys.stdout = StringIO()
        
        try:
            parse_args()
        except SystemExit:
            pass  # argparse calls sys.exit after showing help
        
        help_output = sys.stdout.getvalue()
        
        # Check that SimulStreaming options are in help
        assert 'simulstreaming' in help_output
        assert 'frame-threshold' in help_output
        assert 'beams' in help_output
        assert 'SimulStreaming arguments' in help_output
        
        print("✓ Help message test passed")
        
    finally:
        sys.argv = original_argv
        sys.stdout = original_stdout

def main():
    """Run all tests."""
    print("=" * 60)
    print("WhisperLiveKit SimulStreaming Integration Test")
    print("=" * 60)
    
    tests = [
        test_argument_parsing,
        test_backend_availability,
        test_transcription_engine_config,
        test_simulstreaming_backend_import,
        test_help_message,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All integration tests passed!")
        print("\nNext steps:")
        print("1. Install SimulStreaming dependencies to enable full functionality")
        print("2. Test with actual audio input")
        print("3. Compare latency vs other backends")
    else:
        print("❌ Some tests failed. Please check the integration.")
        sys.exit(1)

if __name__ == "__main__":
    main()
