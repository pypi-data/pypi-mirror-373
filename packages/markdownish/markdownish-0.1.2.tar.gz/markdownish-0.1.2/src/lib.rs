//! Markdown → Signal renderer (baseline scaffold)
//!
//! This crate exposes minimal API per spec.md:
//! - `render` to turn Markdown-ish input into `Rendered` (text + style ranges)
//!
//! Note: This initial baseline normalizes newlines and returns no styles.
//! The Markdown AST walk via `markdown-it` will be implemented next.

use serde::{Deserialize, Serialize};

// Parser
use markdown_it::MarkdownIt;
use markdown_it::Node;
use markdown_it::plugins::cmark;

/// Supported text styles for Signal.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum Style {
    Bold,
    Italic,
    Strikethrough,
    Monospace,
}

/// A style span over the final message text, measured in UTF-16 units.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct TextStyle {
    pub start_utf16: u32,
    pub len_utf16: u32,
    pub style: Style,
}

/// Render result: final plain text + style ranges.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Rendered {
    pub text: String,
    pub styles: Vec<TextStyle>,
}

/// Render Markdown-ish input to output (baseline version).
///
/// Current behavior:
/// - Normalizes CR/CRLF to `\n`.
/// - Emits the normalized text and style spans.
pub fn render(input: &str) -> Rendered {
    // Normalize newlines early; parser behavior depends on platform otherwise.
    let input = normalize_newlines(input);

    // Initialize MarkdownIt with CommonMark core and extras we will need.
    let mut md = MarkdownIt::new();
    cmark::add(&mut md);
    // Enable extra features per spec (strikethrough for ~~text~~)
    markdown_it::plugins::extra::strikethrough::add(&mut md);

    let ast = md.parse(&input);

    // Extract plain text and collect initial styles (bold/italic) and headings.
    let mut ctx = RenderCtx::default();
    flatten_plain_text(&ast, &mut ctx);

    Rendered { text: ctx.out, styles: ctx.styles }
}

/// Convenience: encode style spans to strings formatted "<start>:<len>:<KIND>".
pub fn encode_text_styles(spans: &[TextStyle]) -> Vec<String> {
    spans
        .iter()
        .map(|s| {
            let kind = match s.style {
                Style::Bold => "BOLD",
                Style::Italic => "ITALIC",
                Style::Strikethrough => "STRIKETHROUGH",
                Style::Monospace => "MONOSPACE",
            };
            format!("{}:{}:{}", s.start_utf16, s.len_utf16, kind)
        })
        .collect()
}

/// Normalize CR and CRLF to LF ("\n").
fn normalize_newlines(s: &str) -> String {
    // Replace CRLF first, then any remaining CR
    let s = s.replace("\r\n", "\n");
    s.replace('\r', "\n")
}

// Rendering context used during AST traversal
#[derive(Default)]
struct RenderCtx {
    out: String,
    pos_utf16: u32,
    styles: Vec<TextStyle>,
    in_heading: usize,
}

fn push_str(ctx: &mut RenderCtx, s: &str) {
    ctx.out.push_str(s);
    ctx.pos_utf16 += utf16_len(s) as u32;
}

fn push_char(ctx: &mut RenderCtx, c: char) {
    ctx.out.push(c);
    ctx.pos_utf16 += if (c as u32) <= 0xFFFF { 1 } else { 2 };
}

// Depth-first traversal to collect plain text per spec paragraph/break rules.
fn flatten_plain_text(root: &Node, ctx: &mut RenderCtx) {
    use markdown_it::plugins::cmark::block::paragraph::Paragraph;

    let mut seen_paragraph = false;
    for node in root.children.iter() {
        if node.is::<Paragraph>() {
            if seen_paragraph {
                push_char(ctx, '\n');
                push_char(ctx, '\n');
            }
            // emit paragraph children
            for child in node.children.iter() {
                emit_node_plain(child, ctx);
            }
            seen_paragraph = true;
        } else {
            emit_node_plain(node, ctx);
        }
    }
}

