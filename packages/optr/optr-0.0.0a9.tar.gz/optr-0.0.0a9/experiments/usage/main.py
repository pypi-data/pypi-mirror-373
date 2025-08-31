# ruff: noqa: E402

import signal
import threading

import gi
import uvicorn

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst
from optr.stream.gstreamer import control

from config import Config
from server import create_app
from simulation import SimulationRunner
from simulation.onnx import OnnxSimulation
from streaming import StreamManager, setup_pipeline

Gst.init(None)

# Global state
sim_runner = None
stream_manager = None
recorder = None
http_server = None
running = False
pipe = None
main_loop = None


def on_bus_message(msg):
    """Handle GStreamer bus messages."""
    global running, main_loop

    t = msg.type
    if t == Gst.MessageType.ERROR:
        err, dbg = msg.parse_error()
        print(f"[ERROR] {err}\n{dbg}")
        running = False
        if main_loop and main_loop.is_running():
            GLib.idle_add(main_loop.quit)
        return False
    elif t == Gst.MessageType.EOS:
        print("[INFO] EOS received, exiting.")
        running = False
        if main_loop and main_loop.is_running():
            GLib.idle_add(main_loop.quit)
        return False
    return True


def push_frame():
    """Request and push a frame from the simulation to the pipeline."""
    global sim_runner, stream_manager, recorder, running

    if not running or not stream_manager or not sim_runner:
        return False

    if not stream_manager.is_running:
        return False

    # Request frame from simulation (non-blocking)
    frame_bytes = sim_runner.request_frame()
    if frame_bytes is None:
        # No frame available, continue timer
        return True

    # Add frame to recorder if recording (non-blocking)
    if recorder:
        recorder.add_frame(frame_bytes)

    # Push frame to stream
    return stream_manager.push_frame(frame_bytes)


def start_http_server(port=8080):
    """Start HTTP server in background thread."""
    global sim_runner, recorder

    print(f"Starting HTTP server on port {port}...")

    # Create app using factory function
    app = create_app(sim_runner, recorder)

    # Run server
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


def handle_sigint(signum, frame):
    """Handle interrupt signal."""
    global running, stream_manager, sim_runner, main_loop

    print("\n[INFO] Ctrl+C -> shutting down...")
    running = False

    if sim_runner:
        sim_runner.stop()

    if stream_manager:
        stream_manager.stop()

    # Quit the main loop to ensure clean shutdown
    if main_loop and main_loop.is_running():
        GLib.idle_add(main_loop.quit)


def cleanup():
    """Clean up all resources."""
    global pipe, sim_runner, stream_manager

    print("Cleaning up...")

    if pipe:
        control.stop(pipe)

    if stream_manager:
        stream_manager.stop()

    if sim_runner:
        sim_runner.close()

    print("✅ Cleanup complete!")


def main():
    """Main entry point."""
    global running, pipe, main_loop, sim_runner, stream_manager, recorder

    # Get configuration with proper priority: args > env > defaults
    config = Config.parse()

    print("🚀 Starting Simulation Server")
    print(f"Resolution: {config.width}x{config.height} @ {config.fps} FPS")
    print(f"Output Mode: {config.output}")
    if config.output == "shm":
        print(f"SHM Socket: {config.shm}")
    else:
        print(f"RTMP URL: {config.rtmp}")
    print(f"Recordings: {config.recordings}")
    print(f"HTTP Port: {config.port}")

    try:
        # Setup simulation
        print("Setting up ONNX simulation...")
        simulation = OnnxSimulation()

        # Setup simulation runner with the simulation
        sim_runner = SimulationRunner(simulation, config.width, config.height)
        sim_runner.setup()

        # Setup streaming pipeline
        pipe, appsrc, recorder, frame_dur = setup_pipeline(
            config.width,
            config.height,
            config.fps,
            config.output,
            config.shm,
            config.rtmp,
            config.recordings,
            on_bus_message,
        )

        # Subscribe to action events for recording
        def on_action_started(data):
            print(f"🚀 Action started: {data['id']}")
            if recorder:
                recorder.start_recording(data["id"])

        def on_action_completed(data):
            print(f"🏁 Action completed: {data['id']}")
            if recorder:
                recorder.stop_recording(data["id"])

        sim_runner.on("action_started", on_action_started)
        sim_runner.on("action_completed", on_action_completed)

        sim_runner.start()  # Start the simulation thread

        # Setup stream manager
        stream_manager = StreamManager(appsrc, frame_dur)

        # Start HTTP server in background
        server_thread = threading.Thread(
            target=start_http_server, args=(config.port,), daemon=True
        )
        server_thread.start()

        # Setup signal handler
        signal.signal(signal.SIGINT, handle_sigint)

        # Start pipeline
        running = True
        control.play(pipe)

        # Setup frame pushing timer
        GLib.timeout_add(int(1000 / config.fps), push_frame)

        print("\n✅ Server running!")
        print(f"HTTP API: http://localhost:{config.port}")
        print(f"Health check: http://localhost:{config.port}/health")
        print(f"Actions: http://localhost:{config.port}/actions")
        print("\nPress Ctrl+C to stop...\n")

        # Run main loop
        with control.mainloop() as loop:
            main_loop = loop  # Store reference globally
            try:
                main_loop.run()
            except KeyboardInterrupt:
                pass

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        cleanup()


if __name__ == "__main__":
    main()
