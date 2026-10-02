from pathlib import Path

HTML=(Path(__file__).resolve().parents[1]/"www/index.html").read_text(encoding="utf-8")

def test_apk_has_visible_static_terminal_before_javascript():
    for marker in ["NSE-AI-TERMINAL","All Indian Indices","Angel One API","NSE MCP Live Connect","CALL BUY","PUT BUY","WAIT","NO QUALIFYING TRADE"]:
        assert marker in HTML

def test_apk_shell_has_light_dark_and_mobile_viewport():
    assert "final.css" in HTML
    assert 'viewport-fit=cover' in HTML
    assert 'id="theme"' in HTML
    assert 'dataset.theme' in HTML
