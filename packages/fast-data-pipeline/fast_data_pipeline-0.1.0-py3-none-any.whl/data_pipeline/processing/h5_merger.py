"""Merges HDF5 files by combining their top-level groups.

This script automates the process of finding pairs of HDF5 files (referred
to as 'rec' and 'rosbag' files) from specified folders. It matches these
files based on their time intervals to find corresponding pairs.

For each matched pair, it creates a new HDF5 file that contains all the
top-level groups from both of the original files. For example, if one file
has a '/perception' group and the other has a '/vehicle_data' group, the
merged file will contain both.

The script maintains a log of processed files to avoid re-processing on
subsequent runs.
"""

import h5py
import numpy as np
import glob
import os
from typing import List, Dict, Tuple, Set
import pickle
from .metadata_functions import default_metadata_adder


def merge_hdf5_files(file1: str, file2: str, output_path: str):
    """
    Merges two HDF5 files. On dataset conflict, renames the original dataset
    with a '_rec' suffix and adds the new one with a '_ros' suffix.
    """
    with h5py.File(file1, 'r') as f1, \
         h5py.File(file2, 'r') as f2, \
         h5py.File(output_path, 'w') as out:

        print(f" - Copying from {os.path.basename(file1)}...")
        copy_h5_structure(f1, out, '/')

        print(f" - Merging from {os.path.basename(file2)}...")
        merge_h5_structure(f2, out, '/', rec_suffix="rec", ros_suffix="ros")

def copy_h5_structure(source, dest, current_path):
    """Recursively copies HDF5 structure from source to destination."""
    for name, item in source.items():
        item_path = os.path.join(current_path, name)
        
        if isinstance(item, h5py.Group):
            dest.create_group(item_path)
            copy_h5_structure(item, dest, item_path)
        else:
            dset = dest.create_dataset(item_path, data=item[()])
            for attr_name, attr_value in item.attrs.items():
                dset.attrs[attr_name] = attr_value

def merge_h5_structure(source, dest, current_path, rec_suffix, ros_suffix):
    """
    Recursively merges, renaming conflicting DATASETS with suffixes.
    """
    for name, item in source.items():
        item_path = os.path.join(current_path, name)
        
        if isinstance(item, h5py.Group):
            if item_path not in dest:
                dest.create_group(item_path)
            merge_h5_structure(item, dest, item_path, rec_suffix, ros_suffix)
        else: 
            if item_path in dest:
                renamed_rec_path = f"{item_path}_{rec_suffix}"
                print(f"   - Conflict on '{name}'. Renaming original to '{name}_{rec_suffix}'")
                dest.move(item_path, renamed_rec_path)
                
                new_ros_path = f"{item_path}_{ros_suffix}"
                print(f"   - Storing new as '{name}_{ros_suffix}'")
                dset = dest.create_dataset(new_ros_path, data=item[()])
                for attr_name, attr_value in item.attrs.items():
                    dset.attrs[attr_name] = attr_value
            else:
                dset = dest.create_dataset(item_path, data=item[()])
                for attr_name, attr_value in item.attrs.items():
                    dset.attrs[attr_name] = attr_value

