
from typing import Any, Dict, Optional

from sensor_msgs.msg import Image, PointCloud2
from sensor_msgs_py.point_cloud2 import read_points
import numpy as np

"""
TODO up to debate with Timon
Reason switching to this implementation:
1- Separation of concerns: the parser should only parse, ingestor should do the differentiation
2- Multiple parsers for same message possible
3- No default search for complex messages inside, instead define a new parser and utilize the older ones inside, less debugging and confusion
"""

class ROS2MessageParser:

    def parse(self, msg: Any) -> Optional[Dict[str, Any]]:
        if isinstance(msg, Image):
            return self._parse_sensor_msgs_image(msg)
        if isinstance(msg, PointCloud2):
            return self._parse_sensor_msgs_pointcloud2(msg)
        return None

    def _parse_sensor_msgs_image(self, msg: Image) -> Dict[str, Any]:
        return {
            "type": "Image",
            "data": np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, -1),
            "metadata": {
                "timestamp_s": msg.header.stamp.sec,
                "timestamp_ns": msg.header.stamp.nanosec,
                "frame_id": msg.header.frame_id,
                "height": msg.height,
                "width": msg.width,
                "encoding": msg.encoding,
                "is_bigendian": msg.is_bigendian,
                "step": msg.step,
            }
        }

    def _parse_sensor_msgs_pointcloud2(self, msg: PointCloud2) -> Dict[str, Any]:
        points = read_points(msg, skip_nans=True)
        return {
            "type": "PointCloud2",
            "data": points,
            "metadata": {
                "timestamp_s": msg.header.stamp.sec,
                "timestamp_ns": msg.header.stamp.nanosec,
                "frame_id": msg.header.frame_id,
                "height": msg.height,
                "width": msg.width,
                "is_dense": msg.is_dense,
            }
        }