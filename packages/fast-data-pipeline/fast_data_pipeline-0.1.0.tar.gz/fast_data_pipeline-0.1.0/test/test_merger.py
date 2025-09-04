import pytest
import h5py
import numpy as np
from data_pipeline.processing.hdf5_merger import (
    get_time_intervals,
    match_files_by_overlap,
)

test_scenarios = [
    ("rec_inside_rosbag", {"rec": [(100, 200)], "rosbag": [(50, 250)]}, 1),
    ("rosbag_inside_rec", {"rec": [(50, 250)], "rosbag": [(100, 200)]}, 1),
    (
        "partial_overlap_no_containment",
        {"rec": [(100, 200)], "rosbag": [(150, 250)]},
        0,
    ),
    ("no_overlap", {"rec": [(100, 200)], "rosbag": [(300, 400)]}, 0),
    ("identical_intervals", {"rec": [(100, 200)], "rosbag": [(100, 200)]}, 1),
    (
        "multiple_files_longest_wins",
        {"rec": [(110, 120), (300, 600)], "rosbag": [(50, 150), (250, 650)]},
        2,
    ),
    (
        "one_to_many_containment",
        {"rec": [(100, 150), (160, 190)], "rosbag": [(50, 250)]},
        1,
    ),
]


@pytest.mark.synchronization
@pytest.mark.parametrize(
    "test_name, test_environment, expected_matches",
    [(t[0], t[1], t[2]) for t in test_scenarios],
    indirect=["test_environment"],
    ids=[t[0] for t in test_scenarios],
)
def test_file_matching_scenarios(test_name, test_environment, expected_matches):
    """
    Tests various file matching scenarios using parametrized inputs.
    """
    env = test_environment
    rec_intervals = get_time_intervals(
        env["rec_folder"], "*.h5", env["table_path"], env["timestamp_column"]
    )
    rosbag_intervals = get_time_intervals(
        env["rosbag_folder"], "*.h5", env["table_path"], env["timestamp_column"]
    )
    matched_pairs = match_files_by_overlap(rec_intervals, rosbag_intervals)
    assert len(matched_pairs) == expected_matches


sync_test_data = {"rec": [(100.0, 110.0)], "rosbag": [(99.8, 110.2)]}


# @pytest.mark.synchronization
# @pytest.mark.parametrize("test_environment", [sync_test_data], indirect=True)
# # THE FIX IS HERE: Add 'test_environment' as an argument.
# def test_timestamp_synchronization(test_environment, merged_environment):
#     """
#     Ensures that the timestamps in the merged file are correctly aligned.
#     """
    
#     output_filepath = merged_environment

#     with h5py.File(output_filepath, "r") as hf:
#         final_rec_data = hf["rec_data"][:]
#         final_rosbag_data = hf["rosbag_data"][:]
#         ts_rec = final_rec_data["timestamp"]
#         ts_rosbag_synced = final_rosbag_data["timestamp"]
#         ts_rosbag_original = np.linspace(99.8, 110.2, 10)
#         insertion_indices = np.searchsorted(ts_rosbag_original, ts_rec)
#         insertion_indices[insertion_indices >= len(ts_rosbag_original)] = (
#             len(ts_rosbag_original) - 1
#         )
#         prev_indices = insertion_indices - 1
#         prev_indices[prev_indices < 0] = 0
#         diff1 = np.abs(ts_rosbag_original[insertion_indices] - ts_rec)
#         diff2 = np.abs(ts_rosbag_original[prev_indices] - ts_rec)
#         expected_indices = np.where(diff1 < diff2, insertion_indices, prev_indices)
#         expected_synced_timestamps = ts_rosbag_original[expected_indices]
#         np.testing.assert_array_almost_equal(
#             ts_rosbag_synced, expected_synced_timestamps, decimal=5
#         )
