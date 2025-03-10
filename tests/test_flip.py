from os.path import dirname, join
from unittest.mock import patch

import pytest

from agp import AgpRow, open_agp
from agp.agptools import main
from agp.bed import BadRangeError, BedRange, EmptyRangeError
from agp.flip import flip, reverse_rows


@pytest.fixture
def sample_agp_rows():
    return [
        AgpRow("scaffold_18\t1930402\t2636956\t9\tW\ttig123\t1\t706555\t-"),
        AgpRow("scaffold_18\t2636957\t2637456\t10\tN\t500\tscaffold\tyes\tna"),
        AgpRow("scaffold_18\t2637457\t3193955\t11\tW\ttig456\t1\t556499\t+"),
    ]


def test_reverse_rows(sample_agp_rows):
    reversed_rows = reverse_rows(sample_agp_rows)
    assert reversed_rows[0].component_id == "tig456"
    assert reversed_rows[0].orientation == "-"
    assert reversed_rows[0].object_beg == 1930402


def test_flip(tmpdir):
    with patch(
        "sys.argv",
        [
            "agptools",
            "flip",
            join(dirname(__file__), "data", "flips.txt"),
            join(dirname(__file__), "data", "test.agp"),
            "-o",
            join(tmpdir, "out.agp"),
        ],
    ):
        main()

    test_out = open_agp(join(tmpdir, "out.agp"))
    correct_out = open_agp(join(dirname(__file__), "data", "test_flip_out.agp"))

    for row1, row2 in zip(test_out, correct_out):
        assert row1 == row2


def test_flip_help(capsys):
    with patch("sys.argv", ["agptools", "flip", "--help"]):
        with pytest.raises(SystemExit):
            main()

    out, err = capsys.readouterr()
    assert "list of segments to flip, in bed format" in out


@pytest.mark.parametrize(
    "flip_bed_range, bed_error, error_string",
    [
        (
            BedRange("scaffold_18", 1, 100000),
            EmptyRangeError,
            "range scaffold_18:1-100000 does",
        ),
        (
            BedRange("scaffold_18", 1930402, 2637458),
            BadRangeError,
            "range scaffold_18:1930402-2637458 starts",
        ),
    ],
)
def test_bad_flip(sample_agp_rows, flip_bed_range, bed_error, error_string):
    with pytest.raises(bed_error) as exc:
        flip(sample_agp_rows, [flip_bed_range])
    assert error_string in str(exc.value)
