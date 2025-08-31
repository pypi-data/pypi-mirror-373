import filecmp
import os
import shutil

import pytest

from hex_modifier_tool import hex_crc_insert, parse_and_run, ti_cc23xx_offsets


def create_temp_copy_for(tmp_path, filename):
    copy = str(tmp_path / os.path.basename(filename))
    shutil.copy(filename, copy)
    return copy


@pytest.fixture(scope="session")
def zephyr_image():
    return str(os.path.join(os.path.dirname(__file__), "data", "zephyr_missing_crc.hex"))


@pytest.fixture(scope="session")
def zephyr_ref_image():
    return str(os.path.join(os.path.dirname(__file__), "data", "zephyr_fixed.hex"))


@pytest.fixture(scope="function")
def zephyr_tmp_image(tmp_path, zephyr_image):
    return create_temp_copy_for(tmp_path, zephyr_image)


def test_ti_cc23xx_function(zephyr_tmp_image, zephyr_ref_image):
    hex_crc_insert(zephyr_tmp_image, ti_cc23xx_offsets())
    assert filecmp.cmp(zephyr_tmp_image, zephyr_ref_image, shallow=False)


def test_ti_cc23xx_main(zephyr_tmp_image, zephyr_ref_image):
    argv = ["test", zephyr_tmp_image, "-d", "ti_cc23xx"]
    assert parse_and_run(argv) == 0, "program exited with error"
    assert filecmp.cmp(zephyr_tmp_image, zephyr_ref_image, shallow=False)
