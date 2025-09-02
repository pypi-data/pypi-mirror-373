"""Test generating SVG data strings.

:author: Shay Hill
:created: 2024-12-13
"""

# pyright: reportPrivateUsage = false

from typing import TypeVar

import pytest
from paragraphs import par

from svg_path_data.string_ops import svgd_join, svgd_split
from svg_path_data.svg_data import (
    PathCommand,
    PathCommands,
    format_svgd_absolute,
    format_svgd_relative,
    format_svgd_shortest,
    get_cpts_from_svgd,
    get_svgd_from_cpts,
)

_T = TypeVar("_T")


def test_always_start_with_M() -> None:
    """Always start shortest with an `M` command, even where `m` is shorter."""
    svgd = "m100000 100000l-1 1"
    assert format_svgd_absolute(svgd) == "M1e5 1e5 99999 100001"
    assert format_svgd_relative(svgd) == "m1e5 1e5-1 1"
    assert format_svgd_shortest(svgd) == "M1e5 1e5l-1 1"


def test_multiple_ls_after_mid_m() -> None:
    """Merge multiple L commands after a mid M command."""
    svgd = "M1052 242H536L465 0H2L553 1466h494L1598 0H1124Zm-95 317-162 527L634 559Z"
    cpts = get_cpts_from_svgd(svgd)
    result = format_svgd_shortest(get_svgd_from_cpts(cpts))
    assert_svgd_equal(result, svgd)


def assert_svgd_equal(result: str, expect: str):
    """Assert result == expect and test helper functions.

    This is just a method for running bonus circular tests on other test data.
    """
    assert result == expect
    assert svgd_join(*svgd_split(expect)) == expect
    assert get_svgd_from_cpts(get_cpts_from_svgd(expect)) == format_svgd_shortest(
        expect
    )

    for fmt in (
        format_svgd_absolute,
        format_svgd_relative,
        format_svgd_shortest,
    ):
        pre_loop = fmt(expect)
        cpts = get_cpts_from_svgd(pre_loop)
        assert fmt(get_svgd_from_cpts(cpts)) == pre_loop

    shortest = format_svgd_shortest(expect)
    relative = format_svgd_relative(expect)
    absolute = format_svgd_absolute(expect)
    assert shortest == format_svgd_shortest(relative)
    assert shortest == format_svgd_shortest(absolute)
    assert len(shortest) <= len(relative)
    assert len(shortest) <= len(absolute)


class TestCptsWithMidClose:
    def test_mid_close(self):
        """Insert multiple m commands if a path is closed in the middle."""
        cpts = [
            [(0, 0), (1, 0), (2, 0)],
            [(2, 0), (3, 0), (4, 0)],
            [(4, 0), (5, 0), (0, 0)],  # Close the path
            [(0, 5), (1, 5), (2, 5)],  # Another segment starting with M
            [(2, 5), (3, 5), (4, 5)],  # another disjoint segment, but returned to M
            [(3, 9), (4, 9), (5, 9)],  # Another segment starting with M
            [(5, 9), (6, 9), (3, 9)],  # Close the path
        ]
        expect = "m0 0h4q1 0-4 0zm0 5h4m-1 4h2q1 0-2 0z"
        result = format_svgd_relative(get_svgd_from_cpts(cpts))
        assert_svgd_equal(result, expect)


def test_no_leading_zero():
    """Correctly split numbers without leading zeros."""
    expect = ["M", "0", ".0", "L", "-.2", "-.5", ".3", ".4"]
    assert svgd_split("M0 .0L-.2-.5 .3 .4") == expect


def test_exponential_notation():
    """Correctly split numbers in exponential notation."""
    assert svgd_split("M1e-2 2E3 3.4e+5-1") == ["M", "1e-2", "2E3", "3.4e+5", "-1"]


