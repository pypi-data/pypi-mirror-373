# Getting started with quick-notes

Markdown dialect with support to metadata and toml serialization. [Read the
docs](https://danoan.github.io/quick-notes).

## Features

- Markdown with metadata.
- Markdown <--> toml.
- CLI to generate and validate .md and .toml quick-notes.

## What is a quick-note?

A quick-note is a markdown document labeled with a set of metadata and that can
be exported to toml format.

## Why quick-note 

- Programmatically update of markdown documents.
- General purpose toml format.


### Markdown quick-note 

A markdown quick-note is a markdown text wrapped within special
markdown comments starting with `<!--BEGIN-->` and ending with
`<!--END-->`. 

Here is the `ingredients.md` file.

```
<!--BEGIN id=0 date="2022-12-30T09:07:33.934408" -->
# 2022-12-30T09:07
I should remember to buy:

- Apples
- Milk
- Sugar

<!--END-->
```

A markdown quick-note text always starts with a title. The `<!--BEGIN-->`
statement accepts any list of key-value attributes that could be represented as
a string or as an integer.

Any quick-note in the markdown document can be easily update or removed thanks
to the markdown quick-note parser.

### Toml quick-note

A markdown quick-note can be converted to the general purpose toml format. Therefore,
the markdown quick-notes data can be used in a different markup/render mechanism of 
choice. 

The `ingredients.md` above would have the corresponding `ingredients.toml`:

```toml
[[list_of_quick_note]]
id = 0
date = "2022-12-30T09:07:33.934408"
title = "2022-12-30T09:07"
text = "I should remember to buy\n\n- Apples\n- Milk\n - Sugar\n\n"
```

## CLI application

The CLI application supports the following commands:

- generate-toml: converts a markdown quick-note to toml quick-note.
- generate-markdown: converts a toml quick-note to markdown quick-note.
- validate: check if a toml quick-note and a markdown quick-note are equivalent.
- generate-quick-note: generate a toml quick-note according to a data-layout.

To create toml quick-notes you need to specify a data-layout.

### Data Layout 

A data layout is a python dataclass with support to write and read toml files. The `quick-notes` package comes with a single data layout named: `QuickNote`.

```python   
@dataclass
class QuickNote(QuickNoteBase):
    id: int
    date: str
```

One can extend the `QuickNote` class or create its own. The attributes specified in the data-layout will be automatically
rendered in both markdown and toml representations of the quick-note.

```{caution} 
Instantiate derived classes of QuickNoteBase using keyword arguments only. Otherwise, the attributes
could be assigned values different from those expected.
```

## API module   

The CLI application relies on the quick-notes api. One can import the module `api` to create new applications using quick-notes.

