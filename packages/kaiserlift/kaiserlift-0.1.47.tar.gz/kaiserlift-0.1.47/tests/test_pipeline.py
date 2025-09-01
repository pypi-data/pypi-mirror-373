from pathlib import Path

import kaiserlift


pipeline = getattr(kaiserlift, "pipeline")


def test_pipeline_generates_html() -> None:
    csv_path = Path("tests/example_use/FitNotes_Export_2025_05_21_08_39_11.csv")
    with csv_path.open("rb") as fh:
        html = pipeline([fh])
    assert "<table" in html
    assert html.count('id="result"') == 1
    assert 'id="uploadButton"' in html
    assert 'id="uploadProgress"' in html


def test_pipeline_fragment_without_assets() -> None:
    csv_path = Path("tests/example_use/FitNotes_Export_2025_05_21_08_39_11.csv")
    with csv_path.open("rb") as fh:
        html = pipeline([fh], embed_assets=False)
    assert "<table" in html
    assert "<script" not in html
    assert "<link" not in html
    assert 'id="uploadButton"' not in html
    assert 'id="csvFile"' not in html
    assert 'id="result"' not in html
    assert 'id="uploadProgress"' not in html
