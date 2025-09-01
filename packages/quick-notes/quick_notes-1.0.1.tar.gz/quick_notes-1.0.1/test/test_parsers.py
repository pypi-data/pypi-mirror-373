from danoan.quick_notes.api import to_toml, to_markdown
from danoan.quick_notes.api import model

import conftest as conf
import pytest


@pytest.mark.parametrize("n_entries", [1, 2, 5])
def test_valid_markdown(n_entries, tmp_path):
    list_of_mock_quick_note = [
        conf.MockQuickNoteFactory.next() for _ in range(n_entries)
    ]
    expected_quick_note_list = model.QuickNoteList.create(
        list_of_mock_quick_note
    )

    nr_quick_note_list = to_toml.parse(
        "\n".join([x.markdown_string() for x in list_of_mock_quick_note])
    )
    quick_note_list = nr_quick_note_list.render(conf.MockQuickNote)

    assert quick_note_list == expected_quick_note_list


@pytest.mark.parametrize("n_entries", [1, 2, 5])
def test_valid_quick_note_list(n_entries, tmp_path):
    list_of_mock_quick_note = [
        conf.MockQuickNoteFactory.next() for _ in range(n_entries)
    ]
    expected_quick_note_markdown = "\n".join(
        [x.markdown_string() for x in list_of_mock_quick_note]
    )

    print("Expected: ", expected_quick_note_markdown)

    expected_quick_note_markdown += (
        "\n"  # This accounts for the newline added by the template render
    )

    quick_note_list = model.QuickNoteList.create(list_of_mock_quick_note)
    quick_note_markdown = to_markdown.parse(quick_note_list)

    print("quick_note_markdown: ", quick_note_markdown)

    assert quick_note_markdown == expected_quick_note_markdown
