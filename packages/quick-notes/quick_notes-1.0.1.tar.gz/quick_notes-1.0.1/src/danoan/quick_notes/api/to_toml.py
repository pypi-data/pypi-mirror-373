"""
Parse markdown string to NotRenderedQuickNoteList.
"""

from danoan.quick_notes.api import model

from lark import Lark, Transformer
from typing import Any, Dict, List


class _MarkdownQuickNoteToToml(Transformer):
    def identifier(self, s) -> str:
        (s,) = s
        return str(s)

    def integer(self, i) -> int:
        (i,) = i
        return int(i)

    def value(self, v) -> str:
        (v,) = v
        return v

    def escaped_string(self, s) -> str:
        (s,) = s
        return s[1:-1]

    string = identifier

    def title(self, t) -> Dict[str, str]:
        return {"title": t[0]}

    def text(self, t) -> Dict[str, str]:
        return {"text": "\n".join(t)}

    def attribute(self, items) -> Dict[str, str]:
        k, v = items
        return {k: v}

    def entry(self, items) -> Dict[str, Any]:
        d_params = {}
        for d in items:
            d_params.update(d)

        return d_params

    def document(self, items) -> List[Dict[str, Any]]:
        return list(items)


def parse(markdown_str: str) -> model.NotRenderedQuickNoteList:
    """
    Convert a markdown string containing one or more quick note into a non
    rendered QuickNoteList.

    Args:
        markdown_str: A markdown string containing one or more markdown quick-note.

    Returns:
        A list of QuickNote.
    """
    quick_notes_grammar = r"""
        document: entry*
    
        entry: _begin title text _end
        title: "#" string
        _begin: "<!--BEGIN" (attribute)* "-->" 
        _end: "<!--END-->"
        attribute: identifier "=" value
        value: escaped_string
              |integer
        text: string*
        identifier: /[A-Za-z_]+/ 

        integer: /\d+/
        string: /.+/
        escaped_string: ESCAPED_STRING 

        %import common.ESCAPED_STRING
        %import common.WS
        %ignore WS
    """
    quick_notes_parser = Lark(
        quick_notes_grammar,
        start="document",
        parser="lalr",
        transformer=_MarkdownQuickNoteToToml(),
    )

    parsed_document = quick_notes_parser.parse(markdown_str)
    if not isinstance(parsed_document, list):
        raise RuntimeError(f"Unexpected parsed data type: {parsed_document}")

    parsed_element = model.NotRenderedQuickNoteList(
        quick_notes_parser.parse(markdown_str)
    )
    if not isinstance(parsed_element, model.NotRenderedQuickNoteList):
        raise RuntimeError(f"Unexpected parsed data type: {parsed_element}")

    return parsed_element
