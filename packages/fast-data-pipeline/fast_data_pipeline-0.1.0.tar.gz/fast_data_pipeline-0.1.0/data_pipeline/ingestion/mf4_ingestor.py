import os
import logging
import yaml
from typing import Dict, List, Any, Optional, Type, Tuple

import numpy as np
import pandas as pd
import tables
from asammdf import MDF


from .base_ingestor import BaseIngester

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MF4Ingester(BaseIngester):
    """Ingests MF4 files based on a YAML layout and saves them to HDF5.

    This class discovers MF4 files in a specified input directory, extracts
    data for channels defined in a YAML layout file, and saves the processed
    data into HDF5 files. The HDF5 file structure is dynamically determined
    by the same YAML layout specification, with each signal being saved to its
    own dataset.

    Attributes:
        file_pattern (str): The glob pattern to match MF4 files.
        channel_mapper (Dict[str, str]): A mapping from the original channel
            name in the MF4 file to the desired column name in the HDF5 file.
    """

    def __init__(
        self,
        input_folder: str,
        output_folder: str,
        state_manager,
        file_pattern: str,
        layout_yaml_path: str,
    ):
        """Initializes the MF4Ingester.

        Args:
            input_folder (str): The path to the directory containing input MF4 files.
            output_folder (str): The path to the directory where HDF5 files will be saved.
            state_manager: An object responsible for tracking processed files.
                It must have `get_unprocessed_items` and `update_state` methods.
            file_pattern (str): A file pattern (e.g., "*.mf4") to identify
                files to process within the input folder.
            layout_yaml_path (str): The path to the YAML file that defines the
                data mapping and HDF5 structure.
        """
        super().__init__(input_folder, output_folder, state_manager, layout_yaml_path)
        if "*" not in file_pattern:
            logger.warning(
                "file_pattern does not contain a wildcard '*'. It will only match exact filenames."
            )
        self.file_pattern = file_pattern
        self.channel_mapper = self._create_channel_mapper_from_layout()

    def _create_channel_mapper_from_layout(self) -> Dict[str, str]:
        """Creates a channel name mapping from the loaded YAML layout.

        This method parses the `mapping` section of the layout specification,
        extracting 'original_name' and 'target_name' for entries where the
        source is 'mf4'. It creates a dictionary that maps the source channel
        name to the final dataset name (the last part of the target path).

        Returns:
            Dict[str, str]: A dictionary mapping the original MF4 channel name
                to the target HDF5 dataset name.

        Raises:
            ValueError: If the layout specification is not loaded or is missing
                the 'mapping' key.
        """
        if not self.layout_spec or "mapping" not in self.layout_spec:
            raise ValueError("Layout specification is missing or invalid.")

        mapper = {}
        for mapping in self.layout_spec["mapping"]:
            if mapping.get("source") == "mf4":
                hdf5_path = mapping["target_name"]
                if isinstance(hdf5_path, list):
                    hdf5_path = hdf5_path[0]
                column_name = hdf5_path.split("/")[-1]
                mapper[mapping["original_name"]] = column_name

        logger.info(
            f"Dynamically created channel mapper with {len(mapper)} entries from layout."
        )
        return mapper

    def discover_files(self) -> List[str]:
        """Discovers MF4 files in the input folder that match the file pattern.

        Returns:
            List[str]: A list of absolute paths to the discovered files.
                Returns an empty list if the input directory is not found.
        """
        if not os.path.isdir(self.input_folder):
            logger.error(f"Input directory not found: {self.input_folder}")
            return []
        prefix = (
            self.file_pattern.split("*")[0]
            if "*" in self.file_pattern
            else self.file_pattern
        )
        suffix = self.file_pattern.split("*")[-1] if "*" in self.file_pattern else ""
        matched_files = [
            os.path.join(self.input_folder, f)
            for f in os.listdir(self.input_folder)
            if f.startswith(prefix)
            and f.endswith(suffix)
            and os.path.isfile(os.path.join(self.input_folder, f))
        ]
        return matched_files

    def process_file(self, file_path: str) -> bool:
        """Processes a single MF4 file.

        This method orchestrates the processing of a single MF4 file by
        extracting the relevant data and then saving it to an HDF5 file
        according to the loaded layout specification. It handles exceptions
        during the process and cleans up partially created output files.

        Args:
            file_path (str): The absolute path to the MF4 file to process.

        Returns:
            bool: True if the file was processed and saved successfully,
                False otherwise.
        """
        file_name = os.path.basename(file_path)
        output_name = os.path.splitext(file_name)[0] + ".h5"
        output_path = os.path.join(self.output_folder, output_name)

        try:
            extracted_data = self._extract_from_mf4(file_path)
            if not extracted_data:
                return False

            if self.layout_spec is None:
                logger.error("Cannot save file: Layout specification was not loaded.")
                return False

            return self._save_to_hdf5_by_layout(
                output_path, extracted_data, self.layout_spec
            )

        except Exception as e:
            logger.error(
                f"Unexpected error processing MF4 file {file_name}: {e}", exc_info=True
            )
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except OSError:
                    pass
            return False

    def _save_to_hdf5_by_layout(
        self,
        output_path: str,
        extracted_data: Dict[str, Any],
        layout_spec: Dict[str, Any],
    ) -> bool:
        """Saves extracted data to an HDF5 file, creating one dataset per signal.

        This method iterates through the layout specification and saves each
        signal into its own dataset within the HDF5 file. Regular signals are
        saved as a two-column table ('timestamp_s', 'value'). The 'HostService'
        signal is treated as a special case and saved as a simple 1D array of
        timestamps.

        Args:
            output_path (str): The path for the output HDF5 file.
            extracted_data (Dict[str, Any]): A dictionary containing the
                'timestamps' and a 'data' dictionary of signal arrays.
            layout_spec (Dict[str, Any]): The parsed YAML layout specification.

        Returns:
            bool: True if the save operation was successful, False otherwise.
        """
        logger.info(f"Writing signals to {output_path}.")

        try:
            with tables.open_file(
                output_path, mode="w", title=layout_spec.get("title", "Processed Data")
            ) as h5file:
                timestamps = extracted_data["timestamps"]

                for mapping in layout_spec["mapping"]:
                    if mapping.get("source") != "mf4":
                        continue

                    original_name = mapping["original_name"]
                    output_channel_name = self.channel_mapper.get(original_name)

                    if (
                        not output_channel_name
                        or output_channel_name not in extracted_data["data"]
                    ):
                        logger.warning(
                            f"--> SKIPPING '{original_name}' because its key ('{output_channel_name}') was not found in the extracted data dictionary."
                        )
                        continue

                    signal_data = extracted_data["data"][output_channel_name]
                    target_path = mapping["target_name"]

                    parts = target_path.strip("/").split("/")
                    parent_group = "/" + "/".join(parts[:-1]) if len(parts) > 1 else "/"
                    dataset_name = parts[-1]

                    if original_name == "HostService":
                        h5file.create_array(
                            where=parent_group,
                            name=dataset_name,
                            obj=signal_data,
                            title="Master HostService Timestamps",
                            createparents=True,
                        )
                        logger.info(
                            f"Successfully wrote {len(signal_data)} rows to standalone array '{target_path}'"
                        )
                    else:
                        num_rows = len(timestamps)
                        table_dtype = np.dtype(
                            [("timestamp_s", "f8"), ("value", signal_data.dtype)]
                        )
                        structured_array = np.empty(num_rows, dtype=table_dtype)
                        structured_array["timestamp_s"] = timestamps
                        structured_array["value"] = np.nan_to_num(signal_data)
                        h5file.create_table(
                            where=parent_group,
                            name=dataset_name,
                            obj=structured_array,
                            title=f"Data for {original_name}",
                            createparents=True,
                            filters=tables.Filters(complib="zlib", complevel=5),
                        )
                        logger.info(
                            f"Successfully wrote {len(structured_array)} rows to dataset '{target_path}'"
                        )
            return True
        except Exception as e:
            logger.error(
                f"Failed during PyTables write operation for {output_path}: {e}",
                exc_info=True,
            )
            if os.path.exists(output_path):
                os.remove(output_path)
            return False

    def _extract_from_mf4(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extracts specified channels from an MF4 file into NumPy arrays.

        Opens an MF4 file using `asammdf`, checks if all required channels are
        present, and extracts them into a pandas DataFrame. The DataFrame is
        then converted into a dictionary of NumPy arrays, with timestamps
        stored separately.

        Args:
            file_path (str): The path to the MF4 file.

        Returns:
            Optional[Dict[str, Any]]: A dictionary with 'timestamps' (a NumPy array)
                and 'data' (a dictionary mapping channel names to NumPy arrays).
                Returns None if extraction fails for any reason (e.g., file not
                found, missing channels, empty data).
        """
        logger.info(f"Attempting extraction from: {os.path.basename(file_path)}")
        channels_to_extract = list(self.channel_mapper.keys())

        if not channels_to_extract:
            logger.warning("Channel mapper is empty. Skipping.")
            return None

        try:
            with MDF(file_path, memory="low") as mdf_obj:
                if not self._check_channel_completeness(mdf_obj):
                    logger.warning(
                        f"Channel completeness check failed for {file_path}. Skipping."
                    )
                    return None

                df_intermediate = mdf_obj.to_dataframe(
                    channels=channels_to_extract,
                    time_from_zero=False,
                    time_as_date=False,
                    empty_channels="skip",
                )

                if df_intermediate.empty:
                    logger.warning(
                        f"DataFrame is empty after extraction for {file_path}. Skipping."
                    )
                    return None

                timestamps_np = df_intermediate.index.to_numpy(dtype=np.float64)
                numpy_data: Dict[str, np.ndarray] = {}

                for input_channel, output_channel in self.channel_mapper.items():
                    if input_channel in df_intermediate.columns:
                        col_data = pd.to_numeric(
                            df_intermediate[input_channel], errors="coerce"
                        ).to_numpy(dtype=np.float64)
                        numpy_data[output_channel] = col_data
                    else:
                        logger.warning(
                            f"Channel '{input_channel}' not in DataFrame for {file_path}."
                        )

                # After the loop, explicitly handle the case where HostService was the index.
                # This ensures it's added to numpy_data with the correct key from the mapper.
                host_service_key = self.channel_mapper.get("HostService")
                if host_service_key and host_service_key not in numpy_data:
                    logger.info(
                        f"Adding '{host_service_key}' to extracted data from the main timestamp index."
                    )
                    numpy_data[host_service_key] = timestamps_np

                if not numpy_data:
                    logger.error(
                        f"No channels successfully extracted for {file_path}. Skipping."
                    )
                    return None

                return {"timestamps": timestamps_np, "data": numpy_data}
        except FileNotFoundError:
            logger.error(f"Input file not found during extraction: {file_path}")
            return None
        except Exception as e:
            logger.error(
                f"Error during extraction for {os.path.basename(file_path)}: {e}",
                exc_info=True,
            )
            return None

    def _check_channel_completeness(self, mdf_obj: MDF) -> bool:
        """Checks if all required channels from the mapper exist in the MF4 file.

        Args:
            mdf_obj (MDF): An `asammdf.MDF` object representing the opened file.

        Returns:
            bool: True if all channels specified in `self.channel_mapper` are
                found in the MDF object, False otherwise.
        """
        mdf_channel_list = []
        for group in mdf_obj.groups:
            mdf_channel_list.extend(channel.name for channel in group.channels)

        logger.info(f"All available channels found in file: {sorted(mdf_channel_list)}")

        missing_channels = set(self.channel_mapper.keys()) - set(mdf_channel_list)
        if missing_channels:
            logger.warning(
                f"File is missing required channels: {sorted(list(missing_channels))}"
            )
            return False
        return True

    def _create_table_description(
        self, mdf_obj: MDF
    ) -> Tuple[Optional[Type[tables.IsDescription]], Optional[np.dtype]]:
        """DEPRECATED: Creates PyTables description and NumPy dtype.

        Note:
            This method is not used in the current implementation, which saves
            each signal to a separate dataset via `_save_to_hdf5_by_layout`.
            It was designed for an older approach that saved all signals to a
            single, wide HDF5 table.

        Creates both a PyTables `IsDescription` class and a NumPy `dtype` object
        dynamically based on the channels specified in the channel mapper and
        their data types in the MF4 file.

        Args:
            mdf_obj (MDF): An `asammdf.MDF` object to inspect for channel types.

        Returns:
            Tuple[Optional[Type[tables.IsDescription]], Optional[np.dtype]]: A tuple
                containing the dynamically created PyTables description class and the
                corresponding NumPy dtype object.
        """
        pytables_desc = {"timestamp_s": tables.Float64Col(pos=0)}
        numpy_dtype_list = [("timestamp_s", "f8")]
        col_pos = 1

        TYPE_MAP_PYTABLES = {
            np.dtype("bool"): tables.BoolCol,
            np.dtype("int8"): tables.Int8Col,
            np.dtype("uint8"): tables.UInt8Col,
            np.dtype("int16"): tables.Int16Col,
            np.dtype("uint16"): tables.UInt16Col,
            np.dtype("int32"): tables.Int32Col,
            np.dtype("uint32"): tables.UInt32Col,
            np.dtype("int64"): tables.Int64Col,
            np.dtype("uint64"): tables.UInt64Col,
            np.dtype("float32"): tables.Float32Col,
            np.dtype("float64"): tables.Float64Col,
        }

        TYPE_MAP_NUMPY = {
            np.dtype("bool"): "?",
            np.dtype("int8"): "i1",
            np.dtype("uint8"): "u1",
            np.dtype("int16"): "i2",
            np.dtype("uint16"): "u2",
            np.dtype("int32"): "i4",
            np.dtype("uint32"): "u4",
            np.dtype("int64"): "i8",
            np.dtype("uint64"): "u8",
            np.dtype("float32"): "f4",
            np.dtype("float64"): "f8",
        }

        for input_channel, output_channel in self.channel_mapper.items():
            try:
                signal = mdf_obj.get(input_channel)
                numpy_type = signal.samples.dtype

                ColType = TYPE_MAP_PYTABLES.get(numpy_type, tables.Float64Col)
                np_type_str = TYPE_MAP_NUMPY.get(numpy_type, "f8")

                pytables_desc[output_channel] = ColType(pos=col_pos)
                numpy_dtype_list.append((output_channel, np_type_str))
                col_pos += 1
            except Exception:
                pytables_desc[output_channel] = tables.Float64Col(pos=col_pos)
                numpy_dtype_list.append((output_channel, "f8"))
                col_pos += 1

        description_class = type(
            "MeasurementDescription", (tables.IsDescription,), pytables_desc
        )
        numpy_dtype = np.dtype(numpy_dtype_list)
        return description_class, numpy_dtype

    def _build_structured_array(
        self, numpy_dtype: np.dtype, timestamps: np.ndarray, data: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """DEPRECATED: Constructs a single NumPy structured array from data.

        Note:
            This method is not used in the current implementation. It was
            designed for an older approach that saved all signals to a single,
            wide HDF5 table.

        Combines timestamps and multiple signal data arrays into a single
        structured NumPy array, conforming to a specified dtype.

        Args:
            numpy_dtype (np.dtype): The target structured dtype for the array.
            timestamps (np.ndarray): An array of timestamps.
            data (Dict[str, np.ndarray]): A dictionary mapping channel names to
                their corresponding data arrays.

        Returns:
            np.ndarray: A single structured array containing all the data.
        """
        num_rows = len(timestamps)
        structured_array = np.empty(num_rows, dtype=numpy_dtype)

        structured_array["timestamp_s"] = timestamps

        for name, arr in data.items():
            if name in structured_array.dtype.names:
                target_dtype = structured_array.dtype[name]
                if np.issubdtype(target_dtype, np.integer) or np.issubdtype(
                    target_dtype, np.bool_
                ):
                    arr_filled = np.nan_to_num(arr, nan=0)
                    structured_array[name] = arr_filled.astype(target_dtype)
                else:
                    structured_array[name] = arr.astype(target_dtype)

        return structured_array

    def _save_to_hdf5(
        self,
        output_path: str,
        table_description: Type[tables.IsDescription],
        data: np.ndarray,
        layout_spec: Dict[str, Any],
    ) -> bool:
        """DEPRECATED: Saves a structured array to a single HDF5 table.

        Note:
            This method is not used in the current implementation, which saves
            each signal to a separate dataset via `_save_to_hdf5_by_layout`.
            It was designed for an older approach that saved all signals to a
            single, wide HDF5 table.

        Saves a structured NumPy array to a single table within an HDF5 file,
        using a dynamic layout from the YAML specification.

        Args:
            output_path (str): The path for the output HDF5 file.
            table_description (Type[tables.IsDescription]): The PyTables
                description class defining the table structure.
            data (np.ndarray): The structured NumPy array containing the data.
            layout_spec (Dict[str, Any]): The parsed YAML layout specification.

        Returns:
            bool: True if the save operation was successful, False otherwise.
        """
        logger.info(
            f"Attempting to write {len(data)} rows to {output_path} using specified layout."
        )

        main_mapping = layout_spec["mapping"][0]
        target_path = main_mapping["target_name"]

        if isinstance(target_path, list):
            target_path = target_path[0]

        parts = target_path.strip("/").split("/")
        group_path = "/" + "/".join(parts[:-1]) if len(parts) > 1 else "/"
        table_name = parts[-1]

        try:
            with tables.open_file(
                output_path, mode="w", title=layout_spec.get("title", "Processed Data")
            ) as h5file:
                if group_path != "/":
                    h5file.create_group(
                        h5file.root,
                        group_path.strip("/"),
                        "Data Group",
                        createparents=True,
                    )

                table = h5file.create_table(
                    where=group_path,
                    name=table_name,
                    description=table_description,
                    title=main_mapping.get("description", "Measurement Data"),
                    filters=tables.Filters(complib="zlib", complevel=5),
                )
                if len(data) > 0:
                    table.append(data)

                if "attributes" in main_mapping:
                    for attr_name, attr_value in main_mapping["attributes"].items():
                        table.attrs[attr_name] = attr_value

                table.flush()
            logger.info(f"Successfully wrote data to '{target_path}' in {output_path}")
            return True
        except Exception as e:
            logger.error(
                f"Failed during PyTables write operation for {output_path}: {e}",
                exc_info=True,
            )
            if os.path.exists(output_path):
                os.remove(output_path)
            return False


if __name__ == "__main__":

    class MockStateManager:
        def get_unprocessed_items(self, items):
            return items

        def update_state(self, processed_items):
            logger.info(f"StateManager would save: {processed_items}")

    # for testing inside the module, isolated unit test config
    # TEST_INPUT_DIR = "data-pipeline/sample_data/input/mf4"
    # TEST_OUTPUT_DIR = "data-pipeline/sample_data/output/mf4->hf5"
    # LAYOUT_YAML_PATH = "data-pipeline/configs/test.yaml"

    # for testing in the real data
    TEST_INPUT_DIR = "/mnt/sambashare/ugglf/2025-07-25/mf4"
    TEST_OUTPUT_DIR = "/mnt/sambashare/ugglf/output/latest"
    LAYOUT_YAML_PATH = "data-pipeline/configs/workaround_layout_spesification.yaml"

    os.makedirs(TEST_INPUT_DIR, exist_ok=True)
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

    logger.warning(
        f"This test requires a valid MF4 file in: {os.path.abspath(TEST_INPUT_DIR)}"
    )
    logger.warning(
        "The script will run but may fail at the extraction step if no valid file is found."
    )

    mf4_ingester = MF4Ingester(
        input_folder=TEST_INPUT_DIR,
        output_folder=TEST_OUTPUT_DIR,
        state_manager=MockStateManager(),
        file_pattern="*.mf4",
        layout_yaml_path=LAYOUT_YAML_PATH,
    )

    mf4_ingester.run()