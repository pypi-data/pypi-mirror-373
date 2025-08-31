from __future__ import annotations
import struct, time
from multiprocessing.shared_memory import SharedMemory
from typing import Optional, Union

_HEADER_FORMAT = '<QQ'  # [seq, active_idx]
_HEADER_BYTES = struct.calcsize(_HEADER_FORMAT)  # 16

BytesLike = Union[bytes, bytearray, memoryview]

class SharedFrames:
    """
    Two-frame shared memory with a tiny seqlock:
      hdr[0] = seq (uint64, even -> stable, odd -> writing)
      hdr[1] = active index {0,1}
    Single-writer, multi-reader.
    """
    def __init__(self, shm: SharedMemory, nbytes: int):
        self.shm = shm
        self.nbytes = nbytes
        self._buf = memoryview(shm.buf)

        expected = _HEADER_BYTES + 2 * nbytes
        if len(self._buf) < expected:
            raise ValueError(f"SharedMemory size {len(self._buf)} < expected {expected}")

        self._hdr_view = self._buf[:_HEADER_BYTES]
        # Split header words for clearer write ordering (8-byte each)
        self._hdr_seq = self._hdr_view[:8]
        self._hdr_idx = self._hdr_view[8:16]

        off = _HEADER_BYTES
        self._f0 = self._buf[off:off + nbytes]
        self._f1 = self._buf[off + nbytes:off + 2 * nbytes]

        # Initialize if header appears zeroed (best-effort; consider magic/version)
        seq, active_idx = self._read_header()
        if seq == 0 and active_idx == 0:
            self._f0[:] = b'\x00' * len(self._f0)
            self._f1[:] = b'\x00' * len(self._f1)
            # Publish: idx first, then seq even
            self._write_idx(0)
            self._write_seq(0)

    # ---- header helpers ----
    def _read_header(self) -> tuple[int, int]:
        return (
            struct.unpack('<Q', self._hdr_seq)[0],
            struct.unpack('<Q', self._hdr_idx)[0],
        )

    def _write_seq(self, seq: int) -> None:
        struct.pack_into('<Q', self._hdr_seq, 0, seq)

    def _write_idx(self, idx: int) -> None:
        struct.pack_into('<Q', self._hdr_idx, 0, idx)

    # -------- writer (single process) --------
    def write(self, src: BytesLike) -> None:
        src_mv = memoryview(src)
        if src_mv.nbytes != self.nbytes:
            raise ValueError(f"src length {src_mv.nbytes} != nbytes {self.nbytes}")

        seq, active_idx = self._read_header()
        nxt = 1 - active_idx

        # Begin write: flip seq to odd (announce unstable)
        self._write_seq(seq + 1)

        dst = self._f1 if nxt == 1 else self._f0
        dst[:] = src_mv  # contiguous copy

        # Publish stable: write idx first, then seq even (reduced tear/order risk)
        self._write_idx(nxt)
        self._write_seq(seq + 2)

    # -------- reader (one or more processes) --------
    def read(self, dst: BytesLike) -> None:
        dst_mv = memoryview(dst)
        if dst_mv.nbytes != self.nbytes:
            raise ValueError(f"dst length {dst_mv.nbytes} != nbytes {self.nbytes}")
        if getattr(dst_mv, 'readonly', False):
            raise ValueError("dst must be writable (e.g., bytearray or writable memoryview)")

        spins = 0
        while True:
            s1, idx = self._read_header()
            if s1 & 1:  # writer in progress
                spins += 1
                if (spins & 0x3FFF) == 0:  # yield occasionally
                    time.sleep(0)
                continue

            src = self._f1 if idx == 1 else self._f0
            dst_mv[:] = src

            s2, _ = self._read_header()
            if s1 == s2 and (s2 & 1) == 0:
                return

    @staticmethod
    def create(nbytes: int, name: Optional[str] = None) -> "SharedFrames":
        total_bytes = _HEADER_BYTES + 2 * nbytes
        shm = SharedMemory(create=True, size=total_bytes, name=name)
        return SharedFrames(shm, nbytes)

    @staticmethod
    def attach(name: str, nbytes: int) -> "SharedFrames":
        shm = SharedMemory(name=name, create=False)
        return SharedFrames(shm, nbytes)

    # Context manager for safety
    def __enter__(self) -> "SharedFrames":
        return self
    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        # Release exported buffers before closing the SHM to avoid BufferError
        for mv in (self._f0, self._f1, self._hdr_seq, self._hdr_idx, self._hdr_view, self._buf):
            try:
                mv.release()
            except Exception:
                pass
        self.shm.close()

    def unlink(self) -> None:
        try:
            self.shm.unlink()
        except FileNotFoundError:
            pass
