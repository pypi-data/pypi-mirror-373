import shutil
from pathlib import Path

import pytest

from ewokstomo.tasks.reducedarkflat import ReduceDarkFlat
from ewoks import execute_graph


def get_json_file(file_name: str) -> Path:
    from importlib.resources import path

    with path("ewokstomo.workflows", file_name) as p:
        return p


def get_data_dir(scan_name: str) -> Path:
    return Path(__file__).resolve().parents[0] / "data" / scan_name


@pytest.fixture
def tmp_dataset_path(tmp_path) -> Path:
    scan = "TestEwoksTomo_0010"
    src_dir = get_data_dir(scan)
    dst_dir = tmp_path / scan
    shutil.copytree(src_dir, dst_dir)
    for pattern in ("*_darks.hdf5", "*_flats.hdf5"):
        for f in dst_dir.glob(pattern):
            f.unlink()
    return dst_dir


@pytest.mark.order(1)
@pytest.mark.parametrize("Task", [ReduceDarkFlat])
def test_reducedarkflat_task(Task, tmp_dataset_path):
    nx_file = tmp_dataset_path / "TestEwoksTomo_0010.nx"
    expected_darks = tmp_dataset_path / "TestEwoksTomo_0010_darks.hdf5"
    expected_flats = tmp_dataset_path / "TestEwoksTomo_0010_flats.hdf5"
    assert not expected_darks.exists()
    assert not expected_flats.exists()
    task = Task(
        inputs={
            "nx_path": str(nx_file),
            "dark_reduction_method": "mean",
            "flat_reduction_method": "median",
            "overwrite": True,
            "return_info": False,
        },
    )
    task.run()
    assert Path(task.outputs.reduced_darks_path) == expected_darks
    assert Path(task.outputs.reduced_flats_path) == expected_flats
    assert expected_darks.is_file()
    assert expected_flats.is_file()


@pytest.mark.order(2)
@pytest.mark.parametrize("workflow", ["reducedarkflat.json"])
def test_reducedarkflat_workflow(workflow, tmp_dataset_path):
    wf = get_json_file(workflow)
    nx_file = tmp_dataset_path / "TestEwoksTomo_0010.nx"
    result = execute_graph(
        wf,
        inputs=[{"name": "nx_path", "value": str(nx_file)}],
    )
    expected_darks = tmp_dataset_path / "TestEwoksTomo_0010_darks.hdf5"
    expected_flats = tmp_dataset_path / "TestEwoksTomo_0010_flats.hdf5"
    assert Path(result["reduced_darks_path"]) == expected_darks
    assert Path(result["reduced_flats_path"]) == expected_flats
    assert expected_darks.exists()
    assert expected_flats.exists()