def get_time_intervals(
    folder: str, file_regex: str, dataset_spec: str
) -> Dict[str, Tuple[float, float]]:
    """
    Extracts start and end timestamps from HDF5 files.
    Handles both simple datasets (e.g., "/path/to/dataset") and
    structured datasets (e.g., "/path/to/dataset::field_name").
    """
    filepaths = glob.glob(f"{folder}/{file_regex}")
    time_intervals = {}

    if "::" in dataset_spec:
        dataset_path, field_name = dataset_spec.split("::", 1)
        is_structured = True
    else:
        dataset_path = dataset_spec
        field_name = None
        is_structured = False

    for path in filepaths:
        try:
            with h5py.File(path, "r") as hf5_file:
                if dataset_path not in hf5_file:
                    print(f"Warning: Dataset '{dataset_path}' not found in {path}")
                    continue

                dataset = hf5_file[dataset_path]

                if len(dataset) == 0:
                    print(f"Warning: Dataset '{dataset_path}' in {path} is empty")
                    continue

                if is_structured:
                    if not hasattr(dataset.dtype, 'fields') or field_name not in dataset.dtype.fields:
                        print(f"Warning: Field '{field_name}' not found in dataset '{dataset_path}' in {path}")
                        continue
                    start_time = float(dataset[0][field_name])
                    end_time = float(dataset[-1][field_name])
                else:
                    start_time = float(dataset[0])
                    end_time = float(dataset[-1])

                time_intervals[path] = (start_time, end_time)

        except (KeyError, IOError, ValueError, IndexError) as e:
            print(f"Warning: Could not process {path}. Error: {e}")

    return time_intervals


def load_processed_log(log_path: str) -> Set[str]:
    """Loads a set of processed file paths from a pickle log file."""
    if not os.path.exists(log_path):
        return set()
    try:
        with open(log_path, "rb") as f:
            if os.path.getsize(log_path) > 0:
                return pickle.load(f)
            return set()
    except (pickle.UnpicklingError, EOFError) as e:
        print(f"Warning: Could not read pickle log at {log_path}. Error: {e}")
        return set()


def update_processed_log(
    log_path: str, processed_set: Set[str], filepath1: str, filepath2: str
):
    """Adds newly processed file paths to the log and saves it."""
    processed_set.add(filepath1)
    processed_set.add(filepath2)
    with open(log_path, "wb") as f:
        pickle.dump(processed_set, f)


def filter_unprocessed_files(
    rec_intervals: Dict[str, Tuple[float, float]],
    rosbag_intervals: Dict[str, Tuple[float, float]],
    processed_paths: Set[str],
) -> Tuple[Dict[str, Tuple[float, float]], Dict[str, Tuple[float, float]]]:
    """Filters out files that have already been processed."""
    unprocessed_rec = {
        p: t for p, t in rec_intervals.items() if p not in processed_paths
    }
    unprocessed_rosbag = {
        p: t for p, t in rosbag_intervals.items() if p not in processed_paths
    }
    return unprocessed_rec, unprocessed_rosbag


def match_files_by_overlap(
    files1_intervals: Dict[str, Tuple[float, float]],
    files2_intervals: Dict[str, Tuple[float, float]],
) -> List[Tuple[str, str]]:
    """Matches pairs of files from two groups based on the longest time overlap where one is contained within the other."""
    if not files1_intervals or not files2_intervals:
        return []

    potential_matches = []
    for path1, (start1, end1) in files1_intervals.items():
        for path2, (start2, end2) in files2_intervals.items():
            if start2 <= start1 and end1 <= end2:
                potential_matches.append(((path1, path2), end1 - start1))
            elif start1 <= start2 and end2 <= end1:
                potential_matches.append(((path1, path2), end2 - start2))

    potential_matches.sort(key=lambda x: x[1], reverse=True)

    matched_pairs = []
    used_files = set()
    for (path1, path2), duration in potential_matches:
        if path1 not in used_files and path2 not in used_files:
            matched_pairs.append((path1, path2))
            used_files.add(path1)
            used_files.add(path2)
            print(
                f"-> Match found: {os.path.basename(path1)} and {os.path.basename(path2)} (Contained duration: {duration:.3f}s)"
            )

    return matched_pairs

