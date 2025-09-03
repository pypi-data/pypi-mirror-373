# -*- coding: utf-8 -*-

"""Shared data merging utilities for both Robot and PyATS test execution."""

from pathlib import Path
from typing import List, Dict, Any
from nac_yaml import yaml
import logging

logger = logging.getLogger(__name__)


class DataMerger:
    """Handles merging of YAML data files for both Robot and PyATS test execution."""

    @staticmethod
    def merge_data_files(data_paths: List[Path]) -> Dict[str, Any]:
        """Load and merge YAML files from provided paths.

        Args:
            data_paths: List of paths to YAML files to merge

        Returns:
            Merged dictionary containing all data from the YAML files
        """
        logger.info("Loading yaml files from %s", data_paths)
        data = yaml.load_yaml_files(data_paths)
        # Ensure we always return a dict, even if yaml returns None
        return data if isinstance(data, dict) else {}

    @staticmethod
    def write_merged_data_model(
        data: Dict[str, Any],
        output_directory: Path,
        filename: str = "merged_data_model_test_variables.yaml",
    ) -> None:
        """Write merged data model to YAML file.

        Args:
            data: The merged data dictionary to write
            output_directory: Directory where the YAML file will be saved
            filename: Name of the output YAML file
        """
        full_output_path = output_directory / filename
        logger.info("Writing merged data model to %s", full_output_path)
        yaml.write_yaml_file(data, full_output_path)

    @staticmethod
    def load_yaml_file(file_path: Path) -> Dict[str, Any]:
        """Load a single YAML file from the provided path.

        Args:
            file_path: Path to the YAML file to load

        Returns:
            Loaded dictionary from the YAML file
        """
        logger.info("Loading yaml file from %s", file_path)
        data = yaml.load_yaml_files([file_path])
        return data if data is not None else {}
