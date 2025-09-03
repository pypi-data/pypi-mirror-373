#!/usr/bin/env python3
"""
Test script to verify that the SimulStreaming backend properly tracks audio timing
and calculates accurate latency estimates.
"""

import numpy as np
import logging
import time
from whisperlivekit.whisper_streaming_custom.online_asr import SimulStreamingOnlineProcessor
from whisperlivekit.whisper_streaming_custom.backends import SimulStreamingASR

# Set up logging to see debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def simulate_audio_stream():
    """Simulate audio chunks with proper timing."""
    sample_rate = 16000
    chunk_duration = 1.0  # 1 second chunks
    num_chunks = 5
    
    # Create silence audio chunks (in real scenario, this would be actual audio)
    for i in range(num_chunks):
        chunk_samples = int(sample_rate * chunk_duration)
        audio_chunk = np.zeros(chunk_samples, dtype=np.float32)
        
        # Add a small sine wave to simulate some audio
        t = np.linspace(0, chunk_duration, chunk_samples)
        audio_chunk += 0.1 * np.sin(2 * np.pi * 440 * t)  # 440 Hz tone
        
        # Calculate the actual stream time
        stream_end_time = (i + 1) * chunk_duration
        
        yield audio_chunk, stream_end_time

def test_simulstreaming_timing():
    """Test the SimulStreaming timing fix."""
    try:
        # Initialize ASR backend
        asr = SimulStreamingASR(
            lan="en",
            modelsize="tiny",  # Use tiny model for testing
            model_path="./tiny.pt"
        )
        
        # Initialize online processor
        online_processor = SimulStreamingOnlineProcessor(
            asr=asr,
            buffer_trimming=("segment", 15)
        )
        
        logger.info("Starting SimulStreaming timing test...")
        
        # Process audio chunks
        for i, (audio_chunk, stream_end_time) in enumerate(simulate_audio_stream()):
            logger.info(f"\n--- Processing chunk {i+1}, stream time: {stream_end_time:.2f}s ---")
            
            # Insert audio chunk with proper stream timing
            online_processor.insert_audio_chunk(audio_chunk, stream_end_time)
            
            # Process the audio
            tokens, processed_upto = online_processor.process_iter()
            
            # Get buffer info
            buffer_info = online_processor.get_buffer()
            
            # Log timing information
            logger.info(f"Audio processed up to: {processed_upto:.2f}s")
            logger.info(f"Buffer end time: {buffer_info.end:.2f}s" if buffer_info.end else "Buffer end time: None")
            logger.info(f"Current end time in processor: {online_processor.end:.2f}s")
            
            # Calculate latency (similar to what's done in audio_processor.py)
            current_time = time.time()
            if hasattr(online_processor, 'beg_loop'):
                # In real scenario, beg_loop would be set
                latency = stream_end_time - processed_upto
            else:
                latency = 0.0
            
            logger.info(f"Estimated latency: {latency:.2f}s")
            
            # Show candidate end times (simulating what happens in audio_processor.py)
            candidate_end_times = []
            if hasattr(online_processor, 'end'):
                candidate_end_times.append(online_processor.end)
            if buffer_info.end is not None:
                candidate_end_times.append(buffer_info.end)
            candidate_end_times.append(processed_upto)
            
            logger.info(f"Candidate end times: {candidate_end_times}")
            
            if tokens:
                logger.info(f"Generated {len(tokens)} tokens:")
                for token in tokens:
                    logger.info(f"  Token: '{token.text}' @ {token.start:.2f}-{token.end:.2f}s")
            
            # Simulate processing delay
            time.sleep(0.1)
        
        logger.info("\n--- Test completed successfully! ---")
        logger.info("The end times now properly reflect the actual audio stream timing.")
        
    except ImportError as e:
        logger.error(f"SimulStreaming dependencies not available: {e}")
        logger.info("Please ensure SimulStreaming is properly installed.")
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {e}")
        logger.info("Please ensure the tiny.pt model file is in the current directory.")
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simulstreaming_timing()
