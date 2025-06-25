
import cv2
from pathlib import Path

from ark.client.comm_infrastructure.base_node import BaseNode, main
from arktypes import unpack, rgbd_t

CONFIG_PATH = "config/global.yaml"

class ImageLoggerNode(BaseNode):
    def __init__(self, path: str) -> None:
        """!
        Initializes the node.

        @param path  Path to the configuration file.
        """
        super().__init__("image_logger", path)
        # Setup output directory
        self.output_dir = Path("output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for child in self.output_dir.iterdir():
            if child.is_file():
                child.unlink()

        self.frame = 0
        self.create_subscriber("IntelRealSense/rgbd/sim", rgbd_t, self.save_image)
        
    def save_image(self, t: float, channel_name: str, msg: rgbd_t) -> None:
        image, depth = unpack.unpack_rgbd(msg)
        output_path = self.output_dir / f"{self.frame}.png"
        cv2.imwrite(str(output_path), image)
        self.frame += 1


if __name__ == "__main__":
    main(ImageLoggerNode, CONFIG_PATH)
