use markdownish::{encode_text_styles, render};

fn read(path: &str) -> String {
    std::fs::read_to_string(path).expect(path)
}

#[test]
fn fixtures_simple_and_newlines() {
    for name in [
        "simple",
        "newlines",
        "inline_styles",
        "headings",
        "inline_styles_more",
        "fenced_code",
    ] {
        let base = format!("tests/fixtures/cases/{}", name);
        let input = read(&format!("{}.in.md", base));
        let mut want_text = read(&format!("{}.out.txt", base));
        if want_text.ends_with('\n') {
            want_text.pop();
        }
        let want_styles_raw = read(&format!("{}.styles.txt", base));
        let want_styles: Vec<String> = want_styles_raw
            .lines()
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .collect();

        // Allow control tokens in fixtures for portability: [CR], [CRLF], [LF]
        let prepared_input = input
            .replace("[CRLF]", "\r\n")
            .replace("[CR]", "\r")
            .replace("[LF]", "\n");
        let rendered = render(&prepared_input);
        assert_eq!(rendered.text, want_text, "text mismatch for {}", name);

        let got: Vec<String> = encode_text_styles(&rendered.styles);
        assert_eq!(got, want_styles, "styles mismatch for {}", name);
    }
}
