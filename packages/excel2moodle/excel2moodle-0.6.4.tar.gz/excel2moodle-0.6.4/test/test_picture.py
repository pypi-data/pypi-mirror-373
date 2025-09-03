from pathlib import Path

import pytest

from excel2moodle.core.question import Picture

imgFolder = Path("./test/Abbildungen")

qID = "0103"
katName = "MC1"


@pytest.mark.parametrize(
    ("imgKey", "path", "width", "height"),
    [
        ("1:height:100", "0101.png", 0, 100),
        ("true", "0103.svg", 300, 0),
        ("yes", "0103.svg", 300, 0),
        ("1_a:width:100", "0101_a.png", 100, 0),
        ("0101:height:255", "0101.png", 0, 255),
        ("03:width:545", "0103.svg", 545, 0),
        ("101_a:height:80", "0101_a.png", 0, 80),
        pytest.param(
            "101_a:height:80:width:100", "0101_a.png", 100, 80, marks=pytest.mark.xfail
        ),
    ],
)
def test_PictureFindImgFile(imgKey, path, width, height) -> None:
    imgF = (imgFolder / katName).resolve()
    picture = Picture(imgKey, imgF, qID, width=300)
    print(picture.path)
    p = str(picture.path.stem + picture.path.suffix)
    size = picture.size
    assert p == path
    assert size.get("height", "0") == str(height)
    assert size.get("width", "0") == str(width)


@pytest.mark.parametrize(
    ("imgKey", "expected"),
    [
        ("2_b", "0102_b"),
        ("01_a", "0101_a"),
        ("0101", "0101"),
        ("05-c", "0105-c"),
        ("201", "0201"),
        ("101_a", "0101_a"),
        ("3802_c", "3802_c"),
        ("0902_c", "0902_c"),
        pytest.param("13802_c", "3802_c", marks=pytest.mark.xfail),
        pytest.param("false", None, marks=pytest.mark.xfail),
    ],
)
def test_Picture_EvaluateCorrectPicID(imgKey, expected) -> None:
    imgF = (imgFolder / katName).resolve(strict=True)
    picture = Picture(imgKey, imgF, qID, width=300)
    assert picture.picID == expected
