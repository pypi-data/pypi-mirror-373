from __future__ import annotations
import numpy as np
import mujoco
from ..shared_memory import MuJoCoStateLayout, MuJoCoStateCodec, SharedFrames


class MuJoCoRenderer:
    """
    Custom MuJoCo renderer that reads state from shared memory.
    Holds its own MjData built from a model created in the main process.
    Copies snapshot -> mj_forward -> render.
    """
    def __init__(self, model, layout: MuJoCoStateLayout,
                 width: int = 1280, height: int = 720, camera: str = "track"):
        self.mj = mujoco
        self.model = model                    # provided by Runner (same process)
        self.data = self.mj.MjData(self.model)
        self.codec = MuJoCoStateCodec(layout)
        self._work = np.empty(self.codec.L.frame_len, dtype=self.codec.L.dtype)
        self.width, self.height, self.camera = width, height, camera
        
        # Set up rendering contexts
        self._setup_rendering()

    def _setup_rendering(self):
        """Initialize MuJoCo rendering contexts."""
        try:
            # Create scene and context
            self.scene = mujoco.MjvScene(self.model, maxgeom=10000)
            self.context = mujoco.MjrContext(self.model, mujoco.mjtFontScale.mjFONTSCALE_150)
            
            # Create camera
            self.cam = mujoco.MjvCamera()
            self.cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
            self.cam.trackbodyid = 0  # Track root body
            self.cam.distance = 3.0
            self.cam.elevation = -20
            self.cam.azimuth = 180
            
            # Create viewport
            self.viewport = mujoco.MjrRect(0, 0, self.width, self.height)
            
            # Create framebuffer for offscreen rendering
            self._rgb_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            self._rendering_enabled = True
        except Exception as e:
            print(f"Warning: Failed to initialize MuJoCo rendering: {e}")
            self._rendering_enabled = False
            self._rgb_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)

    def blit_and_forward(self, frames: SharedFrames):
        """Read state from shared memory and update MjData."""
        frames.read_into(self._work.view(np.uint8))
        self.codec.unpack_from(self._work, data=self.data)
        self.mj.mj_forward(self.model, self.data)

    def render_frame(self, frames: SharedFrames) -> np.ndarray:
        """Read from shared memory and render a frame."""
        self.blit_and_forward(frames)
        
        if not self._rendering_enabled:
            # Return black frame if rendering is disabled
            return self._rgb_buffer.copy()
        
        try:
            # Update scene
            mujoco.mjv_updateScene(
                self.model, self.data, mujoco.MjvOption(), None,
                self.cam, mujoco.mjtCatBit.mjCAT_ALL, self.scene
            )
            
            # Render to buffer
            mujoco.mjr_render(self.viewport, self.scene, self.context)
            
            # Read pixels
            mujoco.mjr_readPixels(self._rgb_buffer, None, self.viewport, self.context)
            
            # Flip vertically (OpenGL convention)
            return np.flipud(self._rgb_buffer)
        except Exception as e:
            print(f"Warning: Rendering failed: {e}")
            return self._rgb_buffer.copy()

    def close(self):
        """Clean up rendering resources."""
        if hasattr(self, 'context'):
            self.context.free()
        if hasattr(self, 'scene'):
            self.scene.free()
