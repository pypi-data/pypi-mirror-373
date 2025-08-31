"""Basic streaming test - simple frame writing."""

import numpy as np
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from optr.stream import create_file_writer, write_frames


def generate_test_frames(width: int = 320, height: int = 240, count: int = 60):
    """Generate simple test frames."""
    print(f"Generating {count} test frames ({width}x{height})")
    
    for i in range(count):
        # Create a simple gradient frame that changes over time
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Red gradient over time
        frame[:, :, 0] = (i * 255 // count)
        
        # Green gradient horizontally  
        frame[:, :, 1] = np.linspace(0, 255, width, dtype=np.uint8)
        
        # Blue gradient vertically
        frame[:, :, 2] = np.linspace(0, 255, height, dtype=np.uint8).reshape(-1, 1)
        
        yield frame


def test_basic_file_writing():
    """Test basic file writing with OpenCV writer."""
    print("=== Basic File Writing Test ===")
    
    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "basic_test.mp4"
    print(f"Writing to: {output_path}")
    
    try:
        # Create file writer
        writer = create_file_writer(str(output_path), 320, 240, fps=30.0)
        
        # Generate and write frames
        frames = generate_test_frames(320, 240, 60)  # 2 seconds at 30fps
        write_frames(writer, frames)
        
        # Cleanup
        writer.close()
        
        print(f"✓ Successfully created: {output_path}")
        print(f"  File size: {output_path.stat().st_size} bytes")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = test_basic_file_writing()
    if success:
        print("\n✓ Basic test passed!")
    else:
        print("\n✗ Basic test failed!")
        sys.exit(1)
