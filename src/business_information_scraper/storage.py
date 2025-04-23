from abc import ABC, abstractmethod
from typing import List, Protocol
import csv
import json
import logging
# import sqlalchemy # If using DB

from business_information_scraper.data_models import BusinessInfo

logger = logging.getLogger(__name__)


class DataStorage(Protocol):
    """Defines the interface for data storage implementations."""
    def save(self, data: List[BusinessInfo]) -> None:
        ...

    def setup(self) -> None:
         """Optional: Perform any setup needed (e.g., create table)."""
         pass

class CsvStorage:
    def __init__(self, file_path: str):
        self.file_path = file_path
        logger.info(f"Initializing CSV storage at: {self.file_path}")

    def setup(self) -> None:
        # Write header if file doesn't exist or is empty
        try:
            with open(self.file_path, 'a', newline='', encoding='utf-8') as f:
                if f.tell() == 0:
                    writer = csv.writer(f)
                    # Get headers from Pydantic model
                    writer.writerow(BusinessInfo.model_fields.keys())
                    logger.info(f"CSV header written to {self.file_path}")
        except IOError as e:
             logger.error(f"Error during CSV setup for {self.file_path}: {e}", exc_info=True)
             raise

    def save(self, data: List[BusinessInfo]) -> None:
        logger.info(f"Saving {len(data)} records to CSV: {self.file_path}")
        try:
            with open(self.file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for item in data:
                    # Convert Pydantic model to dict for CSV writing
                    writer.writerow(item.model_dump(mode='python').values()) # Use 'python' mode for correct types if needed
            logger.info(f"Successfully saved {len(data)} records.")
        except IOError as e:
            logger.error(f"Error saving data to CSV {self.file_path}: {e}", exc_info=True)
            # Decide on error handling: raise, log and continue?
        except Exception as e:
             logger.error(f"Unexpected error saving to CSV: {e}", exc_info=True)


def get_storage_strategy(storage_type: str, **kwargs) -> DataStorage:
    """Factory function to get the configured storage strategy."""
    if storage_type.lower() == 'csv':
        if 'file_path' not in kwargs:
            raise ValueError("Missing 'file_path' for CSV storage")
        return CsvStorage(kwargs['file_path'])
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")
