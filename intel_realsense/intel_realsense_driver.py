
from typing import Any, Dict, Optional

from ark.system.driver.sensor_driver import CameraDriver

import pyrealsense2 as rs
import numpy as np
import time

class IntelRealSenseDriver(CameraDriver):
    def __init__(self, 
                 sensor_name: str,
                 sensor_config: Dict[str, Any] = None
                 ) -> None:
        super().__init__(sensor_name, sensor_config, False)
        # Configure depth and color streams
        self.pipeline = rs.pipeline()
        self.rs_config = rs.config()
        self.enable_streams()

    def start_streaming(self):
        """Start the RealSense pipeline"""
        self.pipeline.start(self.rs_config)
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = self.rs_config.resolve(pipeline_wrapper)
        depth_sensor = pipeline_profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()
        self.align = rs.align(rs.stream.color)

    def enable_streams(self):
        """Enable streams dynamically from config file"""
        stream_map = {
            "depth": rs.stream.depth,
            "color": rs.stream.color,
            "infrared": rs.stream.infrared
        }
        
        format_map = {
            "z16": rs.format.z16,
            "bgr8": rs.format.bgr8,
            "rgb8": rs.format.rgb8,
            "y8": rs.format.y8,
            "y16": rs.format.y16
        }

        self.steams_enabled = []
        self.width = self.config.get("width", 640)
        self.height = self.config.get("height", 480)
        self.freq = self.config.get("frequency", 60)
        
        for stream_name, stream_config in self.config["streams"].items():
            if stream_config["enable"]:
                self.rs_config.enable_stream(
                    stream_map[stream_name],
                    self.width,
                    self.height,
                    format_map[stream_config["format"]],
                    self.freq
                )
                self.steams_enabled.append(stream_name)

        self.start_streaming()

        # Wait to allow blue from realsense to correct
        wait_time = self.config.get("wait_time", 3.0)
        time.sleep(wait_time)

    def get_images(self):

        # Wait for frames from the pipeline
        frames = self.pipeline.wait_for_frames()
        frames = self.align.process(frames)

        # Create an empty dictionary to store the images
        images = {}
        if "depth" in self.steams_enabled:
            depth_frame = frames.get_depth_frame()
            depth_image = np.asanyarray(depth_frame.get_data())
            depth_image = depth_image * self.depth_scale
            images["depth"] = depth_image
        if "color" in self.steams_enabled:
            color_frame = frames.get_color_frame()
            color_image = np.asanyarray(color_frame.get_data())
            timestamp = color_frame.get_timestamp() * 1e-3
            images["color"] = color_image
            images["timestamp"] = timestamp
        if "infrared" in self.steams_enabled:
            infrared_frame = frames.get_infrared_frame()
            infrared_image = np.asanyarray(infrared_frame.get_data())
            images["infrared"] = infrared_image

        return images

    def shutdown_driver(self) -> None:
        self.pipeline.stop()
        pass
