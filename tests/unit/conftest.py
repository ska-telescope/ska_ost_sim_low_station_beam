import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def test_image_name():
    file_name = Path("test_image.png")
    yield file_name
    os.remove(file_name)
