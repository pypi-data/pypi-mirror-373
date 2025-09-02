from __future__ import annotations
from typing import Any

from ewokscore import Task
from ewokscore.missing_data import MissingData
from esrf_pathlib import Path
import logging
from pyicat_plus.client.main import IcatClient
from pyicat_plus.client import defaults

logger = logging.getLogger(__name__)


def parse_processed_path(folder_path: str):
    """
    Parse an ESRF PROCESSED_DATA path and extract:
      - proposal, beamline, sample_name, dataset
    Raises ValueError if path is not under PROCESSED_DATA or structure is invalid.
    """
    processed_path = Path(folder_path)
    if processed_path.data_type != "PROCESSED_DATA":
        raise ValueError(f"Path is not PROCESSED_DATA: {processed_path}")

    parts = processed_path.parts
    try:
        idx = parts.index("PROCESSED_DATA")
        sample_name = parts[idx + 1]
        dataset = parts[idx + 2]
    except (ValueError, IndexError):
        raise ValueError(f"Invalid PROCESSED_DATA structure: {processed_path}")

    return processed_path.proposal, processed_path.beamline, sample_name, dataset


def construct_raw_path(processed_path: Path, sample_name: str, dataset: str) -> Path:
    """
    Given an ESRF PROCESSED_DATA Path and sample/dataset, construct the
    corresponding RAW_DATA/<sample_name>/<dataset> Path.
    """
    parts = processed_path.parts
    idx = parts.index("PROCESSED_DATA")
    base_parts = parts[:idx]
    raw_parts = base_parts + ("RAW_DATA", sample_name, dataset)
    return Path(*raw_parts)


def prepare_metadata(
    input_metadata: MissingData | dict[str, Any], sample_name: str
) -> dict[str, Any]:
    """
    Validate or generate metadata dict. If input_metadata is MissingData,
    return {{"Sample_name": sample_name}}.
    """
    if isinstance(input_metadata, MissingData):
        return {"Sample_name": sample_name}
    if "Sample_name" not in input_metadata:
        raise ValueError("Metadata dict must include 'Sample_name'.")
    return input_metadata


def store_processed_data_to_icat(
    proposal: str,
    beamline: str,
    dataset: str,
    processed_path: Path,
    raw_path: Path,
    metadata: dict,
):
    """
    Instantiate IcatClient and store processed data, ensuring disconnect.
    """
    client = IcatClient(metadata_urls=defaults.METADATA_BROKERS)
    try:
        client.store_processed_data(
            beamline=beamline,
            proposal=proposal,
            dataset=dataset,
            path=str(processed_path),
            raw=[str(raw_path)],
            metadata=metadata,
        )
    finally:
        try:
            client.disconnect()
        except Exception:
            logger.warning("Failed to disconnect ICAT client")


class DataPortalUpload(
    Task, input_names=["process_folder_path"], optional_input_names=["metadata"]
):
    """
    Task that uploads a data folder to the Data Portal using pyicat_plus.
    Uses helper functions for parsing paths, metadata, and upload.
    """

    def run(self):
        folder_path = self.inputs.process_folder_path
        metadata_in = getattr(self.inputs, "metadata", MissingData())

        try:
            proposal, beamline, sample, dataset = parse_processed_path(folder_path)
            processed_path = Path(folder_path)
            raw_path = construct_raw_path(processed_path, sample, dataset)
            metadata = prepare_metadata(metadata_in, sample)
            store_processed_data_to_icat(
                proposal, beamline, dataset, processed_path, raw_path, metadata
            )
        except ValueError as e:
            logger.warning("DataPortalUpload skipped: %s", e)
        except Exception as e:
            logger.warning("Error in DataPortalUpload: %s", e)
