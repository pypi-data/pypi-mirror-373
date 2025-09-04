import os
import gc
import re
import keyword
import logging
import pickle
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple, Optional

from tqdm import tqdm
import tables
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg

from .base_ingestor import BaseIngester
from .ros2_msg_parser.parser import ROS2MessageParser


logger = logging.getLogger(__name__)


class SuppressLowLevelOutput:
    """A context manager to suppress stdout and stderr at the OS level."""

    def __enter__(self):
        self.old_stdout_fileno = os.dup(1)
        self.old_stderr_fileno = os.dup(2)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        os.close(devnull)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.dup2(self.old_stdout_fileno, 1)
        os.dup2(self.old_stderr_fileno, 2)
        os.close(self.old_stdout_fileno)
        os.close(self.old_stderr_fileno)


class RosbagIngester(BaseIngester):
    """
    Ingests ROS 2 bag files and converts them to HDF5 format.
    - Simple messages: each attribute is stored as a separate dataset for performance.
    - Complex messages (e.g., Images): parsed into a structured HDF5 group.
    """

    def __init__(
        self,
        input_folder: str,
        output_folder: str,
        state_manager,
        layout_yaml_path: str,
        ros_distro: str = "humble",
        custom_msg_folders: List[str] = None,
        chunk_size: int = 10,
    ):
        super().__init__(input_folder, output_folder, state_manager, layout_yaml_path)
        self.ros_distro = ros_distro
        self.custom_msg_folders = custom_msg_folders or []
        self.chunk_size = chunk_size
        self.typestore = self._initialize_typestore()
        self.topic_map = self._create_topic_map_from_layout()

        self.parser = ROS2MessageParser()
        self.complex_msg_parsers = {
            "sensor_msgs/msg/Image": self.parser._parse_sensor_msgs_image,
            "sensor_msgs/msg/PointCloud2": self.parser._parse_sensor_msgs_pointcloud2,
        }
        logger.info(
            f"Initialized with complex parsers for: {list(self.complex_msg_parsers.keys())}"
        )

    def _create_topic_map_from_layout(self) -> Dict[str, str]:
        if not self.layout_spec or "mapping" not in self.layout_spec:
            raise ValueError("Layout specification is missing or invalid.")
        mapper = {
            m["original_name"]: m["target_name"]
            for m in self.layout_spec["mapping"]
            if m.get("source") == "ros2bag"
        }
        logger.info(f"Dynamically created rosbag topic map with {len(mapper)} entries.")
        return mapper

    def discover_files(self) -> List[str]:
        if not os.path.isdir(self.input_folder):
            return []
        potential = [
            os.path.join(self.input_folder, d)
            for d in os.listdir(self.input_folder)
            if os.path.isdir(os.path.join(self.input_folder, d))
        ]
        return [
            d for d in potential if os.path.isfile(os.path.join(d, "metadata.yaml"))
        ]

    def process_file(self, folder_path: str) -> bool:
        folder_name = os.path.basename(folder_path)
        safe_name = self._sanitize_hdf5_identifier(folder_name)
        output_path = os.path.join(self.output_folder, f"{safe_name}.h5")

        h5file = None
        try:
            h5file = tables.open_file(
                output_path, mode="w", title=f"Data from {folder_name}"
            )
            with SuppressLowLevelOutput():
                with AnyReader(
                    [Path(folder_path)], default_typestore=self.typestore
                ) as reader:
                    self._stream_and_write_dynamic(reader, h5file)

            final_size = os.path.getsize(output_path) / (1024 * 1024)
            logger.info(
                f"Successfully created HDF5 file '{output_path}' with a size of {final_size:.2f} MB."
            )
            return True
        except Exception as e:
            logger.error(f"Failed to process rosbag {folder_name}: {e}", exc_info=True)
            if h5file and h5file.isopen:
                h5file.close()
            if os.path.exists(output_path):
                os.remove(output_path)
            return False
        finally:
            if h5file and h5file.isopen:
                h5file.close()
            gc.collect()

    def _stream_and_write_dynamic(self, reader: AnyReader, h5file: tables.File):
        buffers = {}
        datasets = {}

        connections_to_process = [
            c for c in reader.connections if c.topic in self.topic_map
        ]
        total_messages = sum(c.msgcount for c in connections_to_process)

        message_iterator = reader.messages(connections=connections_to_process)
        progress_bar = tqdm(
            message_iterator,
            total=total_messages,
            desc="  -> Messages",
            unit="msg",
            leave=False,
        )

        for conn, ts, raw in progress_bar:
            topic_path = self.topic_map[conn.topic]
            msg = reader.deserialize(raw, conn.msgtype)

            # Check if the message type has a dedicated complex parser
            if conn.msgtype in self.complex_msg_parsers:
                self._handle_complex_message(h5file, topic_path, msg, conn.msgtype)
            else:
                # Use the original high-performance buffering for simple messages
                if topic_path not in buffers:
                    buffers[topic_path], datasets[topic_path] = (
                        self._initialize_topic_storage(h5file, conn.msgtype, topic_path)
                    )

                row_data = self._get_message_data_as_dict(msg, ts, conn.msgtype)

                for field, value in row_data.items():
                    if field in buffers[topic_path]:
                        buffers[topic_path][field].append(value)

                if len(buffers[topic_path].get("timestamp_s", [])) >= self.chunk_size:
                    self._flush_buffers_to_hdf5(
                        datasets[topic_path], buffers[topic_path]
                    )

        # Flush any remaining data in the buffers for simple messages
        for topic_path, topic_buffers in buffers.items():
            if topic_buffers.get("timestamp_s"):
                self._flush_buffers_to_hdf5(datasets[topic_path], topic_buffers)

        progress_bar.close()

    def _handle_complex_message(
        self, h5file: tables.File, topic_path: str, msg: Any, msgtype: str
    ):
        """
        Handles complex messages by parsing them into a structured dictionary
        and writing that structure to the HDF5 file.
        """
        parser_func = self.complex_msg_parsers[msgtype]

        parsed_data = parser_func(msg)

        parent_group = h5file.root
        parts = topic_path.strip("/").split("/")
        for part in parts:
            if not hasattr(parent_group, part):
                parent_group = h5file.create_group(parent_group, part)
            else:
                parent_group = getattr(parent_group, part)

        self._append_to_structured_datasets(parent_group, parsed_data)

    def _append_to_structured_datasets(
        self, parent_group: tables.Group, data_dict: Dict[str, Any]
    ):
        """
        Recursively traverses a dictionary, creating HDF5 groups for nested dicts
        and datasets for values. Appends data to existing datasets.
        """
        for key, value in data_dict.items():
            sane_key = self._sanitize_hdf5_identifier(key)

            if isinstance(value, dict):
                if not hasattr(parent_group, sane_key):
                    child_group = parent_group._v_file.create_group(
                        parent_group, sane_key, title=sane_key
                    )
                else:
                    child_group = getattr(parent_group, sane_key)
                self._append_to_structured_datasets(child_group, value)

            else:
                dataset_exists = hasattr(parent_group, sane_key)

                if isinstance(value, np.ndarray):
                    if not dataset_exists:
                        # Create a new EArray on first sight
                        atom = tables.Atom.from_dtype(value.dtype)
                        shape = (
                            0,
                        ) + value.shape  # Make it extendable on the first axis
                        parent_group._v_file.create_earray(
                            parent_group, sane_key, atom, shape, title=sane_key
                        )

                    dataset = getattr(parent_group, sane_key)
                    dataset.append(
                        value[np.newaxis, :]
                    )  # Because the items are supposed to be given in batches add a new axis to the front

                # Handling for primitive types (int, float, bool, str)
                else:
                    if not dataset_exists:
                        if isinstance(value, str):
                            # Use VLArray for strings to handle variable lengths gracefully
                            atom = tables.StringAtom(
                                itemsize=len(value.encode("utf-8")) + 64
                            )  # Add buffer
                            parent_group._v_file.create_earray(
                                parent_group, sane_key, atom, (0,), title=sane_key
                            )
                        else:
                            # Use EArray for other primitives
                            atom = tables.Atom.from_dtype(np.array(value).dtype)
                            parent_group._v_file.create_earray(
                                parent_group, sane_key, atom, (0,), title=sane_key
                            )

                    dataset = getattr(parent_group, sane_key)
                    dataset.append([value])  # Append scalar value as a list

    def _initialize_topic_storage(
        self, h5file: tables.File, msgtype_name: str, topic_path: str
    ) -> Tuple[Dict, Dict]:
        buffers = {}
        datasets = {}

        # This is the corrected logic for creating nested groups.
        # It properly iterates through path parts and creates them if they don't exist.
        parts = topic_path.strip("/").split("/")
        parent = h5file.root
        for part in parts:
            if not hasattr(parent, part):
                parent = h5file.create_group(parent, part)
            else:
                parent = getattr(parent, part)
        parent_group = parent

        fields = self._get_all_fields(msgtype_name)
        fields.insert(0, ("timestamp_s", [], "float64", False))

        for flat_name, path, ros_type, is_array in fields:
            sane_name = self._sanitize_hdf5_identifier(flat_name)
            buffers[sane_name] = []

            # This logic remains for simple, flattened message types
            if ros_type == "string" and not is_array:
                atom = tables.StringAtom(itemsize=512)
            elif is_array:
                #TODO: discuss with Timon
                # Arrays of simple types will be pickled into bytes
                atom = tables.VLStringAtom()
            else:
                try:
                    atom = tables.Atom.from_dtype(np.dtype(ros_type))
                except (TypeError, ValueError):
                    logger.warning(
                        f"Could not create atom for unrecognized type '{ros_type}'. Defaulting to VLStringAtom."
                    )
                    atom = tables.VLStringAtom()

            # Using create_earray for fixed-size and create_vlarray for variable-length
            # create_array is fixed size, therefore we can't use it because the data must be streamed so that memory does not overflow
            # This is primarily for the flattened simple messages
            if isinstance(atom, tables.VLStringAtom):
                datasets[sane_name] = h5file.create_vlarray(
                    parent_group, sane_name, atom, title=sane_name
                )
            else:
                datasets[sane_name] = h5file.create_earray(
                    parent_group, sane_name, atom, (0,), title=sane_name
                )

        return buffers, datasets

    def _flush_buffers_to_hdf5(self, datasets: Dict, buffers: Dict):
        for field, data_buffer in buffers.items():
            if not data_buffer:
                continue
            try:
                # Handle VLArrays (variable-length data) differently
                if isinstance(datasets[field], tables.VLArray):
                    for item in data_buffer:
                        # Ensure item is bytes before appending to VLArray
                        if not isinstance(item, bytes):
                            item = pickle.dumps(item)
                        datasets[field].append(item)
                else:
                    # For regular arrays, append the entire list
                    datasets[field].append(data_buffer)
            except Exception as e:
                sample_data = data_buffer[0] if data_buffer else "N/A"
                logger.error(
                    f"Failed to append data for field '{field}' (type: {type(sample_data)}): {e}",
                    exc_info=True,
                )
            data_buffer.clear()

    def _get_message_data_as_dict(self, msg: Any, ts: int, msgtype_name: str) -> Dict:
        data_dict = {"timestamp_s": ts / 1e9}
        all_fields = self._get_all_fields(msgtype_name)

        for flat_name, path, ros_type, is_array in all_fields:
            sane_name = self._sanitize_hdf5_identifier(flat_name)
            value = self._get_value_recursive(msg, path)

            # For simple messages, we still flatten and serialize arrays to bytes
            if is_array and value is not None:
                try:
                    # Prefer numpy's efficient serialization if possible
                    if isinstance(value, np.ndarray):
                        value = value.tobytes()
                    elif isinstance(value, (list, tuple)):
                        value = np.array(value).tobytes()
                    else:  # Fallback to pickle for other iterable types
                        value = pickle.dumps(value)
                except Exception:
                    value = pickle.dumps(value)  # Final fallback
            elif ros_type == "string" and isinstance(value, str):
                value = value.encode("utf-8")

            data_dict[sane_name] = value

        return data_dict

    def _get_all_fields(
        self,
        typename: str,
        prefix: str = "",
        path: Optional[List[str]] = None,
        visited: Optional[Set[str]] = None,
    ) -> List[Tuple[str, List[str], str, bool]]:
        if visited is None:
            visited = set()
        if path is None:
            path = []
        if typename in visited:
            return []

        # Stop recursion if we hit a type that has a complex parser
        if typename in self.complex_msg_parsers:
            return []

        visited.add(typename)
        fields_list = []
        try:
            msg_def = self.typestore.get_msgdef(typename)
        except KeyError:
            return []

        for field_name, field_type_tuple in msg_def.fields:
            flat_name = f"{prefix}{field_name}"
            new_path = path + [field_name]

            node_type_int, type_details = field_type_tuple
            is_array = node_type_int in (3, 4)

            element_type_name = None
            if node_type_int in (1, 2):
                element_type_name = (
                    type_details[0] if node_type_int == 1 else type_details
                )
            elif is_array:
                element_node_type, element_details = type_details[0]
                if element_node_type == 1:
                    element_type_name = element_details[0]
                elif element_node_type == 2:
                    element_type_name = element_details

            if not element_type_name:
                continue

            # If a field is a complex type, treat it as a single item and don't recurse further.
            # The original logic will then pickle it if it's part of a simple message.
            if element_type_name in self.complex_msg_parsers and not is_array:
                fields_list.append((flat_name, new_path, element_type_name, is_array))
                continue

            nested_fields = self._get_all_fields(
                element_type_name, f"{flat_name}_", new_path, visited.copy()
            )

            if nested_fields and not is_array:
                fields_list.extend(nested_fields)
            else:
                fields_list.append((flat_name, new_path, element_type_name, is_array))
        return fields_list

    def _get_value_recursive(self, obj: Any, parts: List[str]) -> Any:
        val = obj
        for part in parts:
            try:
                val = getattr(val, part)
            except AttributeError:
                return None
        if hasattr(val, "sec") and hasattr(val, "nanosec"):
            return val.sec + val.nanosec * 1e-9
        return val

    def _initialize_typestore(self):
        distro = getattr(Stores, f"ROS2_{self.ros_distro.upper()}", Stores.ROS2_HUMBLE)
        store = get_typestore(distro)
        if not self.custom_msg_folders:
            return store

        logger.info(f"Scanning for custom messages in: {self.custom_msg_folders}")
        for folder in self.custom_msg_folders:
            for path in Path(folder).rglob("*.msg"):
                if path.parent.name == "msg":
                    try:
                        pkg = path.parent.parent.name
                        name = f"{pkg}/msg/{path.stem}"
                        store.register(get_types_from_msg(path.read_text(), name))
                        logger.info(f"Registered custom message: {name}")
                    except Exception as e:
                        logger.error(f"Failed to register message {path}: {e}")
        return store

    def _sanitize_hdf5_identifier(self, name: str) -> str:
        name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        if name and name[0].isdigit():
            name = "_" + name
        if keyword.iskeyword(name):
            name += "_"
        return name or "unnamed"


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    class MockStateManager:
        def get_unprocessed_items(self, items):
            return items

        def update_state(self, processed_items):
            logger.info(f"StateManager would save state for: {processed_items}")

    TEST_INPUT_DIR = "/mnt/sambashare/ugglf/2025-07-25/bags"
    TEST_OUTPUT_DIR = "/mnt/sambashare/ugglf/output/latest"
    YAML_PATH = "data-pipeline/configs/h5_layout_specification.yaml"
    CUSTOM_MESSAGES_FOLDER = ["data-pipeline/aivp-ros2-custom-messages"]

    os.makedirs(TEST_INPUT_DIR, exist_ok=True)
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

    logger.warning(
        f"ACTION REQUIRED: Place a sample rosbag folder in: {os.path.abspath(TEST_INPUT_DIR)}"
    )

    rosbag_ingester = RosbagIngester(
        input_folder=TEST_INPUT_DIR,
        output_folder=TEST_OUTPUT_DIR,
        custom_msg_folders=CUSTOM_MESSAGES_FOLDER,
        state_manager=MockStateManager(),
        layout_yaml_path=YAML_PATH,
    )

    rosbag_ingester.run()