class TestNonAdjacentCurveShorthand:
    """Test that non-adjacent curves get shorthand for equal first two points."""

    def test_t(self):
        """Test that adjacent curve shorthand commands are joined."""
        svgd = "M1 2Q1 2 4 4z"
        cmds = PathCommands.from_svgd(svgd)
        assert_svgd_equal(cmds.abs_svgd, "M1 2 4 4Z")

    def test_s(self):
        """Test that adjacent curve shorthand commands are joined."""
        svgd = "M1 2C1 2 3 4 4 3z"
        cmds = PathCommands.from_svgd(svgd)
        assert_svgd_equal(cmds.abs_svgd, "M1 2S3 4 4 3Z")


class TestCloseCurve:
    """Explicitly close with z when a curve closes a path."""

    def test_end_with_curve(self):
        cpts = (
            ((0.5, 0.5), (1.0, 0.0), (2.0, 0.0), (2.5, 0.5)),
            ((2.5, 0.5), (3.0, 1.0), (3.0, 2.0), (2.5, 2.5)),
            ((2.5, 2.5), (2.0, 3.0), (1.0, 3.0), (0.5, 2.5)),
            ((0.5, 2.5), (0.0, 2.0), (0.0, 1.0), (0.5, 0.5)),
        )
        svgd = get_svgd_from_cpts(cpts)
        assert svgd == "M.5 .5C1 0 2 0 2.5 .5s.5 1.5 0 2S1 3 .5 2.5 0 1 .5 .5Z"

    def test_mid_curve(self):
        """Explicitly close anywhere a curve ends at the the start of a path."""
        cpts = (
            ((0.5, 0.5), (1.0, 0.0), (2.0, 0.0), (2.5, 0.5)),
            ((2.5, 0.5), (3.0, 1.0), (3.0, 2.0), (2.5, 2.5)),
            ((2.5, 2.5), (2.0, 3.0), (1.0, 3.0), (0.5, 0.5)),
            ((0.5, 0.5), (1.0, 0.0), (2.0, 0.0), (2.5, 0.5)),
        )
        svgd = get_svgd_from_cpts(cpts)
        assert svgd == "M.5 .5C1 0 2 0 2.5 .5s.5 1.5 0 2S1 3 .5 .5Zm0 0C1 0 2 0 2.5 .5"


def test_consecutive_l_at_start():
    """Test that consecutive L commands at the start of a path added to m."""
    svgd = "M0 0L1 2L2 1"
    cmds = PathCommands.from_svgd(svgd)
    assert_svgd_equal(cmds.abs_svgd, "M0 0 1 2 2 1")


class TestResolution:
    """Test that resolution is used in finding disjoint segments."""

    def test_resolution_from_cpts(self):
        """Test that resolution is used when generating SVG data from cpts."""
        cpts = [
            [(1 / 3, 2 / 3), (3 / 3, 4 / 3)],
            [(3 / 3, 4 / 3 + 1 / 1000), (5 / 3, 4 / 3 + 2 / 10000)],
        ]
        assert_svgd_equal(get_svgd_from_cpts(cpts, resolution=2), "M.33 .67 1 1.33h.67")

    def test_resolution_from_svgd(self):
        svgd = "M.333333 .67L1 1.33H1.67"
        cmds = PathCommands.from_svgd(svgd, resolution=2)
        assert_svgd_equal(cmds.abs_svgd, "M.33 .67 1 1.33H1.67")


class TestBreakCommand:
    """Test bad paths in Command and Commands."""

    def test_repr(self):
        """Test that the repr of a Command is correct."""
        cmd = PathCommand("m", [0, 0])
        assert repr(cmd) == "Command('M', [0.0, 0.0])"

    def test_arc_command(self):
        """Test that an arc command raises a ValueError."""
        svgd = "M0 0 A 1 1 0 0 1 1 1"
        cmds = PathCommands.from_svgd(svgd)
        with pytest.raises(ValueError) as excinfo:
            _ = cmds.cpts
        assert "Arc commands cannot be converted" in str(excinfo.value)


