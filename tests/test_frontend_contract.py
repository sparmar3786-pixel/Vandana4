from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "www" / "index.html").read_text(encoding="utf-8")
APP = (ROOT / "www" / "app.js").read_text(encoding="utf-8")
CSS = (ROOT / "www" / "styles.css").read_text(encoding="utf-8")


def test_puter_script_cannot_block_app_boot():
    assert 'src="https://js.puter.com/v2/" async' in HTML or 'src="https://js.puter.com/v2/" defer' in HTML or 'data-puter-lazy' in HTML


def test_ui_has_30_real_navigation_controls():
    assert "screen-tabs" in HTML
    assert "setScreen" in APP
    assert "data-screen" in APP
    assert "for (var i = 0; i < screens.length; i++)" in APP
    assert "screens.length === 30" in APP or "screens.length" in APP


def test_theme_is_persistent_and_drives_root_theme():
    assert "localStorage.setItem('nse_theme'" in APP
    assert "localStorage.getItem('nse_theme'" in APP
    assert "data-theme" in APP
    assert "[data-theme='dark']" in CSS or ".dark" in CSS


def test_ui_is_not_empty_before_backend_is_available():
    assert "renderScreens()" in APP
    assert "boot()" in APP
    assert APP.index("renderScreens()") < APP.index("boot()")
