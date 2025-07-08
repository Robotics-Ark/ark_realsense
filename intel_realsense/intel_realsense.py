
from typing import Any, Dict, Optional
from dataclasses import dataclass
from enum import Enum

from ark.client.comm_infrastructure.base_node import main
from ark.system.component.sensor import Sensor
from ark.system.driver.sensor_driver import SensorDriver
from ark.system.pybullet.pybullet_camera_driver import BulletCameraDriver
from ark.tools.log import log
from arktypes import rgbd_t
from arktypes.utils import unpack, pack

from intel_realsense_driver import IntelRealSenseDriver

@dataclass
class Drivers(Enum):
    PYBULLET_DRIVER = BulletCameraDriver
    DRIVER = IntelRealSenseDriver


class IntelRealSense(Sensor):

    def __init__(self, name: str, 
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

        self.rgbd_channel = self.name + "/rgbd"
        if self.sim == True:
            self.rgbd_channel = self.rgbd_channel + "/sim"

        self.component_channels_init({
            self.rgbd_channel: rgbd_t,
        })
     
    def pack_data(self, images: Any) -> Dict[str, Any]:
        color_image = images['color']
        depth_image = images['depth']

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