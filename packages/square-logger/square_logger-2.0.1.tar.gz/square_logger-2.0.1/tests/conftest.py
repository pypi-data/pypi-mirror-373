import os
import shutil

import pytest


@pytest.fixture
def log_folder():
    log_folder = "logs"

    yield log_folder

    if os.path.exists(log_folder):
        shutil.rmtree(log_folder, ignore_errors=True)
