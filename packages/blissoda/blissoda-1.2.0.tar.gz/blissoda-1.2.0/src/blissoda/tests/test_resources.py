import pytest

from .. import resources


def test_existing():
    with resources.resource_path("exafs", "exafs.ows") as path:
        assert path.is_file()

    assert str(path) == resources.resource_filename("exafs", "exafs.ows")


def test_non_existing():
    with pytest.raises(FileNotFoundError):
        with resources.resource_path("exafs", "notexisting.ows"):
            pass

    with pytest.raises(FileNotFoundError):
        resources.resource_filename("exafs", "notexisting.ows")


def test_not_a_file():
    with pytest.raises(FileNotFoundError):
        with resources.resource_path("exafs"):
            pass

    with pytest.raises(FileNotFoundError):
        resources.resource_filename("exafs")


def test_copy_existing(tmp_path):
    resources.copy_resource_glob("xrpd", "*.json", dest_dir=tmp_path)
    copied_files = {f.name for f in tmp_path.iterdir() if f.is_file()}
    expected = {"integrate_scan_without_saving.json", "integrate_scan_with_saving.json"}
    assert copied_files == expected


def test_copy_non_existing(tmp_path):
    resources.copy_resource_glob("xrpd", "*.notexisting", dest_dir=tmp_path)
    copied_files = {f.name for f in tmp_path.iterdir() if f.is_file()}
    expected = set()
    assert copied_files == expected
