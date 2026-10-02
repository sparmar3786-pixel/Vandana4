from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "www" / "final-ui.js").read_text(encoding="utf-8")
MAIN = (ROOT / "backend" / "final_main.py").read_text(encoding="utf-8")

def test_extended_navigation_contract():
    for title in ["All Indian Indices", "NSE Indices", "BSE Indices", "NSE Sub Companies", "BSE Sub Companies", "Angel One API", "NSE MCP Live Connect"]:
        assert title in APP
    assert "screens.length<37" in APP

def test_connectivity_contract():
    assert "/api/mcp/connect" in APP
    assert "def mcp_connect" in MAIN

def test_paper_first_contract():
    assert "Live orders are disabled in this build" in (ROOT / "backend" / "main.py").read_text(encoding="utf-8")