class TestArcCommand:
    def test_error_on_cpts(self):
        """Raise a ValueError if cpts is called on an arc command."""
        svgd = "M0 0 A 1 1 0 0 1 1 1"
        cmds = PathCommands.from_svgd(svgd)
        with pytest.raises(ValueError) as excinfo:
            _ = cmds.cpts
        assert "Arc commands cannot be converted" in str(excinfo.value)

    def test_relative_cmds_not_relative(self):
        """Test that relative arc commands are not converted to absolute."""
        svgd = "m1 2a3 4 5 6 7 8 9"
        abs_result = PathCommands.from_svgd(svgd).abs_svgd
        rel_result = PathCommands.from_svgd(svgd).rel_svgd
        assert abs_result == "M1 2A3 4 5 6 7 9 11"
        assert rel_result == "m1 2a3 4 5 6 7 8 9"


def test_close():
    """Interpret Z commands when calculating cpts."""
    svgd = "M0 0 L1 1 Z"
    cpts = get_cpts_from_svgd(svgd)
    assert cpts == [[(0.0, 0.0), (1.0, 1.0)], [(1.0, 1.0), (0.0, 0.0)]]


def test_shortest_mixes_rel_and_abs():
    """Test with a shortest path that mixes relative and absolute commands."""
    svgd = "M0 0 L1111 1111L1110 1111L0 1"
    cmds = PathCommands.from_svgd(svgd)
    assert cmds.svgd == "M0 0 1111 1111h-1L0 1"


