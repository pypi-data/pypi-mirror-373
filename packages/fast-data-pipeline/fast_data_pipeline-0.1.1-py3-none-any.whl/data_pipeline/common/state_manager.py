import os
import pickle
import logging
from typing import Set, List

logger = logging.getLogger(__name__)

class StateManager:
    """Manages the state of processed files to prevent redundant work."""
    def __init__(self, output_folder: str, state_filename: str = "processed_log.pkl"):
        self.log_path = os.path.join(output_folder, state_filename)
        self.processed_items = self._load_state()

    def _load_state(self) -> Set[str]:
        """Loads the set of processed item names from the log file."""
        if not os.path.exists(self.log_path):
            return set()
        try:
            with open(self.log_path, "rb") as f:
                if os.path.getsize(self.log_path) > 0:
                    return pickle.load(f)
                return set()
        except (pickle.UnpicklingError, EOFError) as e:
            logger.warning(f"Could not read log at {self.log_path}. Re-initializing. Error: {e}")
            return set()

    def get_unprocessed_items(self, all_item_paths: List[str]) -> List[str]:
        """Filters a list of all items against the set of processed items."""
        all_item_names = {os.path.basename(p) for p in all_item_paths}
        processed_names = {os.path.basename(p) for p in self.processed_items}
        unprocessed_names = sorted(list(all_item_names - processed_names))
        
        path_map = {os.path.basename(p): p for p in all_item_paths}
        
        return [path_map[name] for name in unprocessed_names]

    def update_state(self, new_items: List[str]):
        """Adds new successfully processed items to the state and saves."""
        self.processed_items.update(new_items)
        try:
            with open(self.log_path, "wb") as f:
                pickle.dump(self.processed_items, f)
        except Exception as e:
            logger.critical(f"CRITICAL: Failed to write state file to {self.log_path}: {e}")
            raise