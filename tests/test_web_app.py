import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest


def test_web_app_renders_sample_collection() -> None:
    app = AppTest.from_file("src/search_engine/web_app.py", default_timeout=15).run()

    assert not app.exception
    assert app.title[0].value == "Search Engine"
    assert app.metric[0].label == "Documents indexed"
    assert app.metric[0].value != "0"
