# tests/test_mf4_ingester.py

import os
import yaml
import pytest
import tables
import numpy as np
import pandas as pd
import shutil
from pathlib import Path
from asammdf import MDF

# Assumes your ingester code is in a 'data_pipeline' package and you have
# installed it with 'pip install -e .'
from data_pipeline.ingestion.mf4_ingestor import MF4Ingester
from data_pipeline.ingestion.base_ingestor import BaseIngester


@pytest.fixture(scope="module")
def test_environment(tmpdir_factory):
    """
    A pytest fixture that runs ONCE for this test module. It:
    1.  Defines robust paths relative to the test file's location.
    2.  Checks for and copies a REAL sample MF4 file into a temporary directory.
    3.  Creates the YAML layout file.
    4.  Runs the MF4Ingester on the temporary data.
    5.  Yields the necessary paths and config for the test functions.
    6.  Cleans up everything automatically after the tests are done.
    """
    
    tests_dir = Path(__file__).parent
    project_root = tests_dir.parent
    
    sample_data_dir = project_root / "sample_data/input/mf4"
    source_mf4_path = sample_data_dir / "rec2_006.mf4" 

    if not source_mf4_path.exists():
        pytest.skip(f"Sample data not found at '{source_mf4_path}'. Skipping tests.")
    
    base_dir = Path(tmpdir_factory.mktemp("mf4_test_run"))
    input_dir = base_dir / "input"
    output_dir = base_dir / "output"
    config_dir = base_dir / "config"
    input_dir.mkdir()
    output_dir.mkdir()
    config_dir.mkdir()

    test_mf4_path = input_dir / source_mf4_path.name
    shutil.copy(source_mf4_path, test_mf4_path)
    
    layout_yaml_path = config_dir / "layout.yaml"
    yaml_content = """
    mapping:
      - source: mf4
        original_name: "Model Root/recorder/hi5/velocity_x_center_rear_axle_mps"
        target_name: /hi5/vehicle_data/velocity_x_center_rear_axle_mps
      - source: mf4
        original_name: "Model Root/recorder/hi5/hi5_timestamp"
        target_name: /hi5/vehicle_data/timestamp_s
      - source: mf4
        original_name: "Model Root/recorder/rfmu/brake_pressure_bar"
        target_name: /rfmu/vehicle_data/brake_pressure_bar
      - source: mf4
        original_name: "Model Root/recorder/rfmu/timestamp_ptp"
        target_name: /rfmu/vehicle_data/timestamp_s
    """
    layout_yaml_path.write_text(yaml_content)

    class MockStateManager:
        def get_unprocessed_items(self, items): return items
        def update_state(self, processed_items): pass

    ingester = MF4Ingester(
        input_folder=str(input_dir),
        output_folder=str(output_dir),
        state_manager=MockStateManager(),
        file_pattern="*.mf4",
        layout_yaml_path=str(layout_yaml_path)
    )
    ingester.run()

    output_h5_filename = test_mf4_path.with_suffix(".h5").name
    output_h5_path = output_dir / output_h5_filename

    yield {
        "source_mf4": str(test_mf4_path),
        "output_h5": str(output_h5_path),
        "layout": yaml.safe_load(yaml_content)
    }


def test_file_creation(test_environment):
    """Check if the output HDF5 file was actually created."""
    output_h5_path = test_environment["output_h5"]
    assert os.path.exists(output_h5_path), "Output HDF5 file was not created."


def test_data_values_are_identical(test_environment):
    """
    Checks if the numerical values in the HDF5 file are identical to the
    source MF4 file.
    """
    source_mf4 = test_environment["source_mf4"]
    output_h5 = test_environment["output_h5"]
    layout = test_environment["layout"]

    with MDF(source_mf4) as mdf, tables.open_file(output_h5, "r") as h5:
        for mapping in layout["mapping"]:
            if mapping.get("source") != "mf4":
                continue

            original_channel_name = mapping["original_name"]
            target_hdf5_path = mapping["target_name"]

            try:
                source_signal = mdf.get(original_channel_name)
                source_values = pd.to_numeric(
                    source_signal.samples, errors="coerce"
                ).astype(np.float64)
            except Exception as e:
                pytest.fail(f"Could not read source channel '{original_channel_name}' from MF4: {e}")

            try:
                parent_group_path = '/' + '/'.join(target_hdf5_path.strip('/').split('/')[:-1])
                
                column_name = target_hdf5_path.strip('/').split('/')[-1]

                table_node = h5.get_node(parent_group_path, 'measurements')
                
                output_values = table_node.col(column_name)

            except Exception as e:
                pytest.fail(f"Could not read target data for '{original_channel_name}' from HDF5: {e}")
            
            np.testing.assert_allclose(
                source_values,
                output_values,
                rtol=1e-7,
                atol=0,
                equal_nan=True,
                err_msg=f"Data mismatch for channel '{original_channel_name}'"
            )