fn emit_node_plain(node: &Node, ctx: &mut RenderCtx) {
    use markdown_it::parser::inline::Text;
    use markdown_it::plugins::cmark::inline::newline::{Hardbreak, Softbreak};
    use markdown_it::plugins::cmark::block::paragraph::Paragraph;
    use markdown_it::plugins::cmark::block::heading::ATXHeading;
    use markdown_it::plugins::cmark::block::lheading::SetextHeader;
    use markdown_it::plugins::cmark::block::code::CodeBlock;
    use markdown_it::plugins::cmark::block::fence::CodeFence;
    use markdown_it::plugins::cmark::inline::backticks::CodeInline;
    use markdown_it::plugins::cmark::inline::emphasis::{Em, Strong};
    use markdown_it::plugins::extra::strikethrough::Strikethrough;

    if let Some(text) = node.cast::<Text>() {
        let s = text.content.as_str();
        push_str(ctx, s);
        return;
    }

    if node.is::<Softbreak>() || node.is::<Hardbreak>() {
        if ctx.in_heading > 0 {
            push_char(ctx, ' ');
        } else {
            push_char(ctx, '\n');
        }
        return;
    }

    if node.is::<Paragraph>() {
        // Paragraph handled at top-level in flatten_plain_text; if nested, just descend
        for child in node.children.iter() {
            emit_node_plain(child, ctx);
        }
        return;
    }

    if let Some(h) = node.cast::<ATXHeading>() {
        // Emit custom heading text: hN <raw text>\n\n
        let label = format!("h{} ", h.level);
        push_str(ctx, &label);
        ctx.in_heading += 1;
        for child in node.children.iter() { emit_node_plain(child, ctx); }
        ctx.in_heading -= 1;
        push_char(ctx, '\n');
        push_char(ctx, '\n');
        return;
    }
    if let Some(h) = node.cast::<SetextHeader>() {
        let label = format!("h{} ", h.level);
        push_str(ctx, &label);
        ctx.in_heading += 1;
        for child in node.children.iter() { emit_node_plain(child, ctx); }
        ctx.in_heading -= 1;
        push_char(ctx, '\n');
        push_char(ctx, '\n');
        return;
    }

    if let Some(f) = node.cast::<CodeFence>() {
        // Monospace span over the literal fenced block content
        let start = ctx.pos_utf16;
        push_str(ctx, f.content.as_str());
        let end = ctx.pos_utf16;
        if end > start {
            ctx.styles.push(TextStyle { start_utf16: start, len_utf16: end - start, style: Style::Monospace });
        }
        // Ensure a single trailing newline after the block (not part of the span)
        if !ctx.out.ends_with('\n') {
            push_char(ctx, '\n');
        }
        return;
    }
    if let Some(b) = node.cast::<CodeBlock>() {
        let start = ctx.pos_utf16;
        push_str(ctx, b.content.as_str());
        let end = ctx.pos_utf16;
        if end > start {
            ctx.styles.push(TextStyle { start_utf16: start, len_utf16: end - start, style: Style::Monospace });
        }
        if !ctx.out.ends_with('\n') {
            push_char(ctx, '\n');
        }
        return;
    }

    // Inline emphasis spans (bold/italic)
    if node.is::<Em>() {
        let start = ctx.pos_utf16;
        for child in node.children.iter() { emit_node_plain(child, ctx); }
        let end = ctx.pos_utf16;
        if end > start && ctx.in_heading == 0 {
            ctx.styles.push(TextStyle { start_utf16: start, len_utf16: end - start, style: Style::Italic });
        }
        return;
    }
    if node.is::<Strong>() {
        let start = ctx.pos_utf16;
        for child in node.children.iter() { emit_node_plain(child, ctx); }
        let end = ctx.pos_utf16;
        if end > start && ctx.in_heading == 0 {
            ctx.styles.push(TextStyle { start_utf16: start, len_utf16: end - start, style: Style::Bold });
        }
        return;
    }

    // Strikethrough and inline code (monospace)
    if node.is::<Strikethrough>() {
        let start = ctx.pos_utf16;
        for child in node.children.iter() { emit_node_plain(child, ctx); }
        let end = ctx.pos_utf16;
        if end > start && ctx.in_heading == 0 {
            ctx.styles.push(TextStyle { start_utf16: start, len_utf16: end - start, style: Style::Strikethrough });
        }
        return;
    }
    if node.is::<CodeInline>() {
        let start = ctx.pos_utf16;
        for child in node.children.iter() { emit_node_plain(child, ctx); }
        let end = ctx.pos_utf16;
        if end > start && ctx.in_heading == 0 {
            ctx.styles.push(TextStyle { start_utf16: start, len_utf16: end - start, style: Style::Monospace });
        }
        return;
    }

    // Default: descend into children
    for child in node.children.iter() {
        emit_node_plain(child, ctx);
    }
}

fn utf16_len(s: &str) -> usize { s.encode_utf16().count() }

// ---------------------------
// Python bindings (feature = "python")
// ---------------------------
#[cfg(feature = "python")]
mod py {
    use super::*;
    use pyo3::prelude::*;

    fn encode_style(s: &TextStyle) -> String {
        let kind = match s.style {
            Style::Bold => "BOLD",
            Style::Italic => "ITALIC",
            Style::Strikethrough => "STRIKETHROUGH",
            Style::Monospace => "MONOSPACE",
        };
        format!("{}:{}:{}", s.start_utf16, s.len_utf16, kind)
    }

    #[pyfunction(name = "render")]
    fn py_render(text: &str) -> PyResult<PyObject> {
        let rendered = crate::render(text);
        Python::with_gil(|py| {
            let styles: Vec<String> = rendered.styles.iter().map(encode_style).collect();
            let dict = pyo3::types::PyDict::new(py);
            dict.set_item("text", rendered.text)?;
            dict.set_item("textStyles", styles)?;
            Ok(dict.into())
        })
    }

    #[pymodule]
    fn markdownish(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
        m.add_function(wrap_pyfunction!(py_render, m)?)?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;

    #[test]
    fn render_baseline_normalizes_newlines() {
        let rendered = render("a\rb\r\nc\n");
        assert_eq!(rendered.text, "a\nb\nc");
        assert!(rendered.styles.is_empty());
    }

    #[test]
    fn encode_no_styles_returns_empty_array() {
        let r = Rendered { text: "hi".into(), styles: vec![] };
        let arr = encode_text_styles(&r.styles);
        assert!(arr.is_empty());
    }

    #[test]
    fn encode_single_style() {
        let r = Rendered {
            text: "bold".into(),
            styles: vec![TextStyle { start_utf16: 0, len_utf16: 4, style: Style::Bold }],
        };
        let arr = encode_text_styles(&r.styles);
        assert_eq!(arr, vec!["0:4:BOLD".to_string()]);
    }

    #[test]
    fn encode_multiple_styles() {
        let r = Rendered {
            text: "mix".into(),
            styles: vec![
                TextStyle { start_utf16: 0, len_utf16: 1, style: Style::Italic },
                TextStyle { start_utf16: 1, len_utf16: 2, style: Style::Bold },
            ],
        };
        let arr = encode_text_styles(&r.styles);
        assert_eq!(arr, vec!["0:1:ITALIC".to_string(), "1:2:BOLD".to_string()]);
    }
}
