# Python API

This package exposes a single Python function for converting Markdown-ish text into a Signal-friendly payload shape usable with `signal-cli`.

## Install

- From PyPI (recommended):
  - `pip install markdownish`
- From source (local dev):
  - `pip install maturin` (or use a venv)
  - `maturin develop -F python`

## API

- `markdownish.render(text: str) -> dict`
  - Returns a dict with keys:
    - `text: str` — final message text after processing
    - `textStyles: list[str]` — style spans encoded as "<start>:<len>:<KIND>"
  - `KIND ∈ {BOLD, ITALIC, STRIKETHROUGH, MONOSPACE}`
  - Offsets are measured in UTF-16 code units over the final `text`.

Notes
- Headings are converted to textual cues `hN <raw text>` with a blank line after; no inline styles are emitted inside headings.
- Soft/hard line breaks become `\n`. Paragraphs are separated by a blank line.
- Code: inline backticks and code blocks emit `MONOSPACE` spans.

## Examples

### Basic

```py
import markdownish
print(markdownish.render("Hello world"))
# {'text': 'Hello world', 'textStyles': []}
```

### Inline styles

```py
import markdownish
r = markdownish.render("Hello **bold** and *it* and ~~gone~~ and `code`.")
print(r['text'])
# Hello bold and it and gone and code.
print(r['textStyles'])
# ['6:4:BOLD', '15:2:ITALIC', '22:4:STRIKETHROUGH', '31:4:MONOSPACE']
```

### Headings

```py
import markdownish
r = markdownish.render("# **Hello** _world_\n\nParagraph.")
print(r['text'])
# h1 Hello world
#
# Paragraph.
print(r['textStyles'])
# []  (no styles from inside the heading are emitted)
```

### Fenced code block

```py
import markdownish
r = markdownish.render("""```bash\nls -la | grep src\n```""")
print(repr(r['text']))
# 'ls -la | grep src\n\n'
print(r['textStyles'])
# ['0:18:MONOSPACE']
```

### Emoji and UTF‑16 offsets

```py
import markdownish
# Smiling face is 2 UTF-16 units; offsets account for that
r = markdownish.render("Hi 😊 **yo**")
print(r['text'])
# Hi 😊 yo
print(r['textStyles'])
# ['6:2:BOLD']  # start=6 counts UTF-16 units
```

The package doesn’t perform any I/O; it only renders text + styles.
