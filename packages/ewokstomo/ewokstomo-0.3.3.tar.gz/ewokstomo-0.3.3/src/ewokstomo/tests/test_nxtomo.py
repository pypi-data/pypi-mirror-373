import pytest
from ewokstomo.tasks.nxtomomill import H5ToNx
from ewoks import execute_graph
from pathlib import Path
import importlib.resources as pkg_resources


def get_json_file(file_name):
    file_path = pkg_resources.files("ewokstomo.workflows").joinpath(file_name)
    return file_path


def get_data_file(file_name):
    file_path = pkg_resources.files(f"ewokstomo.tests.data.{file_name}").joinpath(
        f"{file_name}.h5"
    )
    return file_path


@pytest.mark.order(3)
@pytest.mark.parametrize("Task", [H5ToNx])
def test_nxtomomill(Task, tmpdir):
    output_dir = tmpdir / "output"
    output_dir.mkdir()
    h5_file_path = get_data_file("TestEwoksTomo_0010")
    expected_output = output_dir / "TestEwoksTomo_0010.nx"

    task = Task(
        inputs={
            "bliss_hdf5_path": h5_file_path,
            "nx_path": expected_output,
        }
    )
    task.run()

    assert str(Path(task.outputs.nx_path).resolve()) == str(expected_output)
    # assert Path(expected_output).is_file()


@pytest.mark.order(4)
@pytest.mark.parametrize("workflow", ["nxtomomill.json"])
def test_nxtomomill_workflow(workflow, tmpdir):
    output_dir = tmpdir / "output"
    output_dir.mkdir()
    h5_file_path = get_data_file("TestEwoksTomo_0010")
    expected_output = output_dir / "TestEwoksTomo_0010.nx"
    workflow_file_path = get_json_file(workflow)

    output = execute_graph(
        workflow_file_path,
        inputs=[
            {
                "name": "bliss_hdf5_path",
                "value": h5_file_path,
            },
            {"name": "nx_path", "value": expected_output},
        ],
    )

    assert str(Path(output["nx_path"]).resolve()) == str(expected_output)
    # assert Path(expected_output).is_file()
