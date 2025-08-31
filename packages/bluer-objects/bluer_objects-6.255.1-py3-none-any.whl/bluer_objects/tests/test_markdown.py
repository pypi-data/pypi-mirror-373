from bluer_options.string import random

from bluer_objects.markdown import generate_table


def test_markdown_generate_table():
    assert generate_table(
        [random() for _ in range(50)],
        cols=4,
    )
