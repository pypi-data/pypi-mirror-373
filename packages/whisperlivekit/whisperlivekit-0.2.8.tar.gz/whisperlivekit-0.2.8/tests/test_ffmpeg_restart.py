#!/usr/bin/env python3
"""Test script to verify FFmpeg restart functionality."""

import asyncio
import logging
import signal
import subprocess
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def test_ffmpeg_restart():
    """Test the FFmpeg restart functionality."""
    
    from whisperlivekit.ffmpeg_manager import FFmpegManager, FFmpegState
    
    logger.info("--- Test Case 1: External Kill and Restart ---")
    ffmpeg_manager = FFmpegManager(
        sample_rate=16000,
        channels=1,
        max_retries=3,
        restart_delay=2.0,
        process_timeout=30.0  # Short timeout for testing
    )
    
    error_logs = []
    async def error_callback(error_type):
        logger.info(f"FFmpeg error callback: {error_type}")
        error_logs.append(error_type)
    
    ffmpeg_manager.on_error_callback = error_callback
    
    logger.info("Starting FFmpeg manager...")
    success = await ffmpeg_manager.start()
    if not success:
        logger.error("Failed to start FFmpeg manager")
        return

    logger.info("FFmpeg started successfully")
    initial_pid = ffmpeg_manager.process.pid
    logger.info(f"Initial FFmpeg PID: {initial_pid}")

    logger.info("Writing some data...")
    await ffmpeg_manager.write_data(b"test_data_1")
    await asyncio.sleep(1)

    logger.info(f"Killing FFmpeg process with PID {initial_pid}...")
    try:
        subprocess.run(['kill', '-9', str(initial_pid)], check=True)
        logger.info("FFmpeg process killed.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Failed to kill process: {e}")

    logger.info("Waiting for automatic restart...")
    await asyncio.sleep(10)

    state = await ffmpeg_manager.get_state()
    logger.info(f"FFmpeg state after kill: {state}")

    if state == FFmpegState.RUNNING:
        logger.info("SUCCESS: FFmpeg restarted after external kill.")
        new_pid = ffmpeg_manager.process.pid
        logger.info(f"New FFmpeg PID: {new_pid}")
        assert new_pid != initial_pid, "PID should be different after restart"
        assert "process_died" in error_logs, "process_died should be logged"
    else:
        logger.error(f"FAILED: FFmpeg did not restart. State: {state}")

    logger.info("\n--- Test Case 2: Proactive Restart ---")
    logger.info("Waiting for proactive restart (timeout set to 30s)...")
    
    start_time = time.time()
    restarted = False
    while time.time() - start_time < 40:
        if "proactive_restart" in error_logs:
            logger.info("SUCCESS: Proactive restart triggered.")
            restarted = True
            break
        await asyncio.sleep(1)
    
    if not restarted:
        logger.error("FAILED: Proactive restart did not occur within the timeframe.")
    
    # Wait for the restart to complete
    logger.info("Waiting for proactive restart to complete...")
    await asyncio.sleep(5)
    
    state_after_proactive_restart = await ffmpeg_manager.get_state()
    logger.info(f"State after proactive restart test: {state_after_proactive_restart}")
    if state_after_proactive_restart == FFmpegState.RUNNING:
        logger.info("SUCCESS: Proactive restart completed successfully.")
    else:
        logger.error(f"FAILED: Expected RUNNING state, got {state_after_proactive_restart}")

    logger.info("\n--- Test Case 3: Write Data After Restarts ---")
    logger.info("Writing data after all restarts...")
    write_success = await ffmpeg_manager.write_data(b"final_test_data")
    await asyncio.sleep(1)
    if write_success and await ffmpeg_manager.get_state() == FFmpegState.RUNNING:
        logger.info("SUCCESS: Writing data after restarts was successful.")
    else:
        logger.error("FAILED: Could not write data after restarts.")

    logger.info("\nStopping FFmpeg manager...")
    await ffmpeg_manager.stop()
    logger.info("Test completed.")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_ffmpeg_restart())
