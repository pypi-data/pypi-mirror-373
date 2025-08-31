"""ONNX robot simulation."""

from pathlib import Path

import mujoco
from optr.simulator.mujoco.simulation import Simulation, State

from .controller import OnnxController


class OnnxSimulation(Simulation):
    """ONNX robot simulation."""

    def __init__(
        self,
        scene: str = "src/simulation/assets/models/g1/scene.xml",
        policy_path: str = "src/simulation/assets/policies/balance.onnx",
    ):
        self.scene_path = scene
        self.policy_path = policy_path
        self.state = self._create_state()
        self._controller = self._setup_controller()

    def _create_state(self) -> State:
        if not Path(self.scene_path).exists():
            raise FileNotFoundError(f"Scene file not found: {self.scene_path}")

        model = mujoco.MjModel.from_xml_path(self.scene_path)
        data = mujoco.MjData(model)
        model.opt.timestep = 0.002

        for i in range(model.nkey):
            if model.key(i).name == "knees_bent":
                mujoco.mj_resetDataKeyframe(model, data, i)
                break

        return State(model=model, data=data)

    def _setup_controller(self) -> OnnxController:
        if not Path(self.policy_path).exists():
            raise FileNotFoundError(f"Policy file not found: {self.policy_path}")

        controller = OnnxController(
            policy_path=self.policy_path,
            default_angles=self.state.data.qpos[7:].copy()
        )
        mujoco.set_mjcb_control(controller.get_control)
        return controller

    def step(self) -> State:
        self._controller.update()
        mujoco.mj_step(self.state.model, self.state.data)
        return self.state

    def reset(self) -> State:
        mujoco.mj_resetData(self.state.model, self.state.data)
        for i in range(self.state.model.nkey):
            if self.state.model.key(i).name == "knees_bent":
                mujoco.mj_resetDataKeyframe(self.state.model, self.state.data, i)
                break
        if self._controller:
            self._controller.reset()
        return self.state

    def close(self) -> None:
        mujoco.set_mjcb_control(None)

    @property
    def controller(self) -> OnnxController:
        return self._controller
