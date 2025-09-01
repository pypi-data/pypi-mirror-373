"""
QuickNote base classes.

- NotRenderedQuickNoteList: Type returned by the markdown parser.
- QuickNoteBase: Type from which every QuickNote is derived from.
- QuickNoteList: List of QuickNoteBase.
"""

from danoan.toml_dataclass import TomlDataClassIO, TomlTableDataClassIO

from dataclasses import dataclass, make_dataclass
from typing import Any, Dict, List, TextIO
import toml


@dataclass
class NotRenderedQuickNoteList:
    """
    Default class returned by the markdown parser.

    This class holds the raw data types parsed by the grammar.
    One needs to render as an instance of QuickNoteList using
    the render method.
    """

    quick_notes: List[Dict[str, Any]]

    def render(self, model_class) -> "QuickNoteList":
        r_quick_notes = [model_class(**qn) for qn in self.quick_notes]
        return QuickNoteList.create(r_quick_notes)


@dataclass
class QuickNoteBase(TomlDataClassIO):
    """
    Base class for every QuickNote.

    This class contains the ubiquitous quick-note data:
    title and text. No metadata is stored here.

    One should derive from this class to create custom
    quick-notes.
    """

    title: str
    text: str

    def __iter__(self):
        for name, value in self.__dict__.items():
            if name not in ["text", "title"]:
                yield (name, value)

    @classmethod
    def read_list(cls, stream_in: TextIO) -> "QuickNoteList":
        """
        Read a toml serialized QuickNoteList.
        """
        data_dict = toml.load(stream_in)
        if "list_of_quick_note" not in data_dict:
            raise RuntimeError(
                "Invalid quick-note list. The toml file does not contain a list_of_quick_note table."
            )

        list_of_quick_note = [
            cls(**e) for e in data_dict["list_of_quick_note"]
        ]
        return QuickNoteList.create(list_of_quick_note)


@dataclass
class QuickNoteList(TomlTableDataClassIO):
    """
    Type representing a list of quick-notes.
    """

    @staticmethod
    def create(
        quick_note_instance: List[QuickNoteBase],
    ) -> "QuickNoteList":
        """
        Create a QuickNoteList.
        """
        my_type = make_dataclass(
            "_QuickNoteList",
            [("list_of_quick_note", List[QuickNoteBase])],
            bases=(QuickNoteList,),
            eq=False,
        )
        return my_type(quick_note_instance)

    def __eq__(self, other):
        if isinstance(other, QuickNoteList):
            return self.list_of_quick_note == other.list_of_quick_note
