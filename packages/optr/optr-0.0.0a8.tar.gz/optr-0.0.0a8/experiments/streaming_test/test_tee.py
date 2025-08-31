"""Tee test - streaming to multiple outputs simultaneously."""

import numpy as np
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from optr.stream import create_sink, tee


def generate_test_frames(width: int = 320, height: int = 240, count: int = 60):
    """Generate simple test frames."""
    print(f"Generating {count} test frames ({width}x{height})")
    
    for i in range(count):
        # Create a colorful frame that changes over time
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Create a moving pattern
        t = i / count
        
        # Red channel: horizontal wave
        x = np.linspace(0, 4 * np.pi, width)
        red_wave = (np.sin(x + t * 2 * np.pi) + 1) * 127.5
        frame[:, :, 0] = red_wave.astype(np.uint8)
        
        # Green channel: vertical wave  
        y = np.linspace(0, 4 * np.pi, height).reshape(-1, 1)
        green_wave = (np.cos(y + t * 2 * np.pi) + 1) * 127.5
        frame[:, :, 1] = green_wave.astype(np.uint8)
        
        # Blue channel: time-based gradient
        frame[:, :, 2] = int(t * 255)
        
        yield frame


def test_tee_multiple_outputs():
    """Test streaming to multiple outputs using tee."""
    print("=== Tee Multiple Outputs Test ===")
    
    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Define multiple output destinations
    outputs = [
        str(output_dir / "tee_output1.mp4"),
        str(output_dir / "tee_output2.mp4"),
        str(output_dir / "tee_ffmpeg.mp4"),
    ]
    
    print(f"Streaming to {len(outputs)} outputs:")
    for output in outputs:
        print(f"  - {output}")
    
    try:
        # Create multiple sinks
        sinks = [
            create_sink(outputs[0], 320, 240, fps=30.0),  # OpenCV writer
            create_sink(outputs[1], 320, 240, fps=30.0, codec="XVID"),  # Different codec
            create_sink(outputs[2], 320, 240, fps=30.0, use_ffmpeg=True),  # FFmpeg writer
        ]
        
        # Generate frames and stream to all sinks
        frames = generate_test_frames(320, 240, 90)  # 3 seconds at 30fps
        tee(frames, sinks)
        
        # Check results
        success = True
        for output in outputs:
            output_path = Path(output)
            if output_path.exists():
                size = output_path.stat().st_size
                print(f"✓ Created: {output_path.name} ({size} bytes)")
            else:
                print(f"✗ Missing: {output_path.name}")
                success = False
        
        return success
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_tee_multiple_outputs()
    if success:
        print("\n✓ Tee test passed!")
    else:
        print("\n✗ Tee test failed!")
        sys.exit(1)
