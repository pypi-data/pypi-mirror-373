#!/usr/bin/env python3
"""Resilient SHM to UDP consumer with automatic reconnection and composition support."""

import os
import signal
import sys
import time
from pathlib import Path
from typing import List, Optional, Callable
from enum import Enum

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, Gst

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from optr.stream.gstreamer import (
    caps, control, element, pipeline
)
from optr.stream.fps import FPS as FPSType

# Initialize GStreamer
Gst.init(None)


class ConnectionState(Enum):
    """Connection states for the SHM consumer."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class ResilientSHMConsumer:
    """Resilient SHM to UDP consumer with automatic reconnection."""
    
    def __init__(
        self,
        socket_path: str = "/tmp/sim-stream",
        udp_host: str = "127.0.0.1",
        udp_port: int = 5000,
        width: int = 1920,
        height: int = 1080,
        fps: float = 30.0,
        retry_interval: float = 2.0,
        max_retries: int = -1,  # -1 for infinite
        composition_fn: Optional[Callable] = None
    ):
        self.socket_path = socket_path
        self.udp_host = udp_host
        self.udp_port = udp_port
        self.width = width
        self.height = height
        self.fps = fps
        self.retry_interval = retry_interval
        self.max_retries = max_retries
        self.composition_fn = composition_fn
        
        # State management
        self.state = ConnectionState.DISCONNECTED
        self.pipeline = None
        self.loop = None
        self.running = False
        self.retry_count = 0
        self.last_error = None
        
        # Monitoring
        self.frames_received = 0
        self.last_frame_time = 0
        self.watchdog_timeout = 10.0  # seconds
        
    def check_shm_available(self) -> bool:
        """Check if SHM socket is available and readable."""
        try:
            return os.path.exists(self.socket_path) and os.access(self.socket_path, os.R_OK)
        except Exception as e:
            print(f"[DEBUG] SHM check failed: {e}")
            return False
    
    def build_pipeline(self) -> Optional[Gst.Pipeline]:
        """Build the GStreamer pipeline with composition support."""
        try:
            print(f"[INFO] Building pipeline for {self.socket_path}")
            
            # Create video caps for SHM source
            video_caps = caps.raw(
                width=self.width,
                height=self.height,
                fps=FPSType(self.fps),
                format="RGB"
            )
            
            # Create core elements
            shm_src = element.shmsrc(
                socket_path=self.socket_path,
                is_live=True
            )
            
            # Input queue for buffering
            input_queue = element.queue(
                max_size_buffers=50,
                max_size_bytes=0,
                max_size_time=0,
                leaky=2  # Drop old buffers
            )
            
            # Caps filter to ensure proper format
            caps_filter = element.capsfilter(caps=video_caps)
            
            # Video conversion
            convert = element.videoconvert()
            
            # Composition elements (if provided)
            composition_elements = []
            if self.composition_fn:
                composition_elements = self.composition_fn()
            
            # Encoding chain
            encoder = element.x264enc(
                tune="zerolatency",
                speed_preset="ultrafast",
                bitrate=4000,
                key_int_max=int(self.fps)
            )
            
            parser = element.h264parse()
            payloader = element.rtph264pay(pt=96, config_interval=1)
            
            # Output queue
            output_queue = element.queue(
                max_size_buffers=100,
                leaky=2
            )
            
            # UDP sink
            udp_sink = element.udpsink(
                host=self.udp_host,
                port=self.udp_port,
                sync=False,
                async_=False
            )
            
            # Build element chain
            elements = [
                shm_src, input_queue, caps_filter, convert
            ] + composition_elements + [
                encoder, parser, payloader, output_queue, udp_sink
            ]
            
            # Create pipeline
            pipe = pipeline.chain(*elements, name="resilient-shm-consumer")
            
            # Set up message handling
            control.handle_messages(
                pipe,
                self._on_bus_message,
                Gst.MessageType.ERROR | Gst.MessageType.EOS | Gst.MessageType.WARNING
            )
            
            print(f"[INFO] Pipeline built successfully")
            return pipe
            
        except Exception as e:
            print(f"[ERROR] Failed to build pipeline: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _on_bus_message(self, msg) -> bool:
        """Handle GStreamer bus messages."""
        t = msg.type
        
        if t == Gst.MessageType.ERROR:
            err, dbg = msg.parse_error()
            self.last_error = f"{err}: {dbg}"
            print(f"[ERROR] Pipeline error: {self.last_error}")
            self._handle_error()
            return False
            
        elif t == Gst.MessageType.EOS:
            print("[INFO] End of stream received")
            self._handle_disconnect()
            return False
            
        elif t == Gst.MessageType.WARNING:
            warn, dbg = msg.parse_warning()
            print(f"[WARN] Pipeline warning: {warn}: {dbg}")
            
        return True
    
    def _handle_error(self):
        """Handle pipeline errors."""
        self.state = ConnectionState.ERROR
        self._cleanup_pipeline()
        
        if self.running:
            print(f"[INFO] Scheduling reconnection in {self.retry_interval}s...")
            GLib.timeout_add_seconds(int(self.retry_interval), self._attempt_reconnect)
    
    def _handle_disconnect(self):
        """Handle SHM disconnection."""
        print("[INFO] SHM source disconnected")
        self.state = ConnectionState.DISCONNECTED
        self._cleanup_pipeline()
        
        if self.running:
            print(f"[INFO] Scheduling reconnection in {self.retry_interval}s...")
            GLib.timeout_add_seconds(int(self.retry_interval), self._attempt_reconnect)
    
    def _cleanup_pipeline(self):
        """Clean up the current pipeline."""
        if self.pipeline:
            try:
                control.stop(self.pipeline)
                self.pipeline = None
                print("[DEBUG] Pipeline cleaned up")
            except Exception as e:
                print(f"[WARN] Error during pipeline cleanup: {e}")
    
    def _attempt_reconnect(self) -> bool:
        """Attempt to reconnect to SHM source."""
        if not self.running:
            return False  # Stop timeout
        
        # Check retry limit
        if self.max_retries > 0 and self.retry_count >= self.max_retries:
            print(f"[ERROR] Max retries ({self.max_retries}) exceeded, giving up")
            self.running = False
            if self.loop:
                self.loop.quit()
            return False
        
        self.retry_count += 1
        print(f"[INFO] Reconnection attempt {self.retry_count}")
        
        # Check if SHM is available
        if not self.check_shm_available():
            print(f"[DEBUG] SHM not available, retrying in {self.retry_interval}s...")
            return True  # Continue timeout
        
        # Try to connect
        self.state = ConnectionState.CONNECTING
        self.pipeline = self.build_pipeline()
        
        if not self.pipeline:
            print("[ERROR] Failed to build pipeline, retrying...")
            self.state = ConnectionState.ERROR
            return True  # Continue timeout
        
        # Start pipeline
        try:
            control.play(self.pipeline)
            
            # Wait for state change
            ret, current, pending = self.pipeline.get_state(Gst.SECOND * 5)
            
            if current == Gst.State.PLAYING:
                print("[INFO] ✅ Successfully reconnected!")
                self.state = ConnectionState.CONNECTED
                self.retry_count = 0
                self.last_error = None
                
                # Start watchdog
                GLib.timeout_add_seconds(int(self.watchdog_timeout), self._watchdog_check)
                
                return False  # Stop timeout
            else:
                print(f"[ERROR] Pipeline failed to reach PLAYING state: {current}")
                self._cleanup_pipeline()
                self.state = ConnectionState.ERROR
                return True  # Continue timeout
                
        except Exception as e:
            print(f"[ERROR] Failed to start pipeline: {e}")
            self._cleanup_pipeline()
            self.state = ConnectionState.ERROR
            return True  # Continue timeout
    
    def _watchdog_check(self) -> bool:
        """Watchdog to detect stalled pipelines."""
        if not self.running or self.state != ConnectionState.CONNECTED:
            return False  # Stop timeout
        
        current_time = time.time()
        
        # Check if we've received frames recently
        if self.last_frame_time > 0 and (current_time - self.last_frame_time) > self.watchdog_timeout:
            print("[WARN] Watchdog detected stalled pipeline, forcing reconnection")
            self._handle_disconnect()
            return False
        
        return True  # Continue timeout
    
    def _handle_sigint(self, signum, frame):
        """Handle interrupt signal."""
        print(f"\n[INFO] Received signal {signum}, shutting down...")
        self.stop()
    
    def start(self):
        """Start the resilient consumer."""
        if self.running:
            print("[WARN] Consumer already running")
            return
        
        print("🚀 Starting Resilient SHM to UDP Consumer")
        print(f"SHM source: {self.socket_path}")
        print(f"UDP output: {self.udp_host}:{self.udp_port}")
        print(f"Video: {self.width}x{self.height} @ {self.fps} FPS")
        print(f"Retry interval: {self.retry_interval}s")
        print(f"Max retries: {'infinite' if self.max_retries < 0 else self.max_retries}")
        
        self.running = True
        
        # Setup signal handler
        signal.signal(signal.SIGINT, self._handle_sigint)
        signal.signal(signal.SIGTERM, self._handle_sigint)
        
        # Start initial connection attempt
        GLib.timeout_add(100, self._attempt_reconnect)  # Start after 100ms
        
        # Run main loop
        with control.mainloop() as main_loop:
            self.loop = main_loop
            try:
                print("\nPress Ctrl+C to stop...\n")
                main_loop.run()
            finally:
                self._cleanup_pipeline()
    
    def stop(self):
        """Stop the consumer."""
        self.running = False
        if self.loop:
            self.loop.quit()
    
    def get_status(self) -> dict:
        """Get current status information."""
        return {
            "state": self.state.value,
            "retry_count": self.retry_count,
            "last_error": self.last_error,
            "frames_received": self.frames_received,
            "shm_available": self.check_shm_available()
        }


def create_text_overlay_composition():
    """Example composition: Add text overlay."""
    text_overlay = element.create("textoverlay", {
        "text": "Live Stream",
        "valignment": "top",
        "halignment": "left",
        "font-desc": "Sans Bold 24"
    }, None)
    return [text_overlay]


def create_flip_composition():
    """Example composition: Flip video."""
    flip = element.videoflip(method="horizontal-flip")
    return [flip]


def main():
    """Main entry point."""
    # Parse command line arguments
    socket_path = "/tmp/sim-stream"
    udp_host = "127.0.0.1"
    udp_port = 5000
    width = 1920
    height = 1080
    fps = 30.0
    retry_interval = 2.0
    composition = None
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print("Usage: python resilient_shm_consumer.py [socket_path] [udp_host] [udp_port] [composition]")
            print("Defaults: /tmp/sim-stream 127.0.0.1 5000")
            print("Compositions: text, flip, none")
            return
        
        if len(sys.argv) >= 2:
            socket_path = sys.argv[1]
        if len(sys.argv) >= 3:
            udp_host = sys.argv[2]
        if len(sys.argv) >= 4:
            udp_port = int(sys.argv[3])
        if len(sys.argv) >= 5:
            comp_name = sys.argv[4]
            if comp_name == "text":
                composition = create_text_overlay_composition
            elif comp_name == "flip":
                composition = create_flip_composition
    
    # Create consumer
    consumer = ResilientSHMConsumer(
        socket_path=socket_path,
        udp_host=udp_host,
        udp_port=udp_port,
        width=width,
        height=height,
        fps=fps,
        retry_interval=retry_interval,
        composition_fn=composition
    )
    
    try:
        consumer.start()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Consumer finished")


if __name__ == "__main__":
    main()