def main(metadata_adder=default_metadata_adder):
    """
    Main function to discover, match, and merge HDF5 files.
    """

    def print_h5_structure(filepath: str):
        """Prints all object paths within an HDF5 file for verification."""
        print(f"\n--- Structure of {os.path.basename(filepath)} ---")
        try:
            with h5py.File(filepath, 'r') as f:
                f.visit(lambda name: print(f"   - {name}"))
        except Exception as e:
            print(f"Could not read file structure: {e}")
        print("--- End of Structure ---\n")

    # --- Configuration ---
    REC_FOLDER = "/mnt/sambashare/ugglf/output/latest"
    ROSBAG_FOLDER = "/mnt/sambashare/ugglf/output/latest"
    OUTPUT_FOLDER = "/mnt/sambashare/ugglf/output/sync_output"
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    REC_TIMESTAMP_SPEC = "hi5/vehicle_data/timestamp_s::value"
    ROSBAG_TIMESTAMP_SPEC = "hi5/perception/synced_camera_lidar/timestamp_s"

    rec_glob_pattern = "rec*.h5"
    rosbag_glob_pattern = "rosbag2*.h5"

    LOG_FILE_PATH = os.path.join(OUTPUT_FOLDER, "processed_files.pkl")
    processed_files_set = load_processed_log(LOG_FILE_PATH)
    print(
        f"Loaded {len(processed_files_set)} previously processed file paths from log.\n"
    )

    # --- Stage 1: Discovering all files and their time intervals ---
    print("--- Stage 1: Discovering all files and their time intervals ---")
    all_rec_intervals = get_time_intervals(
        REC_FOLDER, rec_glob_pattern, REC_TIMESTAMP_SPEC
    )
    all_rosbag_intervals = get_time_intervals(
        ROSBAG_FOLDER, rosbag_glob_pattern, ROSBAG_TIMESTAMP_SPEC
    )

    rec_intervals, rosbag_intervals = filter_unprocessed_files(
        all_rec_intervals, all_rosbag_intervals, processed_files_set
    )
    print(
        f"Found {len(rec_intervals)} new rec files and {len(rosbag_intervals)} new rosbag files to process.\n"
    )

    # --- Stage 2: Matching new files by longest contained overlap ---
    print("--- Stage 2: Matching new files by longest contained overlap ---")
    matched_pairs = match_files_by_overlap(rec_intervals, rosbag_intervals)
    print(f"\nFound {len(matched_pairs)} new valid file pairs to process.\n")

    # --- Stage 3: Merging matched pairs ---
    print("--- Stage 3: Merging matched pairs ---")
    if not matched_pairs:
        print("No new matched pairs found to merge.")
    else:
        success_count = 0
        for rec_path, rosbag_path in matched_pairs:
            rec_basename = os.path.basename(rec_path).replace(".h5", "")
            output_filename = f"merged_{rec_basename}.h5"  # Using .h5 extension
            output_file_path = os.path.join(OUTPUT_FOLDER, output_filename)

            try:
                # Step 1: Merge the files for the current pair
                merge_hdf5_files(
                    file1=rec_path,
                    file2=rosbag_path,
                    output_path=output_file_path,
                )
                print(f"   - Merge successful: Created {output_filename}")

                # Step 2: Add metadata to the newly created file
                if metadata_adder:
                    print(f"   - Adding metadata to {output_filename}...")
                    if metadata_adder(output_file_path):
                        print("   - Metadata added successfully.")
                        success_count += 1
                        update_processed_log(
                            LOG_FILE_PATH, processed_files_set, rec_path, rosbag_path
                        )
                        #print_h5_structure(output_file_path)
                    else:
                        print("   - Metadata addition failed. Cleaning up.")
                        os.remove(output_file_path)
                else:
                    # If no metadata function is provided, count as success
                    success_count += 1
                    update_processed_log(
                        LOG_FILE_PATH, processed_files_set, rec_path, rosbag_path
                    )

            except Exception as e:
                print(f"   - CRITICAL ERROR while processing {output_filename}: {e}")
                # Clean up partially created file on a critical error
                if os.path.exists(output_file_path):
                    os.remove(output_file_path)

        print(f"\nSuccessfully processed {success_count} out of {len(matched_pairs)} pairs.")


if __name__ == "__main__":
    

    main()

    