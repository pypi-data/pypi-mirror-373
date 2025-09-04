import numpy as np
import h5py

def default_metadata_adder(merged_file_path: str) -> bool:
    """
    Adds metadata to the merged file using the exact, known paths for the
    required datasets.
    """
    try:
        with h5py.File(merged_file_path, 'a') as f:
            
            timestamp_path = "/hi5/vehicle_data/timestamp_s"
            condition_path = "/rfmu/vehicle_data/road_condition"
            surface_path = "/rfmu/vehicle_data/road_surface"

            if timestamp_path not in f:
                print(f"   - Primary timestamp dataset not found at the expected path: {timestamp_path}")
                return False
            
            timestamp_dataset = f[timestamp_path]
            first_timestamp = float(timestamp_dataset[0]['value'])
            seconds = int(first_timestamp)
            nanoseconds = int((first_timestamp - seconds) * 1e9)

            def get_unique_values(dset_path: str) -> str:
                if dset_path not in f:
                    print(f"   - Info: Metadata dataset not found at '{dset_path}', skipping.")
                    return ""
                
                dataset = f[dset_path]
                if dataset.shape[0] == 0:
                    return ""

                values = dataset[:]
                unique_vals = np.unique(values)
                return ", ".join([x.decode() if isinstance(x, bytes) else str(x) for x in unique_vals])

            road_condition_str = get_unique_values(condition_path)
            road_surface_str = get_unique_values(surface_path)

            #TODO
            #for some reason writing metadata into attributes does not work
            meta_group = f.require_group("metadata") 
            #meta_group.attrs["measurement_id"] = f"{seconds}_{nanoseconds}"
            #meta_group.attrs["measurement_datetime"] = first_timestamp
            #meta_group.attrs["road_surface_type"] = road_surface_str
            #meta_group.attrs["road_condition_type"] = road_condition_str

            measurement_id_str = f"{seconds}_{nanoseconds}"
            meta_group.create_dataset("measurement_id", data=measurement_id_str)

            meta_group.create_dataset("measurement_datetime", data=first_timestamp)
            meta_group.create_dataset("road_surface_type", data=road_surface_str)
            meta_group.create_dataset("road_condition_type", data=road_condition_str)

            f.flush()

            return True

    except TypeError as e:
        print(f"   - A TypeError occurred, likely due to a structured data mismatch: {e}")
        print("   - This usually means a dataset field (e.g., ['value']) was not accessed correctly.")
        return False
    except Exception as e:
        print(f"   - An unexpected error occurred while adding metadata: {e}")
        return False