from pathlib import Path

import pytest

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
    assert app.title[0].value == "Search Engine"
    assert app.metric[0].label == "Documents indexed"
    assert app.metric[0].value != "0"


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
