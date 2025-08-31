"""Buffer test - shared memory buffer read/write."""

import numpy as np
import time
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from optr.stream import create_shared_buffer


def generate_test_frame(width: int = 320, height: int = 240, frame_num: int = 0):
    """Generate a single test frame."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create a pattern that changes with frame number
    t = frame_num / 60.0  # Assume 60fps
    
    # Checkerboard pattern that shifts
    checker_size = 20
    shift = int(t * checker_size) % (checker_size * 2)
    
    for y in range(height):
        for x in range(width):
            checker_x = (x + shift) // checker_size
            checker_y = y // checker_size
            if (checker_x + checker_y) % 2 == 0:
                frame[y, x] = [255, 100, 50]  # Orange
            else:
                frame[y, x] = [50, 100, 255]  # Blue
    
    # Add frame number as a color intensity
    frame[:, :, 1] = np.clip(frame[:, :, 1] + (frame_num % 256), 0, 255)
    
    return frame


def test_shared_memory_buffer():
    """Test shared memory buffer write and read."""
    print("=== Shared Memory Buffer Test ===")
    
    width, height = 320, 240
    buffer_path = "/tmp/test_stream"  # Use /tmp for macOS compatibility
    
    print(f"Creating shared memory buffer at: {buffer_path}")
    print(f"Frame size: {width}x{height}")
    
    try:
        # Create shared memory buffer
        buffer = create_shared_buffer(buffer_path, width, height, channels=3, buffer_count=3)
        
        print("✓ Buffer created successfully")
        
        # Test writing frames
        print("Writing test frames...")
        test_frames = []
        for i in range(5):
            frame = generate_test_frame(width, height, i)
            test_frames.append(frame.copy())
            buffer.write(frame)
            print(f"  Written frame {i}")
            time.sleep(0.1)  # Small delay to simulate real streaming
        
        # Test reading frames back
        print("Reading frames back...")
        read_frames = []
        for i in range(5):
            frame = buffer.read()
            if frame is not None:
                read_frames.append(frame.copy())
                print(f"  Read frame {i}: shape={frame.shape}")
            else:
                print(f"  No frame available at {i}")
        
        # Verify data integrity (check last frame)
        if len(read_frames) > 0 and len(test_frames) > 0:
            last_written = test_frames[-1]
            last_read = read_frames[-1]
            
            if np.array_equal(last_written, last_read):
                print("✓ Data integrity verified - frames match")
                success = True
            else:
                print("✗ Data integrity failed - frames don't match")
                print(f"  Written shape: {last_written.shape}, Read shape: {last_read.shape}")
                success = False
        else:
            print("✗ No frames to compare")
            success = False
        
        # Cleanup
        buffer.close()
        print("✓ Buffer closed and cleaned up")
        
        return success
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_shared_memory_buffer()
    if success:
        print("\n✓ Buffer test passed!")
    else:
        print("\n✗ Buffer test failed!")
        sys.exit(1)
