import pytest

from bluer_options import string

from bluer_objects import file, objects
from bluer_objects.file.load import load_text
from bluer_objects.file.save import save_text
from bluer_objects.tests.test_objects import test_object


@pytest.mark.parametrize(
    [
        "filename",
    ],
    [
        ["test.json"],
        ["test.yaml"],
        ["test.yaml"],
    ],
)
def test_file_load_save_text(
    test_object,
    filename: str,
):
    filename_input = objects.path_of(
        object_name=test_object,
        filename=filename,
    )
    success, text_input = load_text(filename_input)
    assert success

    filename_test = file.add_suffix(
        filename_input,
        string.random(),
    )
    assert save_text(
        filename_test,
        text_input,
    )

    success, text_output = load_text(filename_test)
    assert success

    assert len(text_input) == len(text_output)
    for line_input, line_output in zip(text_input, text_output):
        assert line_input == line_output
