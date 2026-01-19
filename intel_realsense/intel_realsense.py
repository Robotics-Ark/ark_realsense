import importlib
from enum import Enum
from typing import Any, Dict, Optional

from ark.client.comm_infrastructure.base_node import main
from ark.system.component.sensor import Sensor
from ark.system.driver.sensor_driver import SensorDriver
from arktypes import rgbd_t
from arktypes.utils import pack


class Drivers(Enum):
    PYBULLET_DRIVER = "ark.system.pybullet.pybullet_camera_driver.BulletCameraDriver"
    MUJOCO_DRIVER = "ark.system.mujoco.mujoco_camera_driver.MujocoCameraDriver"
    ISAAC_DRIVER = "ark.system.isaac.isaac_camera_driver.IsaacCameraDriver"
    DRIVER = "intel_realsense_driver.IntelRealSenseDriver"

    def load(self):
        module_path, class_name = self.value.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)


class IntelRealSense(Sensor):

    def __init__(
        self,
        name: str,
        global_config: Dict[str, Any] = None,
        driver: Optional[SensorDriver] = None,
    ) -> None:
        """
        Initialize the SystemComponent instance.

        Args:
            name (str): The name of the component, initializes name
            sim (bool): Whether the component is simulated or not
            config (Dict[str, Any]): Configuration parameters for the component
            driver (Optional[SensorDriver]): The driver for the sensor component
        """
        super().__init__(name, global_config, driver)

        self.rgbd_channel = None
        observation_channels = global_config["observation_channels"]
        if observation_channels is not None and len(observation_channels) > 0:
            for key in observation_channels.keys():
                if "rgbd" in key:
                    self.rgbd_channel = key

        if self.rgbd_channel is None:
            namespace = global_config["namespace"]
            self.rgbd_channel = f"{namespace}/" + self.name + "/rgbd"
            if self.sim == True:
                self.rgbd_channel = self.rgbd_channel + "/sim"

        self.component_channels_init(
            {
                self.rgbd_channel: rgbd_t,
            }
        )

    def pack_data(self, images: Any) -> Dict[str, Any]:
        color_image = images["color"]
        depth_image = images["depth"]

        msg = pack.rgbd(rgb_image=color_image, depth_map=depth_image, name=self.name)
        return {self.rgbd_channel: msg}

    def get_sensor_data(self) -> Any:
        """Simulate the sensor's behavior."""
        images = self._driver.get_images()
        return images


CONFIG_PATH = "config/global_config.yaml"
if __name__ == "__main__":
    name = "IntelRealSense"
    driver = IntelRealSenseDriver(name, CONFIG_PATH)
    main(IntelRealSense, name, CONFIG_PATH, driver)
