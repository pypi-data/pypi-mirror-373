from danoan.quick_notes.api.model import QuickNoteBase
from dataclasses import dataclass


@dataclass
class QuickNote(QuickNoteBase):
    id: int
    date: str
