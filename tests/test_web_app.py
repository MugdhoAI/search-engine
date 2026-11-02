from pathlib import Path

import pytest

from search_engine.web_app import BACKGROUND_VIDEO_HTML

try:
    from streamlit.testing.v1 import AppTest
except ModuleNotFoundError:
    AppTest = None


def _load_app():
    assert AppTest is not None
    app_path = Path(__file__).resolve().parents[1] / "src" / "search_engine" / "web_app.py"
    return AppTest.from_file(app_path, default_timeout=15).run()


@pytest.mark.skipif(AppTest is None, reason="Install the app extra to run this smoke test.")
def test_web_app_renders_sample_collection() -> None:
    app = _load_app()

    assert not app.exception
    assert any("Find what matters in your documents." in item.value for item in app.markdown)
    assert any("deterministic TF IDF ranking." in item.value for item in app.markdown)
    assert any("Document collection" in item.value for item in app.markdown)
    assert app.metric[0].label == "Documents indexed"
    assert app.metric[0].value != "0"


def test_web_app_includes_a_muted_looping_video_background() -> None:
    app = _load_app()
    static_dir = Path(__file__).resolve().parents[1] / "src" / "search_engine" / "static"
    markup = "\n".join(item.value for item in app.html)

    assert not app.exception
    assert 'id="site-background"' in markup
    assert "autoplay" in markup
    assert "muted" in markup
    assert "loop" in markup
    assert "playsinline" in markup
    assert "/app/static/purple-desert.mp4" in markup
    assert "/app/static/purple-desert-poster.jpg" in markup
    assert 'id="site-background"' in BACKGROUND_VIDEO_HTML
    assert "autoplay" in BACKGROUND_VIDEO_HTML
    assert "muted" in BACKGROUND_VIDEO_HTML
    assert "loop" in BACKGROUND_VIDEO_HTML
    assert "playsinline" in BACKGROUND_VIDEO_HTML
    assert "/app/static/purple-desert.mp4" in BACKGROUND_VIDEO_HTML
    assert "/app/static/purple-desert-poster.jpg" in BACKGROUND_VIDEO_HTML
    assert (static_dir / "purple-desert.mp4").is_file()
    assert (static_dir / "purple-desert-poster.jpg").is_file()


@pytest.mark.skipif(AppTest is None, reason="Install the app extra to run this smoke test.")
def test_web_app_searches_sample_collection() -> None:
    app = _load_app()

    app.text_input[0].set_value("python")
    search_button = next(button for button in app.button if button.label == "Search")
    search_button.click()
    app.run()

    assert not app.exception
    assert any("Results for: python" in item.value for item in app.subheader)
    assert any("result(s), ordered by TF IDF score." in item.value for item in app.caption)


@pytest.mark.skipif(AppTest is None, reason="Install the app extra to run this smoke test.")
def test_web_app_shows_a_helpful_no_results_state() -> None:
    app = _load_app()

    app.text_input[0].set_value("no matching term")
    search_button = next(button for button in app.button if button.label == "Search")
    search_button.click()
    app.run()

    assert not app.exception
    assert any("No matching documents" in item.value for item in app.info)