potrace_output = par(
    """M338 236 c-5 -3 -6 -6 -3 -6 1 -1 2 -2 2 -3 0 -2 1 -2 2 -2 2 0 3 0 4 -1 2 -2 2
    -2 4 -1 1 2 2 2 3 1 2 -3 6 0 6 6 1 8 -4 9 -11 3 l-3 -3 0 4 c0 3 -1 4 -4 2z M170
    235 h1v2V55l0 6c-2 0 -5 -1 -5 -1 -1 -1 -3 -1 -4 -1 -3 0 -13 -5 -14 -6 -1 -1 -2 -2
    -4 -2 -3 0 -6 -2 -4 -3 1 -1 1 -1 0 -1 -1 -1 -1 -1 -1 0 0 1 -1 1 -1 1 -2 0 -5 -4
    -4 -5 0 -1 -1 -1 -2 -2 -1 0 -4 -3 -8 -6 -4 -4 -9 -8 -11 -9 -6 -5 -15 -14 -14 -15
    1 -1 0 -1 -2 -2 -4 0 -8 -4 -11 -10 -4 -7 -1 -6 3 1 2 4 3 5 2 3 0 -2 -1 -4 -2 -5
    -1 0 -1 -1 -1 -1 1 -1 5 1 5 2 0 1 0 1 1 1 1 0 1 0 1 -1 -2 -2 2 -8 4 -8 0 1 2 1 2
    1 1 0 1 1 1 1 0 1 2 4 4 7 5 6 5 6 -2 7 l-4 1 5 0 c4 -1 5 0 7 2 2 2 4 3 4 3 1 0 0
    -1 -2 -3 -3 -3 -3 -3 -1 -5 1 -1 1 -1 0 -1 -2 1 -11 -10 -9 -12 2 -3 6 -2 9 3 3 2 5
    4 6 3 1 0 0 -1 -3 -3 -6 -5 -8 -8 -6 -10 2 -1 3 -1 4 2 3 6 9 9 12 6 2 -1 6 -2 6 0
    0 1 -6 6 -7 6 -3 0 2 5 7 8 3 1 4 6 3 9 -1 1 8 5 11 5 1 0 0 -1 -2 -2 -7 -2 -11 -9
    -7 -10 4 -2 12 5 12 10 0 2 0 2 1 1 0 -1 1 -2 0 -3 0 -1 0 -1 1 0 2 1 1 4 -2 5 -2 0
    -2 0 0 1 1 1 3 3 4 4 0 1 1 3 2 3 0 0 1 0 2 0 0 1 0 1 -1 1 0 -1 -1 -1 -1 0 0 0 2 1
    4 2 2 1 4 3 4 3 0 1 0 1 1 0 2 -1 8 2 8 4 0 1 2 3 4 4 2 1 4 2 4 2 0 -1 -1 -2 -3 -3
    -2 0 -3 -1 -3 -2 1 0 0 -2 -2 -3 -3 -2 -2 -4 2 -2 4 3 5 2 1 0 -4 -3 -10 -9 -9 -9 0
    0 1 1 3 1 1 1 3 2 4 2 2 0 4 1 6 4 3 3 5 4 5 3 1 -1 2 0 4 1 l2 3 -2 -3 s1 2 3 4s1
    2 3 4t1 2t8 5 c-1 -2 -2 -3 -3 -2 -2 0 -9 -6 -9 -8 1 -3 4 -2 7 1 2 2 4 3 4 2 1 -1
    1 -1 1 0 1 0 2 1 2 0 2 0 17 13 17 14 -1 1 6 5 8 5 2 1 10 3 12 4 3 1 5 1 5 0 0 -1
    2 -2 6 -3 3 -1 8 -3 10 -5 3 -2 5 -3 6 -3 1 0 1 -1 1 -1 0 -1 1 -2 1 -3 1 0 3 -4 5
    -8 2 -4 4 -7 5 -7 0 0 1 -1 2 -2 0 -2 1 -2 1 -1 1 1 0 2 -2 5 -1 2 -2 3 -1 2 1 -1 2
    -1 2 0 0 0 1 1 1 1 1 0 1 0 1 1 0 2 1 2 2 1 3 -2 4 0 1 2 -1 1 -2 3 -2 3 0 1 -1 2
    -1 3 -2 0 -2 3 0 3 2 1 2 1 1 -1 0 -3 5 -10 9 -11 1 0 2 1 1 1 0 0 1 1 2 2 0 1 1 2
    1 3 0 2 3 3 16 3 5 1 6 1 4 0 -12 0 -14 -1 -14 -3 1 -3 4 -5 6 -3 1 1 4 1 6 2 1 0 4
    0 5 1 1 0 2 0 2 -1 0 -1 0 -2 -1 -2 -1 0 -1 0 -1 -1 0 -1 1 0 2 1 2 1 3 2 2 2 0 1 1
    1 2 0 2 -1 2 -1 0 -3 -2 -1 -3 -4 -1 -3 0 1 2 0 3 -1 2 -1 3 -1 3 0 0 1 1 1 3 1 4 0
    5 1 2 3 -2 1 -2 1 0 1 2 0 3 0 4 1 0 1 1 1 1 1 1 0 0 -1 -1 -2 -1 -2 -1 -2 0 -3 1
    -1 1 -1 2 0 1 1 1 1 2 0 2 -2 5 0 5 3 -1 4 0 6 1 4 1 -1 1 -1 1 1 0 2 -1 3 -1 2 -1
    0 -1 2 -2 4 0 2 -1 3 -2 3 0 -1 -1 0 -2 1 -1 0 -1 1 -1 1 1 0 0 1 0 3 -2 3 -5 4 -5
    2 0 -1 -1 -1 -1 1 0 1 -1 1 -1 0 0 -1 0 -1 -2 0 -1 2 -4 2 -17 2 -8 0 -15 0 -16 1
    -2 0 -15 -3 -19 -4 -2 -2 -3 -1 -8 0 -4 1 -7 2 -8 1 -1 0 -2 0 -2 1 0 1 -6 3 -8 3
    -1 0 -2 0 -2 1 -1 1 -1 1 -1 0 0 -1 -2 -1 -11 0 -2 0 -2 0 1 1 3 1 2 1 -2 1 -4 -1
    -7 -1 -7 -2 0 -1 -1 -1 -2 0 -1 1 -2 1 -3 0 -2 -2 -5 -3 -3 -1 0 1 -4 1 -9 -1 -3 -1
    -5 -1 -5 0 -1 1 -3 1 -5 1 -2 0 -6 1 -9 2 -4 0 -7 1 -8 1 -1 0 -4 -1 -6 -1Q1 2 3
    4Q4 2 5 3z"""
)


class TestCloseWithAxis:
    """Test that Z replaces V or H commands for closing paths."""

    def test_close_with_h(self):
        """Test that a horizontal line is closed with Z."""
        result = get_svgd_from_cpts([[(0, 0), (1, 0)], [(1, 0), (0, 0)]])
        assert result == "M0 0H1Z"

    def test_close_with_v(self):
        """Test that a horizontal line is closed with Z."""
        result = get_svgd_from_cpts([[(0, 0), (0, 1)], [(0, 1), (0, 0)]])
        assert result == "M0 0V1Z"


