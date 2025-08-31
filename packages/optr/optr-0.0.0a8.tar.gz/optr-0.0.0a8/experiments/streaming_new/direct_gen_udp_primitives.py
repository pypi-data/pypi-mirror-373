#!/usr/bin/env python3
import signal
import sys
import numpy as np

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, Gst

from optr.stream.gstreamer import (
    buffer, caps, control, element, pipeline
)
from optr.stream.fps import FPS as FPSType

# ---------- Init ----------
Gst.init(None)

# ---------- Config ----------
WIDTH, HEIGHT = 640, 360
FPS = 30
OUT_MP4 = "output.mp4"
UDP_HOST = "127.0.0.1"
UDP_PORT = 5000
BITRATE_KBPS = 1500

# ---------- Global state ----------
running = True
ts_ns = 0
frame_dur = int(1_000_000_000 // FPS)  # nanoseconds per frame
frame_idx = 0
appsrc = None
pipe = None
loop = None

# ---------- Frame generator (safe math) ----------
def make_frame(idx: int) -> bytes:
    # Do arithmetic in uint16 to avoid OverflowError, then modulo 256 → uint8
    x = np.arange(WIDTH, dtype=np.uint16)             # 0..W-1
    y = np.arange(HEIGHT, dtype=np.uint16)            # 0..H-1

    R = (np.tile(x, (HEIGHT, 1)) + (idx * 3)) % 256
    G = (np.tile(y[:, None], (1, WIDTH)) + (idx * 5)) % 256
    B = ((R + G) // 2) % 256

    frame = np.dstack([
        R.astype(np.uint8),
        G.astype(np.uint8),
        B.astype(np.uint8)
    ])                                                # H x W x 3 (RGB)

    return frame.tobytes()

def push_frame():
    global ts_ns, frame_idx, running
    if not running:
        return False  # stop timeout

    data = make_frame(frame_idx)
    ret = buffer.push(appsrc, data, ts_ns, frame_dur)
    
    if ret != Gst.FlowReturn.OK:
        print(f"[WARN] push-buffer returned {ret}, sending EOS...")
        appsrc.emit("end-of-stream")
        return False
    
    ts_ns += frame_dur
    frame_idx += 1
    return True

def on_bus_message(msg):
    t = msg.type
    if t == Gst.MessageType.ERROR:
        err, dbg = msg.parse_error()
        print(f"[ERROR] {err}\n{dbg}")
        try:
            loop.quit()
        except Exception:
            pass
        return False  # Stop watching messages
    elif t == Gst.MessageType.EOS:
        print("[INFO] EOS received, exiting.")
        try:
            loop.quit()
        except Exception:
            pass
        return False  # Stop watching messages
    return True  # Continue watching messages

def handle_sigint(signum, frame):
    global running
    print("\n[INFO] Ctrl+C -> sending EOS (finalizes MP4).")
    running = False
    appsrc.emit("end-of-stream")

def main():
    global appsrc, pipe, loop
    
    # Create video caps
    video_caps = caps.raw(width=WIDTH, height=HEIGHT, fps=FPSType(FPS), format="RGB")
    
    # Create elements
    appsrc = element.appsrc(
        caps=video_caps,
        is_live=True,
        block=True,
        format="time"
    )
    
    convert = element.videoconvert()
    queue1 = element.queue()
    tee = element.tee()
    
    # File branch elements
    file_encoder = element.x264enc(
        tune="zerolatency",
        speed_preset="ultrafast", 
        bitrate=BITRATE_KBPS,
        key_int_max=FPS
    )
    file_parser = element.create("h264parse", None, None)
    file_muxer = element.create("mp4mux", {"faststart": True}, None)
    file_sink = element.create("filesink", {"location": OUT_MP4}, None)
    
    # UDP branch elements  
    udp_encoder = element.x264enc(
        tune="zerolatency",
        speed_preset="ultrafast",
        bitrate=BITRATE_KBPS, 
        key_int_max=FPS
    )
    udp_parser = element.create("h264parse", None, None)
    udp_payloader = element.create("rtph264pay", {"pt": 96, "config-interval": 1}, None)
    udp_sink = element.udpsink(host=UDP_HOST, port=UDP_PORT)
    
    # Create main pipeline with source -> convert -> queue -> tee
    pipe = pipeline.chain(appsrc, convert, queue1, tee, name="dual-output")
    
    # Create branches using the branch utility
    file_branch = [file_encoder, file_parser, file_muxer, file_sink]
    udp_branch = [udp_encoder, udp_parser, udp_payloader, udp_sink]
    
    pipeline.branch(tee, file_branch, udp_branch)
    
    # Set up message handling using control primitives
    control.handle_messages(pipe, on_bus_message, 
                           Gst.MessageType.ERROR | Gst.MessageType.EOS)
    
    # Set up signal handler
    signal.signal(signal.SIGINT, handle_sigint)
    
    # Start pipeline using async control function
    control.play(pipe)
    
    # Set up frame pushing timer
    GLib.timeout_add(int(1000 / FPS), push_frame)
    
    # Run with control primitives
    with control.mainloop() as main_loop:
        loop = main_loop
        try:
            loop.run()
        finally:
            control.stop(pipe)

if __name__ == "__main__":
    main()
