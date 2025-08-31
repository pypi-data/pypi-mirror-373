"""Recorder test - clip recording with triggers."""

import numpy as np
import time
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from optr.stream import create_clip_recorder, create_trigger_recorder


def generate_test_frame(width: int = 320, height: int = 240, frame_num: int = 0):
    """Generate a single test frame with animation."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create animated circles
    center_x, center_y = width // 2, height // 2
    t = frame_num / 30.0  # Assume 30fps
    
    # Moving circle
    circle_x = int(center_x + 50 * np.sin(t))
    circle_y = int(center_y + 30 * np.cos(t))
    
    # Draw circle (simple implementation)
    radius = 20
    for y in range(max(0, circle_y - radius), min(height, circle_y + radius)):
        for x in range(max(0, circle_x - radius), min(width, circle_x + radius)):
            if (x - circle_x) ** 2 + (y - circle_y) ** 2 <= radius ** 2:
                frame[y, x] = [255, 100, 100]  # Red circle
    
    # Background gradient
    frame[:, :, 2] = np.linspace(0, 255, height, dtype=np.uint8).reshape(-1, 1)
    frame[:, :, 1] = (frame_num * 2) % 256
    
    return frame


def test_basic_clip_recording():
    """Test basic clip recording functionality."""
    print("=== Basic Clip Recording Test ===")
    
    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Create clip recorder
        recorder = create_clip_recorder(
            str(output_dir), 
            width=320, 
            height=240, 
            fps=30.0,
            duration=2.0  # 2 second clips
        )
        
        print("✓ Recorder created successfully")
        
        # Start recording
        clip_path = recorder.start("test_clip.mp4")
        print(f"Started recording: {clip_path}")
        
        # Generate and record frames
        for i in range(60):  # 2 seconds at 30fps
            frame = generate_test_frame(320, 240, i)
            recorder.write(frame)
            if i % 15 == 0:  # Progress every 0.5 seconds
                print(f"  Recorded frame {i}/60")
        
        # Stop recording
        final_path = recorder.stop()
        print(f"Stopped recording: {final_path}")
        
        # Check if file was created
        if Path(final_path).exists():
            size = Path(final_path).stat().st_size
            print(f"✓ Clip created: {size} bytes")
            success = True
        else:
            print("✗ Clip file not found")
            success = False
        
        # Cleanup
        recorder.close()
        
        return success
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trigger_recording():
    """Test trigger-based recording."""
    print("=== Trigger Recording Test ===")
    
    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Create base recorder
        base_recorder = create_clip_recorder(
            str(output_dir),
            width=320,
            height=240,
            fps=30.0,
            duration=1.5  # 1.5 second clips
        )
        
        # Create trigger function (trigger every 45 frames for 30 frames)
        frame_count = 0
        def trigger_fn():
            nonlocal frame_count
            # Trigger from frame 15-45 and 90-120
            return (15 <= frame_count < 45) or (90 <= frame_count < 120)
        
        # Create trigger recorder
        recorder = create_trigger_recorder(base_recorder, trigger_fn)
        
        print("✓ Trigger recorder created successfully")
        
        # Simulate streaming with trigger
        total_frames = 150
        clips_created = []
        
        for i in range(total_frames):
            frame_count = i
            frame = generate_test_frame(320, 240, i)
            
            was_recording = recorder.is_recording()
            recorder.write(frame)  # This processes the trigger
            is_recording = recorder.is_recording()
            
            # Detect recording state changes
            if not was_recording and is_recording:
                print(f"  Started recording at frame {i}")
            elif was_recording and not is_recording:
                print(f"  Stopped recording at frame {i}")
            
            if i % 30 == 0:  # Progress every second
                print(f"  Processed frame {i}/{total_frames}")
        
        # Check output directory for clips
        clip_files = list(output_dir.glob("clip_*.mp4"))
        print(f"Found {len(clip_files)} clip files:")
        
        success = len(clip_files) >= 2  # Should have at least 2 clips
        for clip_file in clip_files:
            size = clip_file.stat().st_size
            print(f"  {clip_file.name}: {size} bytes")
        
        if success:
            print("✓ Trigger recording created expected clips")
        else:
            print("✗ Expected at least 2 clips from trigger recording")
        
        # Cleanup
        recorder.close()
        
        return success
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Running clip recorder tests...\n")
    
    success1 = test_basic_clip_recording()
    print()
    success2 = test_trigger_recording()
    
    if success1 and success2:
        print("\n✓ All recorder tests passed!")
    else:
        print("\n✗ Some recorder tests failed!")
        sys.exit(1)
