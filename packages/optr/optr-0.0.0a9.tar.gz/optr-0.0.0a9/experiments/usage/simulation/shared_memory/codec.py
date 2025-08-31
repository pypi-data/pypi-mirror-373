from __future__ import annotations
import numpy as np
from dataclasses import dataclass

@dataclass(frozen=True)
class MuJoCoStateLayout:
    nq: int
    nv: int
    nmocap: int
    include_qvel: bool = False
    include_mocap: bool = True
    include_time: bool = True
    dtype: np.dtype = np.float64

    @property
    def itemsize(self) -> int: return np.dtype(self.dtype).itemsize
    @property
    def qpos_len(self) -> int: return self.nq
    @property
    def qvel_len(self) -> int: return self.nv if self.include_qvel else 0
    @property
    def mpos_len(self) -> int: return self.nmocap * 3 if self.include_mocap else 0
    @property
    def mquat_len(self) -> int: return self.nmocap * 4 if self.include_mocap else 0
    @property
    def time_len(self) -> int: return 1 if self.include_time else 0
    @property
    def frame_len(self) -> int:
        return self.qpos_len + self.qvel_len + self.mpos_len + self.mquat_len + self.time_len
    @property
    def frame_nbytes(self) -> int: return self.frame_len * self.itemsize

class MuJoCoStateCodec:
    """Packs/Unpacks MuJoCo state arrays into/from a flat float array (dtype=layout.dtype)."""
    def __init__(self, layout: MuJoCoStateLayout):
        self.L = layout
        off = 0
        self.sl_qpos = slice(off, off + self.L.qpos_len); off += self.L.qpos_len
        self.sl_qvel = slice(off, off + self.L.qvel_len); off += self.L.qvel_len
        self.sl_mpos = slice(off, off + self.L.mpos_len); off += self.L.mpos_len
        self.sl_mquat = slice(off, off + self.L.mquat_len); off += self.L.mquat_len
        self.sl_time = slice(off, off + self.L.time_len)

    def pack_into(self, dst: np.ndarray, *, qpos, qvel=None, mocap_pos=None, mocap_quat=None, t=None) -> None:
        np.copyto(dst[self.sl_qpos], qpos, casting="no")
        if self.L.qvel_len and qvel is not None:
            np.copyto(dst[self.sl_qvel], qvel, casting="no")
        if self.L.mpos_len and mocap_pos is not None:
            dst[self.sl_mpos] = np.asarray(mocap_pos).reshape(-1).astype(self.L.dtype, copy=False)
        if self.L.mquat_len and mocap_quat is not None:
            dst[self.sl_mquat] = np.asarray(mocap_quat).reshape(-1).astype(self.L.dtype, copy=False)
        if self.L.time_len and t is not None:
            dst[self.sl_time][0] = float(t)

    def unpack_from(self, src: np.ndarray, *, data) -> None:
        data.qpos[:] = src[self.sl_qpos]
        if self.L.qvel_len:
            data.qvel[:] = src[self.sl_qvel]
        if self.L.mpos_len and data.model.nmocap:
            data.mocap_pos[:] = src[self.sl_mpos].reshape(data.mocap_pos.shape)
        if self.L.mquat_len and data.model.nmocap:
            data.mocap_quat[:] = src[self.sl_mquat].reshape(data.mocap_quat.shape)
        if self.L.time_len:
            data.time = float(src[self.sl_time][0])
