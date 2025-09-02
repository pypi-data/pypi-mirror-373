import shutil
from pathlib import Path

import pytest
from ewokstomo.tasks.reconstruct_slice import ReconstructSlice
from ewoks import execute_graph
import importlib.resources as pkg_resources


def get_json_file(file_name: str) -> Path:
    from importlib.resources import path

    with path("ewokstomo.workflows", file_name) as p:
        return p


def get_data_file(file_name):
    file_path = pkg_resources.files(f"ewokstomo.tests.data.{file_name}").joinpath(
        f"{file_name}.h5"
    )
    return file_path


def get_data_dir(scan_name: str) -> Path:
    return Path(__file__).resolve().parent / "data" / scan_name


@pytest.fixture
def tmp_dataset_path(tmp_path) -> Path:
    src_dir = get_data_dir("TestEwoksTomo_0010")
    dst_dir = tmp_path / "TestEwoksTomo_0010"
    shutil.copytree(src_dir, dst_dir)
    # remove any existing darks/flats and gallery
    for pattern in ("*_darks.hdf5", "*_flats.hdf5", "gallery"):
        for f in dst_dir.glob(pattern):
            if f.is_dir():
                shutil.rmtree(f)
            else:
                f.unlink()
    return dst_dir


@pytest.mark.order(5)
@pytest.mark.parametrize("Task", [ReconstructSlice])
def test_slice_reconstruction_task(Task, tmp_dataset_path):
    nx = tmp_dataset_path / "TestEwoksTomo_0010.nx"

    nx_path = "dontexist.nx"
    nabu_conf = {
        "dataset": {"location": None},
        "reconstruction": {
            "start_z": "middle",
            "end_z": "middle",
        },
        "output": {"location": ""},
    }
    with pytest.raises(FileNotFoundError):
        task = Task(
            inputs={
                "config_dict": nabu_conf,
                "slice_index": "middle",
                "nx_path": nx_path,
            }
        )
        task.run()

    nx_path = str(nx)
    task = Task(
        inputs={"config_dict": nabu_conf, "slice_index": "middle", "nx_path": nx_path}
    )
    task.run()

    rec_path = Path(task.outputs.reconstructed_slice_path)
    assert rec_path.exists(), "Reconstructed slices directory does not exist"
    assert rec_path.is_file(), "Reconstructed slices path is not a file"


@pytest.mark.parametrize("workflow", ["reconstruction.json"])
def test_full_reconstruction_workflow(workflow, tmp_dataset_path):
    h5_file_path = get_data_file("TestEwoksTomo_0010")
    nx = str(tmp_dataset_path / "TestEwoksTomo_0010.nx")
    workflow_file_path = get_json_file(workflow)
    nabu_conf = {
        "dataset": {"location": None},
        "reconstruction": {
            "start_z": "middle",
            "end_z": "middle",
        },
        "output": {"location": ""},
    }

    reconstructed = execute_graph(
        workflow_file_path,
        inputs=[
            {
                "task_identifier": "ewokstomo.tasks.nxtomomill.H5ToNx",
                "name": "bliss_hdf5_path",
                "value": h5_file_path,
            },
            {
                "task_identifier": "ewokstomo.tasks.reconstruct_slice.ReconstructSlice",
                "name": "config_dict",
                "value": nabu_conf,
            },
            {
                "task_identifier": "ewokstomo.tasks.reconstruct_slice.ReconstructSlice",
                "name": "slice_index",
                "value": "middle",
            },
            {
                "task_identifier": "ewokstomo.tasks.nxtomomill.H5ToNx",
                "name": "nx_path",
                "value": nx,
            },
            {
                "task_identifier": "ewokstomo.tasks.reconstruct_slice.ReconstructSlice",
                "name": "nx_path",
                "value": nx,
            },
        ],
    )

    rec_path = Path(reconstructed["reconstructed_slice_path"])
    assert rec_path.exists(), "Reconstructed slices directory does not exist"
    assert rec_path.is_file(), "Reconstructed slices path is not a file"
    gallery_dir = rec_path.parents[2] / "gallery"
    assert gallery_dir.exists(), "Gallery directory does not exist"
    assert gallery_dir.is_dir(), "Gallery path is not a directory"

    images = sorted(gallery_dir.glob("*.png"))
    assert len(images) == 5, f"Expected 5 images, found {len(images)}"
