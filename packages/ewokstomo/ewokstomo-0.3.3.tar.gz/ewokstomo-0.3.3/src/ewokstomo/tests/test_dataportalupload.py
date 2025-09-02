import pytest

from ewokstomo.tasks import dataportalupload
from esrf_pathlib import Path


def test_parse_processed_path_happy_case():
    p = "/data/visitor/ma0000/id00/20250101/PROCESSED_DATA/sample/sample_dataset"
    proposal, beamline, sample, dataset = dataportalupload.parse_processed_path(p)
    assert proposal == "ma0000"
    assert beamline == "id00"
    assert sample == "sample"
    assert dataset == "sample_dataset"


def test_parse_processed_path_not_processed_data_raises():
    with pytest.raises(ValueError, match="Path is not PROCESSED_DATA"):
        dataportalupload.parse_processed_path(
            "/data/visitor/ma0000/id00/20250101/RAW_DATA/sample/sample_dataset"
        )


@pytest.mark.parametrize(
    "path",
    [
        "/data/visitor/ma0000/id00/20250101/PROCESSED_DATA",  # no sample/dataset
        "/data/visitor/ma0000/id00/20250101/PROCESSED_DATA/sample_only",  # no dataset
    ],
)
def test_parse_processed_path_invalid_structure_raises(path):
    with pytest.raises(ValueError, match="Invalid PROCESSED_DATA structure"):
        dataportalupload.parse_processed_path(path)


def test_construct_raw_path_basic():
    processed = Path(
        "/data/visitor/ma0000/id00/20250101/PROCESSED_DATA/sample/sample_dataset/process"
    )
    out = dataportalupload.construct_raw_path(processed, "sample", "sample_dataset")
    # Should replace PROCESSED_DATA → RAW_DATA, keep the same base parts before
    assert isinstance(out, Path)
    assert out.parts == (
        "/",
        "data",
        "visitor",
        "ma0000",
        "id00",
        "20250101",
        "RAW_DATA",
        "sample",
        "sample_dataset",
    )


def test_prepare_metadata_missing_key_raises():
    with pytest.raises(ValueError, match="Metadata dict must include 'Sample_name'"):
        dataportalupload.prepare_metadata({"test": "test"}, "test_sample")


def test_prepare_metadata_valid_dict_returns_same():
    data = {"Sample_name": "foo", "foo": "bar"}
    out = dataportalupload.prepare_metadata(data, "should_not_be_used")
    assert out is data


def test_prepare_metadata_missing_data_returns_sample_name():
    missing = dataportalupload.MissingData()
    result = dataportalupload.prepare_metadata(missing, "my_sample")
    assert result == {"Sample_name": "my_sample"}
