from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
UI=(ROOT/"www"/"final-ui.js").read_text(encoding="utf-8")
HTML=(ROOT/"www"/"index.html").read_text(encoding="utf-8")
RENDER=(ROOT/"render.yaml").read_text(encoding="utf-8")
API=(ROOT/"backend"/"final_main.py").read_text(encoding="utf-8")

def test_final_ui_has_38_screens_and_requested_tabs():
    for x in ["All Indian Indices","NSE Indices","BSE Indices","NSE Sub Companies","BSE Sub Companies","Angel One API","NSE MCP Live Connect","System Health"]:
        assert x in UI
    assert "screens.length<37" in UI

def test_angel_credentials_are_not_persisted():
    for x in ["angel-client-id","angel-access-token","angel-mpin","angel-totp"]:
        assert x in UI
    assert "localStorage.setItem('angel-" not in UI

def test_backend_contracts():
    assert "def angel_connect" in API
    assert "def mcp_connect" in API
    assert "def equities" in API
    assert "def readyz" in API

def test_render_is_configured_for_final_backend():
    assert "backend.final_main:app" in RENDER
    assert "healthCheckPath: /readyz" in RENDER
    assert "ENABLE_LIVE_ORDERS" in RENDER

def test_apk_shell_loads_final_ui():
    assert "final.css" in HTML
    assert "final-ui.js" in HTML
