import os
import threading
import time

import gi

gi.require_version("Gst", "1.0")
gi.require_version("GObject", "2.0")
from gi.repository import GObject, Gst

Gst.init(None)

pipeline = Gst.Pipeline.new("mixer")

comp = Gst.ElementFactory.make("compositor", "comp")
enc = Gst.ElementFactory.make("x264enc")
enc.set_property("tune", "zerolatency")
enc.set_property("speed-preset", "ultrafast")
enc.set_property("bitrate", 4500)
enc.set_property("key-int-max", 60)
h264p = Gst.ElementFactory.make("h264parse")
mux = Gst.ElementFactory.make("flvmux")
mux.set_property("streamable", True)
sink = Gst.ElementFactory.make("rtmpsink")
sink.set_property("location", "rtmps://live.cloudflare.com:443/live/<your-key>")
for e in (comp, enc, h264p, mux, sink):
    pipeline.add(e)
Gst.Element.link_many(comp, enc, h264p, mux, sink)

sources = {}  # sock_path -> {'bin', 'pad'}


def make_source_bin(sock_path, w, h, xpos, ypos, alpha=1.0):
    bin_ = Gst.Bin.new(os.path.basename(sock_path))

    # live src
    shms = Gst.ElementFactory.make("shmsrc")
    shms.set_property("socket-path", sock_path)
    shms.set_property("is-live", True)
    shms.set_property("do-timestamp", True)
    conv = Gst.ElementFactory.make("videoconvert")
    scale = Gst.ElementFactory.make("videoscale")
    livef = Gst.ElementFactory.make("capsfilter")
    livef.set_property(
        "caps",
        Gst.Caps.from_string(
            f"video/x-raw,format=RGBA,width={w},height={h},framerate=30/1"
        ),
    )

    # fallback to black when live is absent
    fs = Gst.ElementFactory.make("fallbackswitch")  # selects first active input
    black = Gst.ElementFactory.make("videotestsrc")
    black.set_property("pattern", "black")
    black.set_property("is-live", True)
    blkf = Gst.ElementFactory.make("capsfilter")
    blkf.set_property(
        "caps",
        Gst.Caps.from_string(
            f"video/x-raw,format=RGBA,width={w},height={h},framerate=30/1"
        ),
    )

    qout = Gst.ElementFactory.make("queue")

    for e in (shms, conv, scale, livef, fs, black, blkf, qout):
        bin_.add(e)
    Gst.Element.link_many(shms, conv, scale, livef)
    Gst.Element.link_many(black, blkf)
    livef.link(fs)  # fs.sink_0 = live
    blkf.link(fs)  # fs.sink_1 = black
    fs.link(qout)

    # ghost pad out
    ghost = Gst.GhostPad.new("src", qout.get_static_pad("src"))
    bin_.add_pad(ghost)

    pipeline.add(bin_)
    bin_.set_state(Gst.State.PLAYING)

    # compositor request pad
    sinkpad = comp.get_request_pad("sink_%u")
    sinkpad.set_property("xpos", xpos)
    sinkpad.set_property("ypos", ypos)
    sinkpad.set_property("alpha", alpha)
    sinkpad.set_property("width", w)
    sinkpad.set_property("height", h)
    ghost.link(sinkpad)

    # watch for errors/EOS to recycle this bin
    bus = pipeline.get_bus()
    bus.add_signal_watch()

    def on_msg(bus, msg):
        if msg.src == shms and msg.type in (Gst.MessageType.ERROR, Gst.MessageType.EOS):
            # drop to black immediately (fs already does), then cleanup/retry
            comp.release_request_pad(sinkpad)
            bin_.set_state(Gst.State.NULL)
            pipeline.remove(bin_)
            sources.pop(sock_path, None)
        return True

    bus.connect("message", on_msg)
    return {"bin": bin_, "pad": sinkpad}


def ensure_source(sock_path, w, h, x, y, alpha=1.0):
    if sock_path in sources:
        return
    # only attach if socket file exists (producer up)
    if os.path.exists(sock_path):
        sources[sock_path] = make_source_bin(sock_path, w, h, x, y, alpha)


def watcher():
    layout = [  # declare where each socket should land on the canvas
        ("/shared/prodA.sock", 1920, 1080, 0, 0, 1.0),
        ("/shared/prodB.sock", 480, 270, 50, 50, 0.8),
        ("/shared/prodC.sock", 480, 270, 50, 340, 0.8),
    ]
    while True:
        for sock_path, w, h, x, y, a in layout:
            # create if appears
            ensure_source(sock_path, w, h, x, y, a)
            # if it was removed on error, we’ll re-create next time it appears
            if sock_path not in sources and os.path.exists(sock_path):
                ensure_source(sock_path, w, h, x, y, a)
        time.sleep(0.25)


pipeline.set_state(Gst.State.PLAYING)
threading.Thread(target=watcher, daemon=True).start()
GObject.MainLoop().run()
