import pytest
import os
import shutil
import h5py
import numpy as np

# --- Constants ---
TEST_DIR = "merger_test_data"
REC_FOLDER = os.path.join(TEST_DIR, "rec_files")
ROSBAG_FOLDER = os.path.join(TEST_DIR, "rosbag_files")
TABLE_PATH = "/test/table"
TIMESTAMP_COLUMN = "timestamp"

def create_test_h5_file(filepath: str, start_time: float, end_time: float, num_points: int = 10):
    """Helper function to create a simple HDF5 file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    timestamps = np.linspace(start_time, end_time, num_points, dtype=np.float64)
    data = np.zeros(num_points, dtype=[(TIMESTAMP_COLUMN, 'f8'), ('value', 'i4')])
    data[TIMESTAMP_COLUMN] = timestamps
    data['value'] = np.arange(num_points)
    with h5py.File(filepath, 'w') as f:
        f.create_dataset(TABLE_PATH, data=data)

@pytest.fixture
def test_environment(request):
    """A pytest fixture to set up and tear down a file-based test environment."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(REC_FOLDER)
    os.makedirs(ROSBAG_FOLDER)

    test_cases = request.param
    for i, interval in enumerate(test_cases.get("rec", [])):
        create_test_h5_file(os.path.join(REC_FOLDER, f"rec_{i}.h5"), interval[0], interval[1])
    for i, interval in enumerate(test_cases.get("rosbag", [])):
        create_test_h5_file(os.path.join(ROSBAG_FOLDER, f"rosbag_{i}.h5"), interval[0], interval[1])

    yield {
        "rec_folder": REC_FOLDER,
        "rosbag_folder": ROSBAG_FOLDER,
        "table_path": TABLE_PATH,
        "timestamp_column": TIMESTAMP_COLUMN
    }

    shutil.rmtree(TEST_DIR)