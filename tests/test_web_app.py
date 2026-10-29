from pathlib import Path

import pytest

try:
    from streamlit.testing.v1 import AppTest
except ModuleNotFoundError:
    AppTest = None


@pytest.mark.skipif(AppTest is None, reason="Install the app extra to run this smoke test.")
def test_web_app_renders_sample_collection() -> None:
    assert AppTest is not None
    app_path = Path(__file__).resolve().parents[1] / "src" / "search_engine" / "web_app.py"
    app = AppTest.from_file(app_path, default_timeout=15).run()

    assert not app.exception
    assert app.title[0].value == "Search Engine"
    assert app.metric[0].label == "Documents indexed"
    assert app.metric[0].value != "0"
