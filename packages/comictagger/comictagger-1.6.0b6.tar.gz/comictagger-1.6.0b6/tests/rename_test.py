from __future__ import annotations

import pathlib

import pytest

from comicapi.genericmetadata import md_test
from comictaggerlib import filerenamer
from testing.filenames import file_renames, folder_names


@pytest.mark.parametrize(
    "template, move, move_only, smart_cleanup, platform, expected, exception, warnings", file_renames
)
def test_rename(template, move, move_only, smart_cleanup, platform, expected, exception, warnings):
    fr = filerenamer.FileRenamer(None, platform=platform)
    fr.set_metadata(md_test, "cory doctorow #1.cbz")
    fr.move = move
    fr.move_only = move_only
    fr.set_template(template)
    fr.smart_cleanup = smart_cleanup
    with exception:
        assert str(pathlib.PureWindowsPath(fr.determine_name(".cbz"))) == str(pathlib.PureWindowsPath(expected))
    assert fr.warnings == warnings


@pytest.mark.parametrize("inp, result", folder_names)
def test_get_rename_dir(inp, result, cbz):
    assert result() == filerenamer.get_rename_dir(cbz, inp)
