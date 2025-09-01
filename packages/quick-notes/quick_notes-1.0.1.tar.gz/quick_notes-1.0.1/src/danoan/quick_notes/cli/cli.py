from danoan.quick_notes.api import to_markdown, to_toml
from danoan.quick_notes.api.model import QuickNoteList

from danoan.quick_notes.cli.model import QuickNote

import argparse
from datetime import datetime
import io
import sys
from typing import TextIO, Optional, Union


def generate_markdown_from_stream(toml_stream: TextIO) -> str:
    """
    Generate markdown quick-note from toml data.

    Args:
        toml_stream: String stream serving toml data.

    Returns:
        String representing a markdown quick-note.
    """
    return to_markdown.parse(QuickNote.read_list(toml_stream))


def generate_toml_from_stream(markdown_stream: TextIO) -> QuickNoteList:
    """
    Generate toml quick-note from markdown data.

    Args:
        markdown_stream: String stream serving markdown data.

    Returns:
        String representing a toml quick-note.
    """
    not_rendered_quick_note = to_toml.parse(markdown_stream.read())
    return not_rendered_quick_note.render(QuickNote)


def generate_markdown_from_filepath(toml_filepath: str) -> str:
    """
    Generate markdown quick-note from a toml quick-note file.

    Args:
        toml_filepath: Path to the toml quick-note file.

    Returns:
        String representing a markdown quick-note.
    """
    with open(toml_filepath, "r") as stream:
        return generate_markdown_from_stream(stream)


def generate_toml_from_filepath(markdown_filepath: str) -> QuickNoteList:
    """
    Generate toml quick-note from a markdown quick-note file.

    Args:
        markdown_filepath: Path to the markdown quick-note file.

    Returns:
        String representing a toml quick-note.
    """
    with open(markdown_filepath, "r") as stream:
        return generate_toml_from_stream(stream)


def validate_files(toml_filepath: str, markdown_filepath: str) -> bool:
    """
    Check consistency between a toml quick-note and a markdown quick-note.

    Args:
        toml_filepath:  Path to the toml quick-note file.
        markdown_filepath: Path to the markdown quick-note file.

    Returns:
        True if the files are consistent; and False otherwise.
    """
    with open(markdown_filepath, "r") as f_md, open(toml_filepath) as f_toml:
        markdown_string = f_md.read()

        to_toml.parse(markdown_string)

        if QuickNote.read_list(f_toml) == to_toml.parse(
            markdown_string
        ).render(QuickNote):
            return True

        return False


def generate_quick_note(id: int, date: str, title: str, text: str) -> str:
    """
    Generate a toml quick-note.

    Args:
        id: Unique identifier.
        date: Creation date.
        title: Title of the quick-note.
        text: Content of the quick-note.

    Returns:
        Toml quick-note filled up with the given parameters.
    """
    s = io.StringIO()
    QuickNoteList.create(
        [QuickNote(id=id, date=date, title=title, text=text)]
    ).write(s)
    return s.getvalue()


def _extract_help_summary(docstring: Optional[str]) -> str:
    if not docstring:
        return ""

    if docstring.split("."):
        return docstring.split(".")[0]
    else:
        return ""


def _extract_help(docstring: Optional[str]) -> str:
    if not docstring:
        return ""
    else:
        return docstring

    param_first_index = docstring.find(":param")
    returns_first_index = docstring.find(":returns")

    if param_first_index != -1:
        return docstring[:param_first_index]
    elif returns_first_index != -1:
        return docstring[:returns_first_index]
    else:
        return docstring


def _generate_markdown(toml_filepath: Union[str, TextIO], **kwargs):
    """
    Generate markdown quick-notes from toml quick-notes.

    Args:
        toml_filepath: Path to the toml file.
    """
    if isinstance(toml_filepath, type(sys.stdin)):
        sys.stdout.write(generate_markdown_from_stream(toml_filepath))  # type: ignore
    elif isinstance(toml_filepath, str):
        sys.stdout.write(generate_markdown_from_filepath(toml_filepath))


