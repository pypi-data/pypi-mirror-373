"""ONNX-controlled MuJoCo simulation following the Simulation protocol."""

from pathlib import Path
import sys
import mujoco

# Add src to path to import optr modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from optr.input.keyboard import KeyboardInput
from optr.simulator.mujoco.simulation import State

from controller import OnnxController


class OnnxSimulation:
    """ONNX-controlled robot simulation implementing the Simulation protocol."""

    def __init__(
        self,
        scene: str = "../assets/models/g1/scene.xml",
        policy: str = "balance.onnx",
        socket_path: str = "/tmp/robot/keyboard.sock",
    ):
        """Initialize ONNX simulation.

        Args:
            scene: Path to MuJoCo scene XML file
            policy: ONNX policy filename
            socket_path: Socket path for keyboard input
        """
        self.scene_path = scene
        self.policy = policy
        self.socket_path = socket_path

        # Protocol-required state
        self.state: State = self._create_initial_state()
        
        # ONNX-specific components
        self.controller = None
        self.keyboard = None
        self._setup_onnx_components()

    def _create_initial_state(self) -> State:
        """Create initial simulation state."""
        if not Path(self.scene_path).exists():
            raise FileNotFoundError(f"Scene file not found: {self.scene_path}")

        model = mujoco.MjModel.from_xml_path(self.scene_path)
        data = mujoco.MjData(model)
        
        # Setup timing
        model.opt.timestep = 0.002
        
        # Reset to initial pose if available
        for i in range(model.nkey):
            if model.key(i).name == "knees_bent":
                mujoco.mj_resetDataKeyframe(model, data, i)
                break
        
        return State(model=model, data=data)

    def _setup_onnx_components(self) -> None:
        """Setup ONNX controller and keyboard input."""
        # Setup keyboard input
        self.keyboard = KeyboardInput(self.socket_path)
        self.keyboard.start()

        # Setup ONNX controller
        policy_path = f"../assets/policies/{self.policy}"
        if not Path(policy_path).exists():
            raise FileNotFoundError(f"Policy file not found: {policy_path}")

        default_angles = self.state.data.qpos[7:].copy()
        
        self.controller = OnnxController(
            policy_path=policy_path,
            keyboard_input=self.keyboard,
            default_angles=default_angles,
            ctrl_dt=0.02,
            n_substeps=10,
            action_scale=0.5,
            vel_scale=(1.5, 0.8, 2 * 3.14159),
        )

        # Register control callback
        mujoco.set_mjcb_control(self.controller.get_control)

    def step(self) -> State:
        """Step the simulation forward (implements protocol)."""
        mujoco.mj_step(self.state.model, self.state.data)
        return self.state

    def reset(self) -> State:
        """Reset to initial state (implements protocol)."""
        mujoco.mj_resetData(self.state.model, self.state.data)
        
        # Reset to keyframe if available
        for i in range(self.state.model.nkey):
            if self.state.model.key(i).name == "knees_bent":
                mujoco.mj_resetDataKeyframe(self.state.model, self.state.data, i)
                break
        
        # Reset controller
        if self.controller:
            self.controller.reset()
            
        return self.state

    def close(self) -> None:
        """Clean up simulation resources (implements protocol)."""
        mujoco.set_mjcb_control(None)
        if self.keyboard:
            self.keyboard.stop()
