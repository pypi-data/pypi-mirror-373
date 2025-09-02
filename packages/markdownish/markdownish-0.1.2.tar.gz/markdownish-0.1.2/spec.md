# Markdown → Signal Renderer (Rust) — **Specification**

> **Purpose**: Define a minimal, predictable pipeline that converts Markdown-ish input to a *plain text message* and a list of **text style ranges**, suitable for use with Signal via `signal-cli`.

- **Primary consumer**: a Rust library used by an app that posts messages via `signal-cli`.
- **Detection engine**: `markdown-it` (Rust). No custom syntax; **no spoilers**. We **do** implement a custom *header* conversion to `hN <raw text>`.
- **Output**: (`Rendered`) structure.

---

## 1. Scope

### 1.1 In scope

- Inline styles: **bold**, *italic*, ~~strikethrough~~, `monospace` (inline and fenced blocks).
- Headings (ATX `#`, `##`, …, `######`, and Setext `===`/`---`) → **custom conversion**: `hN <raw text>`.
- Newlines/paragraph breaks.
- Final outputs: `text` and `textStyles` (array).

### 1.2 Out of scope (rendered as plain text)

- Links, images, blockquotes, lists, tables, HTML, footnotes, task checkboxes, autolinks, emojis-as-shortcodes.
- Custom syntax (spoilers, mentions, handles) — can be added later.

---

## 2. Terminology

- **Raw text**: plain textual content of a node with all Markdown markers removed (e.g., `**bold**` → `bold`).
- **UTF‑16 offset/length**: index/length counted in UTF‑16 code units over the **final message string**.
- **Detection**: identifying a style span from the AST (e.g., *Strong*, *Emphasis*, *Strikethrough*, *CodeInline*, *FencedCode*).

---

## 3. Input → Output Overview

### 3.1 Input

- UTF‑8 string, may contain CR, LF, or CRLF; normalize to `\n` during parsing/flattening.

### 3.2 Output data model (library)

```rust
pub enum Style { Bold, Italic, Strikethrough, Monospace }

pub struct TextStyle { pub start_utf16: u32, pub len_utf16: u32, pub style: Style }

pub struct Rendered { pub text: String, pub styles: Vec<TextStyle> }
```

### 3.3 Output for callers

- Library returns only the rendered text and style spans.
- Recommended encoding for styles when needed: `textStyles = ["<start>:<len>:<KIND>", …]` with `KIND ∈ {BOLD, ITALIC, STRIKETHROUGH, MONOSPACE}`.

---

## 4. Supported Markdown → Signal Rules

### 4.1 Inline styles

- **Bold**: `**text**` or `__text__` → span `{style: Bold}` over `text`.
- **Italic**: `*text*` or `_text_` → span `{style: Italic}` over `text`.
- **Strikethrough**: `~~text~~` → span `{style: Strikethrough}` over `text`.
- **Inline code**: `` `text` `` → span `{style: Monospace}` over `text`.

**Nesting/overlap**: Allowed. Each style produces its own range; overlapping ranges are legal.

**Escapes**: Backslash escapes handled by `markdown-it`; only the unescaped characters reach `collect_text()`.

**Inside code**: Emphasis markers inside code are treated as literal.

### 4.2 Code blocks

- **Fenced code** (` `lang … ` `) and **indented code blocks** are mapped to a contiguous `{style: Monospace}` span that covers the entire block content (excluding the trailing newline that separates the block from the next paragraph).
- Language tags are ignored for styling.
- The block’s literal text is preserved exactly (line order, spaces, tabs preserved; tabs are not expanded by the renderer).

### 4.3 Headings → custom textual conversion

- **ATX**: `#`, `##`, `###`, `####`, `#####`, `######` become `h1`, `h2`, …, `h6` respectively.
- **Setext**: `===` underlines → `h1`; `---` underlines → `h2`.
- **Conversion**: A heading becomes a single output line:
  - Prefix: `hN ` (N = 1..6), then the **raw text** of the heading (all inline markers removed), then a single newline `\n`.
  - Inline emphasis inside headings is **not styled** in Signal (because we are replacing the entire heading with `hN …`).
    - Rationale: Signal has no heading style; the textual cue `hN` replaces styled content. (Optional future feature: still style inner spans.)
- **Examples**:
  - `# **Hello** _world_` → `h1 Hello world\n`
  - `Title\n=====` → `h1 Title\n`

### 4.4 Paragraphs & line breaks

- Paragraphs are concatenated with a **single blank line** (i.e., two `\n`): one ending the paragraph, one between paragraphs.
- **Softbreak** → `\n`.
- **Hardbreak** → `\n`.

### 4.5 All other constructs

- Links/images/HTML/tables/lists/blockquote/footnotes/tasks: emit **only their plain textual content** (link destinations/titles dropped). No styles created.

---

## 5. Algorithm (normative)

### 5.1 Parse

- Create a `MarkdownIt` instance.
- Enable CommonMark core + `extra` features needed for strikethrough and fenced code.
- Parse the input to an AST (`Node`).

### 5.2 Flatten walk → build output

Maintain:

- `String out` (final message text), initially empty.
- `u32 pos` = current UTF‑16 length of `out`.
- `Vec<TextStyle> spans`.

Walk the AST depth-first. For each node:

1. **Heading (ATX/Setext)**

   - Compute `let label = format!("h{} ", level)`; append to `out`; `pos += utf16_len(label)`.
   - Append node’s `raw text` via `collect_text()`; update `pos` accordingly.
   - Append `\n`; `pos += 1`.
   - **Do not** create style spans for child emphasis (per §4.3). (A future feature gate may toggle this.)

