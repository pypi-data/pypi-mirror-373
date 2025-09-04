import os
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import yaml
from tqdm import tqdm
logger = logging.getLogger(__name__)


class BaseIngester(ABC):
    """
    Abstract base class for data ingestion pipelines.

    This class defines a common interface for discovering raw data files,
    processing them, and saving them into a standardized format. It is
    designed to work with a state manager to avoid reprocessing files.
    """

    def __init__(
        self,
        input_folder: str,
        output_folder: str,
        state_manager,
        layout_yaml_path: Optional[str] = None,
    ):
        """
        Initializes the ingester.

        Args:
            input_folder: The directory containing the raw source files.
            output_folder: The directory where processed files will be saved.
            state_manager: An instance of a StateManager class.
            layout_yaml_path (Optional): The path to a YAML file describing the
                                         output HDF5 file layout.
        """
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.state_manager = state_manager
        self.layout_spec = (
            self._parse_layout_yaml(layout_yaml_path) if layout_yaml_path else None
        )

        os.makedirs(self.input_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)

    def _parse_layout_yaml(self, yaml_path: str) -> Dict[str, Any]:
        """
        Parses the layout YAML file to guide HDF5 creation. This method is
        common to any ingester that creates a configurable HDF5 file.
        """
        if not os.path.exists(yaml_path):
            logger.error(f"Layout YAML not found at: {yaml_path}")
            raise FileNotFoundError(f"Layout YAML not found at: {yaml_path}")
        with open(yaml_path, "r") as f:
            spec = yaml.safe_load(f)
        logger.info(f"Successfully loaded layout specification from {yaml_path}")
        return spec

    @abstractmethod
    def discover_files(self) -> List[str]:
        """
        Scans the input directory to find all potential source files.
        This method must be implemented by each subclass.

        Returns:
            A list of absolute paths to the source files or folders.
        """
        pass

    @abstractmethod
    def process_file(self, file_path: str) -> bool:
        """
        Processes a single source file/folder and saves the result.
        This method must be implemented by each subclass.

        Args:
            file_path: The absolute path to the source file or folder.

        Returns:
            True if processing was successful, False otherwise.
        """
        pass

    def run(self):
        """
        Orchestrates the entire ingestion process for the data source.

        It discovers all potential files, filters out those that have already
        been processed, processes the new files, and updates the state log
        with any files that were successfully processed.
        """
        logger.info(f"--- Running {self.__class__.__name__} ---")
        logger.info(f"Input folder: {self.input_folder}")
        logger.info(f"Output folder: {self.output_folder}")

        all_files = self.discover_files()
        new_files = self.state_manager.get_unprocessed_items(all_files)

        if not new_files:
            logger.info("No new files found to process.")
            return

        logger.info(f"Found {len(new_files)} new files to process.")
        successfully_processed = []
        
        for file_path in tqdm(new_files, desc=f"Processing {self.__class__.__name__}"):
            try:
                if self.process_file(file_path):
                    successfully_processed.append(file_path)
                    logger.debug(f"Successfully processed: {os.path.basename(file_path)}")
                else:
                    logger.error(f"Failed to process: {os.path.basename(file_path)}")
            except Exception as e:
                logger.critical(
                    f"An unexpected error occurred while processing {file_path}: {e}",
                    exc_info=True,
                )

        if successfully_processed:
            self.state_manager.update_state(successfully_processed)
            logger.info(
                f"Updated state with {len(successfully_processed)} newly processed files."
            )
        logger.info(f"--- {self.__class__.__name__} finished ---")
