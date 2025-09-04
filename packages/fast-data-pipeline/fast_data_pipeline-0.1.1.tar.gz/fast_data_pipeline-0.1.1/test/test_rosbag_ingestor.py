# tests/test_rosbag_ingestor.py

import os
import re
import yaml
import pytest
import tables
import numpy as np
import shutil
from pathlib import Path
from rosbags.highlevel import AnyReader
from test.utils import create_h5_layout_from_yaml
from data_pipeline.ingestion.rosbag_ingestor import RosbagIngester



@pytest.fixture(scope="module")
def rosbag_test_environment(tmpdir_factory):
    """
    Sets up a complete, isolated test environment for the RosbagIngester.
    """
    tests_dir = Path(__file__).parent
    project_root = tests_dir.parent

    sample_data_dir = project_root / "sample_data" / "input" / "rosbag"
    custom_msgs_path = project_root / "aivp-ros2-custom-messages"

    if not sample_data_dir.exists() or not any(sample_data_dir.iterdir()):
        pytest.skip(f"Sample rosbag data folder not found in '{sample_data_dir}'.")
    if not custom_msgs_path.exists():
        pytest.skip(f"Custom message submodule not found at '{custom_msgs_path}'.")

    source_rosbag_path = next(p for p in sample_data_dir.iterdir() if p.is_dir())
    
    base_dir = Path(tmpdir_factory.mktemp("rosbag_test_run"))
    input_dir = base_dir / "input"
    output_dir = base_dir / "output"
    config_dir = base_dir / "config"
    input_dir.mkdir()
    output_dir.mkdir()
    config_dir.mkdir()

    test_rosbag_path = input_dir / source_rosbag_path.name
    shutil.copytree(source_rosbag_path, test_rosbag_path)
    test_custom_msgs_path = input_dir / "custom_msgs"
    shutil.copytree(custom_msgs_path, test_custom_msgs_path)

   
    temp_layout_path = config_dir / "test_layout.yaml"
    layout_content = {
        'mapping': [{
            'source': 'ros2bag',
            'original_name': '/marwis',
            'target_name': '/rfmu/marwis/data',
            'units': 'degC',
            'description': 'MARWIS sensor data'
        }]
    }
    temp_layout_path.write_text(yaml.dump(layout_content))

    class MockStateManager:
        def get_unprocessed_items(self, items): return items
        def update_state(self, processed_items): pass

    ingester = RosbagIngester(
        input_folder=str(input_dir),
        output_folder=str(output_dir),
        state_manager=MockStateManager(),
        layout_yaml_path=str(temp_layout_path),
        ros_distro="jazzy",
        custom_msg_folders=[str(test_custom_msgs_path)]
    )
    ingester.run()

    source_folder_name = test_rosbag_path.name
    sanitized_name = re.sub(r'[^a-zA-Z0-9_]', '_', source_folder_name)
    if sanitized_name and sanitized_name[0].isdigit():
        sanitized_name = '_' + sanitized_name
    
    output_h5_filename = f"{sanitized_name}.h5"
    output_h5_path = output_dir / output_h5_filename

    yield {
        "output_h5": str(output_h5_path),
        "layout_path": str(temp_layout_path),
        "layout_content": layout_content,
        "source_rosbag": str(test_rosbag_path)
    }


def test_rosbag_file_creation(rosbag_test_environment):
    """Test 1: Check if the output HDF5 file was created."""
    output_h5_path = rosbag_test_environment["output_h5"]
    assert os.path.exists(output_h5_path), "Output HDF5 file from rosbag was not created."


def test_rosbag_output_conforms_to_layout(rosbag_test_environment):
    """Test 3: Validate that the HDF5 file conforms to the layout."""
    output_h5_path = Path(rosbag_test_environment["output_h5"])
    layout_spec_path = Path(rosbag_test_environment["layout_path"])

    assert output_h5_path.exists()

    try:
        h5_validator = create_h5_layout_from_yaml(layout_spec_path, enforce_units=True)
        h5_validator.validate(output_h5_path)
    except Exception as e:
        pytest.fail(f"HDF5 file validation raised an exception: {e}")


def test_rosbag_data_values_are_identical(rosbag_test_environment):
    """Test 4: Spot check values for data integrity for all topics."""
    output_h5, source_rosbag, layout = rosbag_test_environment.values()

    with tables.open_file(output_h5, 'r') as h5file, \
         AnyReader([Path(source_rosbag)]) as reader:
        
        for topic_mapping in layout['mapping']:
            original_topic = topic_mapping['original_name']
            target_table_path = topic_mapping['target_name']

            try:
                h5_table = h5file.root
                for part in target_table_path.strip('/').split('/'):
                    h5_table = getattr(h5_table, part)
            except (tables.NoSuchNodeError, AttributeError):
                pytest.fail(f"Could not access table '{target_table_path}' in HDF5 file.")

            connections = [c for c in reader.connections if c.topic == original_topic]
            if not connections:
                pytest.skip(f"Topic '{original_topic}' not found in the bag.")

            original_data = [(ts, reader.deserialize(raw, connections[0].msgtype))
                             for _, ts, raw in reader.messages(connections=connections)]

            assert len(original_data) == h5_table.nrows, f"Row count mismatch for topic {original_topic}"

            if h5_table.nrows > 0:
                first_ts_ros = original_data[0][0] / 1e9
                first_ts_h5 = h5_table[0]['timestamp_s']
                assert np.isclose(first_ts_ros, first_ts_h5), f"Timestamp mismatch for topic {original_topic}"