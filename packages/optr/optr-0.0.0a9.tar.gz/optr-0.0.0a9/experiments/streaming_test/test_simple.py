"""Simple test without OpenCV dependency - tests core functionality."""

import numpy as np
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Test only the core components without OpenCV
from optr.stream.buffer.shared import create_shared_buffer
from optr.stream.writer.ffmpeg import create_ffmpeg_writer


def generate_test_frame(width: int = 320, height: int = 240, frame_num: int = 0):
    """Generate a simple test frame."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Simple gradient pattern
    frame[:, :, 0] = (frame_num * 4) % 256  # Red changes over time
    frame[:, :, 1] = np.linspace(0, 255, width, dtype=np.uint8)  # Green gradient
    frame[:, :, 2] = np.linspace(0, 255, height, dtype=np.uint8).reshape(-1, 1)  # Blue gradient
    
    return frame


def test_buffer_only():
    """Test shared memory buffer without OpenCV."""
    print("=== Buffer Only Test ===")
    
    width, height = 320, 240
    # Use /tmp for macOS compatibility instead of /dev/shm
    buffer_path = "/tmp/simple_test"
    
    try:
        # Create buffer
        buffer = create_shared_buffer(buffer_path, width, height)
        print("✓ Buffer created")
        
        # Write a frame
        frame = generate_test_frame(width, height, 42)
        buffer.write(frame)
        print("✓ Frame written")
        
        # Read it back
        read_frame = buffer.read()
        if read_frame is not None and np.array_equal(frame, read_frame):
            print("✓ Frame read back correctly")
            success = True
        else:
            print("✗ Frame mismatch")
            success = False
        
        # Cleanup
        buffer.close()
        print("✓ Buffer cleaned up")
        
        return success
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ffmpeg_writer():
    """Test FFmpeg writer without OpenCV."""
    print("=== FFmpeg Writer Test ===")
    
    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "simple_ffmpeg.mp4"
    
    try:
        # Create FFmpeg writer
        writer = create_ffmpeg_writer(320, 240, 30.0, str(output_path))
        print("✓ FFmpeg writer created")
        
        # Write some frames
        for i in range(30):  # 1 second at 30fps
            frame = generate_test_frame(320, 240, i)
            writer.write(frame)
        
        print("✓ Frames written")
        
        # Close writer
        writer.close()
        print("✓ Writer closed")
        
        # Check if file exists
        if output_path.exists():
            size = output_path.stat().st_size
            print(f"✓ Output file created: {size} bytes")
            return True
        else:
            print("✗ Output file not found")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Simple Streaming Test (No OpenCV)\n")
    
    success1 = test_buffer_only()
    print()
    success2 = test_ffmpeg_writer()
    
    if success1 and success2:
        print("\n✓ Simple tests passed!")
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)
