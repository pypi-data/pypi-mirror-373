# markdownish

Rust library to render Markdown-ish input into a Signal-friendly plain text message and text style ranges suitable for use with `signal-cli`.

- Spec: see `spec.md` for rules and future implementation details
- Status: baseline working — headings + inline styles (bold/italic/strikethrough/monospace)
- Parser: `markdown-it`
- Python: optional `pyo3` bindings behind `python` feature

## Quick Start (Rust)

- Call `render(&str) -> Rendered` to get:
  - `Rendered.text: String` — final message text (headings converted to `hN ...`).
  - `Rendered.styles: Vec<TextStyle>` — style spans with UTF‑16 offsets.
  - Encode spans for transport if needed with `encode_text_styles(&rendered.styles)` → `["<start>:<len>:<KIND>", ...]` (format usable with `signal-cli`).

## Example

```rust
use markdownish::{render, Style, TextStyle, encode_text_styles};

let rendered = render("# **Hello** _world_\n\nHello **bold** and *it*.");
// rendered.text => "h1 Hello world\n\nHello bold and it."
// rendered.styles => spans for bold/italic in the paragraph (none inside headings)

let encoded = encode_text_styles(&rendered.styles);
println!("{}", rendered.text);
println!("{:?}", encoded);
```

## What gets translated (high level)

- Headings: ATX/Setext → `hN <raw text>` plus a blank line after. Inline styles inside headings are not emitted.
- Bold/Italic: `**text**`/`__text__`, `*text*`/`_text_` → spans over the inner text.
- Paragraphs/Breaks: paragraphs separated by a blank line; soft/hard breaks → `\n`.
- Newlines: input CR/CRLF normalized to `\n`.
  

## Features

- `python`: enables optional Python bindings via `pyo3` (module scaffolding pending). Build with:
  - `cargo build --features python`
  - Or install the Python extension via `maturin`:
    - `pip install maturin` (once)
    - `maturin develop -F python` (installs `markdownish` into your current venv)

## Python usage

After `maturin develop -F python`, try:

- `python scripts/render.py "# **Hello** _world_ and **b** *i*"`
  - Outputs JSON with `text` and `textStyles` (array of `"<start>:<len>:<KIND>"`).
- `python scripts/repl.py`
  - Interactive: type lines, then `:go` to render current buffer.

Python API (high level):
- `import markdownish; markdownish.render(text: str) -> dict` with keys:
  - `text: str` — final message string
  - `textStyles: list[str]` — array of `"<start>:<len>:<KIND>"`

## Docs

- Generate Rust docs: `cargo doc --open`
 
