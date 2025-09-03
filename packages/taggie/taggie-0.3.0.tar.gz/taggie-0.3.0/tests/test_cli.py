# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0


import pytest

from taggie.main import get_parser


@pytest.mark.parametrize(
    "argv,expected,succeeds,error,code,out,err",
    (
        ([], dict(), True, None, None, None, None),
        # -h/--help
        (["-h"], dict(), False, SystemExit, 0, None, None),
        (["--help"], dict(), False, SystemExit, 0, None, None),
        # -V/--version
        (["-V"], dict(version=True), False, SystemExit, 0, "taggie 0.0.0", None),
        (["--version"], dict(version=True), False, SystemExit, 0, "taggie 0.0.0", None),
        # -g/--group
        (["-g", "language"], dict(groups=["language"]), True, None, None, None, None),
        (
            ["--group", "language"],
            dict(groups=["language"]),
            True,
            None,
            None,
            None,
            None,
        ),
        (["-g"], None, False, SystemExit, 2, None, None),
        (["--group"], None, False, SystemExit, 2, None, None),
        # -s/--sort
        # default choice is most
        ([], dict(sort_by="most"), True, None, None, None, None),
        ([], dict(sort_by="most"), True, None, None, None, None),
        # accepts choices
        (["-s", "most"], dict(sort_by="most"), True, None, None, None, None),
        (["--sort", "most"], dict(sort_by="most"), True, None, None, None, None),
        (["-s", "name"], dict(sort_by="name"), True, None, None, None, None),
        (["--sort", "name"], dict(sort_by="name"), True, None, None, None, None),
        # rejects invalid choice
        (["-s", "else"], None, False, SystemExit, 2, None, "invalid choice"),
        (["--sort", "else"], None, False, SystemExit, 2, None, "invalid choice"),
        # rejects no argument
        (["-s"], None, False, SystemExit, 2, None, "expected one argument"),
        (["--sort"], None, False, SystemExit, 2, None, "expected one argument"),
    ),
)
def test_parse_args(argv, expected, succeeds, error, code, out, err, capsys):
    parser = get_parser()
    if succeeds:
        args = parser.parse_args(argv)
        for key, value in expected.items():
            assert getattr(args, key) == value
    else:
        if error == SystemExit:
            with pytest.raises(error, check=lambda e: e.code == code):
                args = parser.parse_args(argv)
            captured = capsys.readouterr()
            if out:
                assert out in captured.out
            if err:
                assert err in captured.err
        else:
            with pytest.raises(error):
                args = parser.parse_args(argv)