class TestPotraceOutput:
    def test_cycle(self) -> None:
        iterations: list[str] = []
        iterations.append(format_svgd_relative(potrace_output))
        iterations.append(format_svgd_relative(iterations[-1]))
        assert iterations[0] == iterations[1]


class TestValidateSvgd:
    def test_params_after_z(self):
        """Test that parameters after a Z command raise a ValueError."""
        svgd = "M0 0L1 1Z1 1"
        with pytest.raises(ValueError) as excinfo:
            _ = PathCommands.from_svgd(svgd)
        assert "Command Z takes 0" in str(excinfo.value)

    def test_does_not_start_with_m(self):
        """Test that a path not starting with M raises a ValueError."""
        svgd = "L1 1"
        with pytest.raises(ValueError) as excinfo:
            _ = PathCommands.from_svgd(svgd)
        assert "SVG path data must start with a move" in str(excinfo.value)

    def test_wrong_number_of_params(self):
        svgd = "M0 0L1"
        with pytest.raises(ValueError) as excinfo:
            _ = PathCommands.from_svgd(svgd)
        assert "Command L takes (some multiple of) 2" in str(excinfo.value)

    def test_junk_in_svgd(self):
        """Raise a ValueError if missed text looks like potential content."""
        svgd = "M0 0L1a 1b"
        with pytest.raises(ValueError) as excinfo:
            _ = PathCommands.from_svgd(svgd)
        assert "Unrecognized content 'b' in input" in str(excinfo.value)


class TestZeroLengthCurves:
    """Skip zero-length curves when generating SVG data from cpts."""

    def test_skip_zero_length_quadratic(self):
        """Skip zero-length quadratic curves."""
        cpts = [
            [(0, 0), (1, 1), (2, 2)],  # Normal quadratic
            [(2, 2), (2, 2), (2, 2)],  # Zero-length quadratic
            [(2, 2), (3, 3), (4, 4)],  # Normal quadratic
        ]
        result = get_svgd_from_cpts(cpts)
        assert result == "M0 0 4 4"

    def test_all_zeros(self):
        """Skip all-zero-length curves."""
        cpts = [
            [(0, 0), (0, 0), (0, 0), (0, 0)],
            [(0, 0), (0, 0), (0, 0), (0, 0)],
        ]
        result = get_svgd_from_cpts(cpts)
        assert result == ""

    def test_no_movement(self):
        """Skip non-path even if there is a movement."""
        cpts = [
            [(1, 1), (1, 1), (1, 1), (1, 1)],
            [(2, 2), (2, 2), (2, 2), (2, 2)],
            [(3, 3), (3, 3), (3, 3), (3, 3)],
        ]
        result = get_svgd_from_cpts(cpts)
        assert result == ""

    def test_empty_svgd_to_cpts(self):
        """An empty SVG data string results in an empty list of cpts."""
        cpts = get_cpts_from_svgd("")
        assert cpts == []

    def test_empty_cpts_to_svgd(self):
        """An empty list of cpts results in ty SVG data string."""
        svgd = get_svgd_from_cpts([])
        assert svgd == ""


class TestLinearCurves:
    """Test that linear curves are converted to L commands."""

    def test_no_t_after_m(self):
        """A T shortcut following a non-curve is a L command."""
        svgd = "M0 0L1 0T2 0"
        cmds = PathCommands.from_svgd(svgd)
        assert_svgd_equal(cmds.abs_svgd, "M0 0H2")

    def test_flatten_linear_curves(self):
        """Convert linear curves to L commands."""
        svgd = "M0 0Q1 1 2 2T4 4C5 5 6 6 7 7S9 9 10 10"
        cmds = PathCommands.from_svgd(svgd)
        assert_svgd_equal(cmds.abs_svgd, "M0 0 10 10")


cpts = [
    [(0, 0), (0, 0), (0, 0), (0, 0)],  # Zero-length quadratic
    [(0, 0), (0, 0), (0, 0), (0, 0)],  # Zero-length quadratic
]