2. **Inline style wrappers**

   - On `Strong` → record `start = pos`; recurse into children; on exit: if `pos > start` push `{start, len: pos-start, Bold}`.
   - On `Em` → same, `Italic`.
   - On `Strikethrough` → same.
   - On `CodeInline` → same with `Monospace`.

3. **Code blocks**

   - Record `start = pos`.
   - Append the block’s literal content as-is (preserving newlines); update `pos`.
   - If `pos > start`, push `{start, len: pos-start, Monospace}`.
   - Append a single trailing newline `\n` (not included in the monospace span).

4. **Text leaf nodes**

   - `s = node.collect_text()`; append to `out`; `pos += utf16_len(s)`.

5. **Soft/Hard breaks**

   - Append `\n`; `pos += 1`.

6. **Everything else**

   - Recurse into children; do not emit markers/attributes.

### 5.3 UTF‑16 accounting

- `utf16_len(s)` = `s.encode_utf16().count()`.
- Newlines (`\n`) count as `1` unit.
- Surrogate pairs (e.g., many emoji) count as `2` units; handled by `encode_utf16()`.

### 5.4 Normalization

- Convert CR or CRLF to `\n` once, on input or during leaf handling.
- No trailing whitespace trimming is performed; content is preserved.

---

## 6. Library API (proposed)

```rust
pub fn render(input: &str) -> Rendered;
```

- The library does not perform I/O; callers handle transport.

### 6.1 Python bindings (required)

- Provide Python bindings (e.g., via `pyo3`) exposing a single-call render function that accepts a UTF‑8 `str` and returns the final rendered text plus a `textStyles` array.
- Proposed Python API shape:
  - `render(text: str) -> dict` where the result is `{ "text": str, "textStyles": list[str] }` and each style item uses the `"<start>:<len>:<KIND>"` encoding. Always an array.
  - Alternatively, `render(text: str) -> (str, list[str])` is acceptable if tuple form is preferred.
- "Rendered" text here means the final message string after all processing in this spec, including header conversion to the textual `hN <raw>` form and newline normalization.
- The Python bindings perform no I/O; they only expose the render operation.

---

## 7. Examples (normative)

### 7.1 Inline styles

**Input**

```
Hello **bold** and *it* and ~~gone~~ and `code`.
```

**Output.text**

```
Hello bold and it and gone and code.
```

**Output.styles (UTF‑16)**

```
[ Bold      (start=6,  len=4),
  Italic    (start=15, len=2),
  Strike    (start=22, len=4),
  Monospace (start=31, len=4) ]
```

### 7.2 Headings

**Input**

```
# **Hello** _world_
Paragraph.
```

**Output.text**

```
h1 Hello world

Paragraph.
```

**Output.styles**

```
[]  // inline styles inside headings are not emitted
```

### 7.3 Fenced code block

**Input**

````
```bash
ls -la | grep src
```
````

**Output.text**

```
ls -la | grep src

```

**Output.styles**

```
[ Monospace (start=0, len=18) ]
```

---

## 8. Edge Cases & Rules

- **Unmatched markers**: if the parser yields literal text (not a style node), it remains literal; no styles emitted.
- **Overlapping/nesting**: produce independent spans in document order; overlaps are allowed.
- **Empty spans**: never emit zero-length ranges.
- **Whitespace around headings**: leading/trailing whitespace inside heading text is trimmed by `collect_text()` behavior; no additional trimming.
- **Very long messages**: no internal hard wrap; Signal’s size limits are left to the caller.

---

## 9. Testing

### 9.1 Must-haves (coverage)

- UTF‑16 correctness (emoji, multi-code-unit scripts).
- Overlaps: `***both***` should yield two overlapping spans over `both`.
- Headings: ATX levels 1–6 and Setext to `h1`/`h2`.
- Code blocks: with and without trailing newline.
- Newline normalization: CR, LF, CRLF all normalize to `\n`.
- Non-ASCII punctuation and RTL text.

### 9.2 Fixture format (for integration tests)

- Each test case is three files in `tests/fixtures/cases/`:
  - `<name>.in.md` — input Markdown-ish text (UTF‑8)
  - `<name>.out.txt` — expected final rendered text (post header conversion and newline normalization)
  - `<name>.styles.txt` — zero or more lines, each `"<start>:<len>:<KIND>"`. Empty file means no styles.
- The test harness runs `render()` on `.in.md` and asserts:
  - `Rendered.text == contents(<name>.out.txt)`
  - `encode_text_styles(Rendered.styles) == lines(<name>.styles.txt)` (always array form)

Note: To keep fixtures portable in a text-only VCS, inputs may include special tokens which the harness replaces before rendering:
- `[CRLF]` → `\r\n`, `[CR]` → `\r`, `[LF]` → `\n`.

### 9.3 Smoke tests (initial)

- `simple` — Input: `Hello world` → Output text: `Hello world`, Styles: none.
- `newlines` — Input with CR/LF/CRLF mix → Output text with only `\n`, Styles: none.
- Future: add `inline_styles`, `headings`, `fenced_code`, `overlap_italic_bold`, `emoji_utf16` as the renderer implementation lands.

---

## 10. Implementation Notes

- Prefer a single DFS walk over the AST; avoid re-encoding segments repeatedly. Keep a running UTF‑16 cursor.
- When emitting encoded styles, always use an array even for a single span.
- The header conversion policy (no inline styles inside headings) is deliberate for simplicity and predictability; consider a feature flag `style_headings` to enable styling later if needed.

---

## 11. Future Extensions

- Mentions/handles (ranges).
- Spoilers `||…||` via inline plugin.
- Lists → `•` and ordered numerals.
- Tables → plain text with column alignment.
- Link text + (URL) in parentheses.
