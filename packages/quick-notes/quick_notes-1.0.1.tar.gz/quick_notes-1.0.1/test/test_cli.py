from danoan.quick_notes.api import to_toml, to_markdown
from danoan.quick_notes.cli import cli

import conftest as conf
from io import StringIO
import pytest


@pytest.mark.parametrize("num_entries", [1, 2, 5])
def test_generate_markdown(num_entries, tmp_path):
    # Initialization
    toml_filepath = tmp_path.joinpath("quick-notes.toml")

    quick_note_list = conf.generate_mock_quick_note_list(num_entries)
    with open(toml_filepath, "w") as f:
        quick_note_list.write(f)

    # Execution
    markdown_string = cli.generate_markdown_from_filepath(toml_filepath)

    # Ground Truth
    nr_quick_note_list_from_generated_markdown = to_toml.parse(markdown_string)
    quick_note_list_from_generated_markdown = (
        nr_quick_note_list_from_generated_markdown.render(conf.MockQuickNote)
    )

    expected_toml_stream = StringIO()
    quick_note_list.write(expected_toml_stream)

    produced_toml_stream = StringIO()
    quick_note_list_from_generated_markdown.write(produced_toml_stream)

    # Comparison
    assert produced_toml_stream.read() == expected_toml_stream.read()


@pytest.mark.parametrize("num_entries", [1, 2, 5])
def test_generate_toml(num_entries, tmp_path):
    # Initialization
    markdown_filepath = tmp_path.joinpath("quick-notes.md")

    markdown_string = conf.generate_mock_quick_note_markdown(num_entries)
    with open(markdown_filepath, "w") as f:
        f.write(markdown_string)

    # Execution
    quick_note_list = cli.generate_toml_from_filepath(markdown_filepath)

    # Ground Truth
    markdown_from_generated_quick_note_list = to_markdown.parse(
        quick_note_list
    )

    # Comparison
    assert to_toml.parse(markdown_string) == to_toml.parse(
        markdown_from_generated_quick_note_list
    )


@pytest.mark.parametrize("num_entries", [1, 2, 5])
def test_validate_files(num_entries, tmp_path):
    # Initialization
    markdown_filepath = tmp_path.joinpath("quick-notes.md")
    toml_filepath = tmp_path.joinpath("quick-notes.toml")

    markdown_string = conf.generate_mock_quick_note_markdown(num_entries)
    with open(markdown_filepath, "w") as f:
        f.write(markdown_string)

    with open(toml_filepath, "w") as f:
        to_toml.parse(markdown_string).render(conf.MockQuickNote).write(f)

    # Comparison
    assert cli.validate_files(toml_filepath, markdown_filepath)

    # Slight modification and Comparison
    markdown_string = conf.generate_mock_quick_note_markdown(num_entries + 1)
    with open(markdown_filepath, "w") as f:
        f.write(markdown_string)

    assert not cli.validate_files(toml_filepath, markdown_filepath)


def test_generate_parser():
    assert cli.create_parser()
