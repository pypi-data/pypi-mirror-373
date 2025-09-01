"""
Parse QuickNoteList to markdown string.
"""

from danoan.quick_notes.api import model

from pathlib import Path
from jinja2 import Environment, PackageLoader


def parse(quick_note_list: model.QuickNoteList) -> str:
    """
    Convert a QuickNoteList into a markdown string.

    Args:
        quick_note_list: An instance of QuickNoteList.

    Returns:
        Markdown string equivalent of the list of QuickNote.
    """
    env = Environment(
        loader=PackageLoader(
            "danoan.quick_notes.api", package_path="templates"
        )
    )

    template = env.get_template(
        Path("quick-note-table.tpl.md").expanduser().as_posix()
    )
    return template.render({"data": {"quick_note_list": quick_note_list}})