def _generate_toml(markdown_filepath: str, **kwargs):
    """
    Generate toml quick-notes from markdown quick-notes.

    Args:
        markdown_filepath: Path to the markdown file
    """
    if isinstance(markdown_filepath, type(sys.stdin)):
        generate_toml_from_stream(markdown_filepath).write(sys.stdout)  # type: ignore
    elif isinstance(markdown_filepath, str):
        generate_toml_from_filepath(markdown_filepath).write(sys.stdout)


def _validate_files(
    toml_filepath: str,
    markdown_filepath: str,
    overwrite_markdown: bool,
    overwrite_toml: bool,
    **kwargs,
):
    """
    Check if the toml and markdown versions are equivalent.

    Args:
        toml_filepath: Path to the toml file.
        markdown_filepath: Path to the markdown file.
        overwrite_markdown (optional): If True, rewrites the markdown file based on the toml file.
        overwrite_toml (optional): If True, rewrites the toml file based on the markdown file.

    It will print "Valid" if the quick-notes are consistent; and it will print "Invalid" otherwise.
    """
    if overwrite_markdown and overwrite_toml:
        overwrite_toml = False

    if validate_files(toml_filepath, markdown_filepath):
        print("Valid")
    else:
        if overwrite_toml:
            with open(markdown_filepath, "r") as fm:
                to_toml.parse(fm.read()).render(QuickNote).write(toml_filepath)
        elif overwrite_markdown:
            with open(markdown_filepath, "w") as fm, open(
                toml_filepath
            ) as f_toml:
                fm.write(to_markdown.parse(QuickNote.read_list(f_toml)))
        else:
            print("Invalid")


def _generate_quick_note(
    text: str,
    id: int = 0,
    date: Optional[str] = None,
    title: Optional[str] = None,
    **kwargs,
):
    """
    Generate quick-note in toml format.

    Args:
        text: Quick-note content.
        id (optional): Quick-note identifier. Default = 0.
        date (optional): Creation date. Default is the current date.
        title (optional): Quick-note title. Default is the current date.
    """
    if not date:
        date = datetime.now().isoformat()
    if not title:
        title = datetime.fromisoformat(date).isoformat(timespec="minutes")

    s = generate_quick_note(id, date, title, text)
    sys.stdout.write(s)


def create_parser():
    parser = argparse.ArgumentParser(
        "quick-notes",
        description="Create quick-notes in markdown and toml format.",
    )

    subparsers = parser.add_subparsers()

    toml_parser = subparsers.add_parser(
        "generate-toml",
        help=_extract_help_summary(_generate_toml.__doc__),
        description=_extract_help(_generate_toml.__doc__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    toml_parser.add_argument("markdown_filepath", nargs="?", default=sys.stdin)
    toml_parser.set_defaults(func=_generate_toml)

    markdown_parser = subparsers.add_parser(
        "generate-markdown",
        help=_extract_help_summary(_generate_markdown.__doc__),
        description=_extract_help(_generate_markdown.__doc__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    markdown_parser.add_argument("toml_filepath", nargs="?", default=sys.stdin)
    markdown_parser.set_defaults(func=_generate_markdown)

    validate_parser = subparsers.add_parser(
        "validate",
        help=_extract_help_summary(_validate_files.__doc__),
        description=_extract_help(_validate_files.__doc__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    validate_parser.add_argument("--toml-filepath", "-t", required=True)
    validate_parser.add_argument("--markdown-filepath", "-m", required=True)
    validate_parser.add_argument(
        "--overwrite-markdown", action="store_true", default=False
    )
    validate_parser.add_argument(
        "--overwrite-toml", action="store_true", default=False
    )
    validate_parser.set_defaults(func=_validate_files)

    generate_quick_note_parser = subparsers.add_parser(
        "generate-quick-note",
        help=_extract_help_summary(_generate_quick_note.__doc__),
        description=_extract_help(_generate_quick_note.__doc__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    generate_quick_note_parser.add_argument("text")
    generate_quick_note_parser.add_argument("--id", type=int, default=0)
    generate_quick_note_parser.add_argument("--date")
    generate_quick_note_parser.add_argument("--title")
    generate_quick_note_parser.set_defaults(func=_generate_quick_note)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    if "func" in args:
        args.func(**vars(args))
    else:
        parser.print_help(sys.stdout)


if __name__ == "__main__":
    main()
