from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/"www/final.css").read_text(encoding="utf-8")
HTML=(ROOT/"www/index.html").read_text(encoding="utf-8")

def test_build322_visual_tokens_are_present():
    for token in ["--background:","--surface:","--primary:","--success:","--error:","--font-family-monospace","IBM Plex Mono"]:
        assert token in CSS

def test_build322_card_navigation_language_is_present():
    for cls in [".top{",".screen-tabs{",".detail{",".metric{",".tab{",".panel{"]:
        assert cls in CSS

def test_mobile_layout_remains_supported():
    assert "@media(max-width:620px)" in CSS
    assert 'viewport-fit=cover' in HTML
