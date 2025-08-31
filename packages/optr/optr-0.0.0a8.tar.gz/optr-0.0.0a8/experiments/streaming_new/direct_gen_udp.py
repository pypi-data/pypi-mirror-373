#!/usr/bin/env python3
import signal
import sys
import numpy as np

import gi
gi.require_version('Gst', '1.0')     # ✅ fix: declare GI version first
from gi.repository import Gst, GLib

# ---------- Config ----------
WIDTH, HEIGHT = 640, 360
FPS = 30
OUT_MP4 = "output.mp4"
UDP_HOST = "127.0.0.1"
UDP_PORT = 5000
BITRATE_KBPS = 1500

# ---------- Init ----------
Gst.init(None)

PIPELINE = f"""
appsrc name=src is-live=true block=true format=time
       caps=video/x-raw,format=RGB,width={WIDTH},height={HEIGHT},framerate={FPS}/1 !
videoconvert !
queue !
tee name=t
  t. ! queue !
      x264enc tune=zerolatency speed-preset=ultrafast bitrate={BITRATE_KBPS} key-int-max={FPS} !
      h264parse !
      mp4mux faststart=true !
      filesink location={OUT_MP4}
  t. ! queue !
      x264enc tune=zerolatency speed-preset=ultrafast bitrate={BITRATE_KBPS} key-int-max={FPS} !
      h264parse !
      rtph264pay pt=96 config-interval=1 !
      udpsink host={UDP_HOST} port={UDP_PORT} sync=false async=false
"""

pipeline = Gst.parse_launch(PIPELINE)
appsrc = pipeline.get_by_name("src")
bus = pipeline.get_bus()
bus.add_signal_watch()

loop = GLib.MainLoop()
running = True
ts_ns = 0
frame_dur = int(Gst.SECOND // FPS)
frame_idx = 0

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
    buf = Gst.Buffer.new_allocate(None, len(data), None)
    buf.fill(0, data)
    buf.pts = ts_ns
    buf.dts = ts_ns
    buf.duration = frame_dur
    ts_ns += frame_dur
    frame_idx += 1

    ret = appsrc.emit("push-buffer", buf)
    if ret != Gst.FlowReturn.OK:
        print(f"[WARN] push-buffer returned {ret}, sending EOS...")
        appsrc.emit("end-of-stream")                 # ✅ fix: use emit
        return False
    return True

def on_bus_message(bus, msg):
    t = msg.type
    if t == Gst.MessageType.ERROR:
        err, dbg = msg.parse_error()
        print(f"[ERROR] {err}\n{dbg}")
        try:
            loop.quit()
        except Exception:
            pass
    elif t == Gst.MessageType.EOS:
        print("[INFO] EOS received, exiting.")
        try:
            loop.quit()
        except Exception:
            pass

bus.connect("message", on_bus_message)

def handle_sigint(signum, frame):
    global running
    print("\n[INFO] Ctrl+C -> sending EOS (finalizes MP4).")
    running = False
    appsrc.emit("end-of-stream")                      # ✅ fix: use emit

signal.signal(signal.SIGINT, handle_sigint)

# ---------- Run ----------
pipeline.set_state(Gst.State.PLAYING)
GLib.timeout_add(int(1000 / FPS), push_frame)
try:
    loop.run()
finally:
    pipeline.set_state(Gst.State.NULL)
