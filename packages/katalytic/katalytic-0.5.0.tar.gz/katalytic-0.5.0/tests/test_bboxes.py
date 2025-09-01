import itertools

import pytest

from katalytic._pkg import all_types_besides
from katalytic.maths.bboxes import (
    _FORMATS,
    calc_bbox_area,
    calc_bbox_center,
    calc_IoB,
    calc_IoB_max,
    calc_IoB_min,
    calc_IoU,
    convert_bbox,
    intersect_bboxes,
    is_bbox,
    non_max_suppression,
    set_bbox_scores,
)

_EXAMPLES = {
    "xyXY": (1, 2, 9, 9),
    "xyXY_s": ((1, 2, 9, 9), 0.5),
    "xyXYs": (1, 2, 9, 9, 0.5),
    "xy_XY": ((1, 2), (9, 9)),
    "xy_XY_s": ((1, 2), (9, 9), 0.5),
    "xy_wh": ((1, 2), (8, 7)),
    "xy_wh_s": ((1, 2), (8, 7), 0.5),
    "xywh": (1, 2, 8, 7),
    "xywh_s": ((1, 2, 8, 7), 0.5),
    "xywhs": (1, 2, 8, 7, 0.5),
}


def _check_all_besides(bbox, blacklist):
    formats = set(_FORMATS) - set(blacklist)
    return list(itertools.product([bbox], formats))


def _pick_all_besides(blacklist):
    return [bbox for fmt, bbox in _EXAMPLES.items() if fmt not in blacklist]


def _generate_all_possible_conversions():
    all_combinations = itertools.product(_EXAMPLES.items(), _EXAMPLES.items())
    possible = []
    for (fmt_1, box_1), (fmt_2, box_2) in all_combinations:
        if (fmt_2.endswith("s") and not fmt_1.endswith("s")) or fmt_2 == fmt_1:
            continue

        possible.append((box_1, fmt_1, fmt_2, box_2))

    return possible


def _generate_all_impossible_conversions():
    all_combinations = itertools.product(_EXAMPLES.items(), _EXAMPLES.items())
    impossible = []
    for (fmt_1, box_1), (fmt_2, box_2) in all_combinations:
        if fmt_2.endswith("s") and not fmt_1.endswith("s"):
            impossible.append((box_1, fmt_1, fmt_2))

    return impossible


class Test_calc_area:
    @pytest.mark.parametrize("fmt, bbox", _EXAMPLES.items())
    def test_all_formats(self, fmt, bbox):
        assert calc_bbox_area(bbox, fmt) == 8 * 7

    @pytest.mark.parametrize(
        "bbox, fmt, area",
        [
            ((0, 0, 5, 5), "xyXY", 25),
            ((0, 0, 10, 10), "xywh", 100),
            ((0, 0, 1, 5), "xyXY", 5),
            ((0, 0, 10, 1), "xywh", 10),
        ],
    )
    def test_basic(self, bbox, fmt, area):
        assert calc_bbox_area(bbox, fmt) == area


class Test_convert_bbox:
    @pytest.mark.parametrize("wrong_type", all_types_besides("sequences"))
    def test_wrong_type(self, wrong_type):
        with pytest.raises(TypeError):
            convert_bbox(wrong_type, "xyXY", "xywh")

    @pytest.mark.parametrize("bbox, before, after, _", _generate_all_possible_conversions())
    def test_not_the_specified_format(self, bbox, before, after, _):
        # skip false positives
        if ("wh" in before and "XY" in after) or ("XY" in before and "wh" in after):
            return

        with pytest.raises(ValueError):
            convert_bbox(bbox, after, before)

    @pytest.mark.parametrize("fmt, bbox", _EXAMPLES.items())
    def test_same_format(self, fmt, bbox):
        with pytest.raises(ValueError):
            convert_bbox(bbox, fmt, fmt)

    @pytest.mark.parametrize("wrong_format", [1, None, "asd", "qwerty"])
    def test_wrong_format(self, wrong_format):
        with pytest.raises(ValueError):
            convert_bbox((1, 2, 3, 4), "xywh", wrong_format)

        with pytest.raises(ValueError):
            convert_bbox((1, 2, 3, 4), wrong_format, "xywh")

    @pytest.mark.parametrize("bbox, before, after", _generate_all_impossible_conversions())
    def test_impossible(self, bbox, before, after):
        with pytest.raises(ValueError):
            convert_bbox(bbox, before, after)

    @pytest.mark.parametrize("bbox, before, after, expected", _generate_all_possible_conversions())
    def test_expected(self, bbox, before, after, expected):
        assert convert_bbox(bbox, before, after) == expected


class Test_calc_bbox_center:
    @pytest.mark.parametrize(
        "bbox, fmt, expected", [((0, 0, 5, 4), "xyXY", (2.5, 2)), ((0, 0, 3, 10), "xywh", (1.5, 5.0))]
    )
    def test_float(self, bbox, fmt, expected):
        assert calc_bbox_center(bbox, fmt) == expected

    @pytest.mark.parametrize("bbox, fmt, expected", [((0, 0, 5, 4), "xyXY", (2, 2)), ((0, 0, 3, 10), "xywh", (1, 5))])
    def test_int(self, bbox, fmt, expected):
        assert calc_bbox_center(bbox, fmt, as_int=True) == expected


class Test_calc_IoU:
    @pytest.mark.parametrize(
        "bbox, fmt_1, bbox_2, fmt_2",
        [((0, 0, 5, 5), "xyXY", (5, 5, 10, 10), "xyXY"), ((1, 1, 4, 4), "xywh", (6, 6, 9, 9), "xyXY")],
    )
    def test_no_overlap(self, bbox, fmt_1, bbox_2, fmt_2):
        assert calc_IoU(bbox, fmt_1, bbox_2, fmt_2) == 0

    @pytest.mark.parametrize(
        "bbox_1, fmt_1, bbox_2, fmt_2",
        [
            ((0, 0, 5, 5), "xyXY", (0, 0, 5, 5), "xyXY"),
            ((1, 1, 4, 4), "xywh", (1, 1, 5, 5), "xyXY"),
            (((1, 1), (4, 4), 0.3), "xy_wh_s", ((1, 1), (5, 5), 0.6), "xy_XY_s"),
        ],
    )
    def test_perfect_overlap(self, bbox_1, fmt_1, bbox_2, fmt_2):
        assert calc_IoU(bbox_1, fmt_1, bbox_2, fmt_2) == 1

    @pytest.mark.parametrize(
        "bbox_1, fmt_1, bbox_2, fmt_2, expected",
        [
            ((0, 0, 5, 5), "xyXY", (3, 4, 7, 7), "xyXY", 0.05714285714285714),
            ((0, 0, 5, 5), "xyXY", (1, 1, 6, 6), "xyXY", 0.47058823529411764),
            (((0, 0, 5, 5), 0.9), "xyXY_s", (0, 1, 10, 3), "xywh", 0.375),
        ],
    )
    def test_partial_overlap(self, bbox_1, fmt_1, bbox_2, fmt_2, expected):
        assert calc_IoU(bbox_1, fmt_1, bbox_2, fmt_2) == expected


class Test_calc_IoB:
    @pytest.mark.parametrize(
        "bbox, fmt_1, bbox_2, fmt_2",
        [((0, 0, 5, 5), "xyXY", (5, 5, 10, 10), "xyXY"), ((1, 1, 4, 4), "xywh", (6, 6, 9, 9), "xyXY")],
    )
    def test_no_overlap(self, bbox, fmt_1, bbox_2, fmt_2):
        assert calc_IoB(bbox, fmt_1, bbox_2, fmt_2) == 0

    @pytest.mark.parametrize(
        "bbox_1, fmt_1, bbox_2, fmt_2",
        [
            ((0, 0, 5, 5), "xyXY", (0, 0, 5, 5), "xyXY"),
            ((1, 1, 4, 4), "xywh", (1, 1, 5, 5), "xyXY"),
            (((1, 1), (4, 4), 0.3), "xy_wh_s", ((1, 1), (5, 5), 0.6), "xy_XY_s"),
        ],
    )
    def test_perfect_overlap(self, bbox_1, fmt_1, bbox_2, fmt_2):
        assert calc_IoB(bbox_1, fmt_1, bbox_2, fmt_2) == 1

    @pytest.mark.parametrize(
        "bbox_1, fmt_1, bbox_2, fmt_2, expected",
        [
            ((0, 0, 5, 5), "xyXY", (3, 4, 7, 7), "xyXY", 0.08),
            ((0, 0, 5, 5), "xyXY", (1, 1, 6, 6), "xyXY", 0.64),
            (((0, 0, 5, 5), 0.9), "xyXY_s", (0, 1, 10, 3), "xywh", 0.6),
        ],
    )
    def test_partial_overlap(self, bbox_1, fmt_1, bbox_2, fmt_2, expected):
        assert calc_IoB(bbox_1, fmt_1, bbox_2, fmt_2) == expected


class Test_calc_IoB_min:
    @pytest.mark.parametrize(
        "bbox_1, fmt_1, bbox_2, fmt_2, expected",
        [
            ((0, 0, 5, 5), "xyXY", (3, 4, 7, 7), "xyXY", 0.08),
            ((0, 0, 5, 5), "xyXY", (1, 1, 6, 6), "xyXY", 0.64),
            (((0, 0, 5, 5), 0.9), "xyXY_s", (0, 1, 10, 3), "xywh", 0.5),
        ],
    )
    def test_partial_overlap(self, bbox_1, fmt_1, bbox_2, fmt_2, expected):
        assert calc_IoB_min(bbox_1, fmt_1, bbox_2, fmt_2) == expected


class Test_calc_IoB_max:
    @pytest.mark.parametrize(
        "bbox_1, fmt_1, bbox_2, fmt_2, expected",
        [
            ((0, 0, 5, 5), "xyXY", (3, 4, 7, 7), "xyXY", 0.16666666666666666),
            ((0, 0, 5, 5), "xyXY", (1, 1, 6, 6), "xyXY", 0.64),
            (((0, 0, 5, 5), 0.9), "xyXY_s", (0, 1, 10, 3), "xywh", 0.6),
        ],
    )
    def test_partial_overlap(self, bbox_1, fmt_1, bbox_2, fmt_2, expected):
        assert calc_IoB_max(bbox_1, fmt_1, bbox_2, fmt_2) == expected


class Test_set_bbox_scores:
    @pytest.mark.parametrize("after", ["xywh", "xy_XY", "xy_wh"])
    def test_invalid_after_format(self, after):
        with pytest.raises(ValueError):
            set_bbox_scores([(1, 2, 3, 4)], [0], "xyXY", after)

    @pytest.mark.parametrize("scores", [-1, -0.1, 1.1, 2, 3.5])
    def test_invalid_scores(self, scores):
        with pytest.raises(ValueError):
            set_bbox_scores([(1, 2, 3, 4)], [scores], "xyXY", "xyXYs")

    @pytest.mark.parametrize("bboxes, scores", [([(1, 2, 3, 4)], [1, 0.2]), ([(1, 2, 3, 4), (1, 2, 3, 4)], [1])])
    def test_unequal_lengths(self, bboxes, scores):
        with pytest.raises(ValueError):
            set_bbox_scores(bboxes, scores, "xyXY", "xyXYs")

    @pytest.mark.parametrize(
        "bboxes, scores, before, after, expected",
        [
            ([((1, 2), (3, 4))], [1], "xy_XY", "xyXYs", [(1, 2, 3, 4, 1)]),
            ([((1, 2), (3, 4)), ((2, 2), (3, 4))], [1, 0.2], "xy_XY", "xyXYs", [(1, 2, 3, 4, 1), (2, 2, 3, 4, 0.2)]),
            ([((1, 2, 3, 4)), ((2, 2, 3, 4))], [1, 0.2], "xyXY", "xyXY_s", [((1, 2, 3, 4), 1), ((2, 2, 3, 4), 0.2)]),
        ],
    )
    def test_ok(self, bboxes, scores, before, after, expected):
        assert set_bbox_scores(bboxes, scores, before, after) == expected


class Test_non_max_suppression:
    def test_no_scores(self):
        with pytest.raises(ValueError):
            non_max_suppression([(1, 2, 3, 4)], "xyXY")

    def test_scores(self):
        bboxes = [(1, 2, 3, 4), (5, 6, 7, 8), (5, 6, 7, 7)]
        expected = [(1, 2, 3, 4), (5, 6, 7, 8)]
        scores = [0.9, 0.8, 0.7]
        assert non_max_suppression(bboxes, "xyXY", scores=scores) == expected

    def test_empty(self):
        assert non_max_suppression([], "xyXYs") == []

    def test_perfect_overlap(self):
        bboxes = [((10, 10, 100, 100), 0.9), ((10, 10, 100, 100), 0.8), ((10, 10, 100, 100), 0.7)]

        assert non_max_suppression(bboxes, "xyXY_s") == [((10, 10, 100, 100), 0.9)]

    def test_no_overlap(self):
        bboxes = expected = [[10, 10, 50, 50, 0.9], [60, 60, 100, 100, 0.8]]

        assert non_max_suppression(bboxes, "xyXYs") == expected

    def test_partial_overlap(self):
        bboxes = [
            [10, 10, 100, 100, 0.9],
            [100, 100, 190, 190, 0.6],
            [100, 100, 185, 185, 0.7],
            [90, 90, 190, 190, 0.7],
            [50, 50, 150, 150, 0.8],
        ]

        assert non_max_suppression(bboxes, "xyXYs") == [
            [10, 10, 100, 100, 0.9],
            [50, 50, 150, 150, 0.8],
            [100, 100, 185, 185, 0.7],
        ]


class Test_intersect_bboxes:
    @pytest.mark.parametrize(
        "bbox_1, fmt_1, bbox_2, fmt_2",
        [((0, 0, 5, 5), "xyXY", (5, 5, 10, 10), "xyXY"), ((1, 1, 4, 4), "xywh", (6, 6, 9, 9), "xyXY")],
    )
    def test_no_overlap(self, bbox_1, fmt_1, bbox_2, fmt_2):
        assert intersect_bboxes(bbox_1, fmt_1, bbox_2, fmt_2) is None

    @pytest.mark.parametrize(
        "bbox_1, fmt_1, bbox_2, fmt_2",
        [
            ((0, 0, 5, 5), "xyXY", (0, 0, 5, 5), "xyXY"),
            ((1, 1, 4, 4), "xywh", (1, 1, 5, 5), "xyXY"),
            (((1, 1), (4, 4), 0.3), "xy_wh_s", ((1, 1), (5, 5), 0.6), "xy_XY_s"),
        ],
    )
    def test_perfect_overlap(self, bbox_1, fmt_1, bbox_2, fmt_2):
        assert intersect_bboxes(bbox_1, fmt_1, bbox_2, fmt_2) == bbox_1

    @pytest.mark.parametrize(
        "bbox_1, fmt_1, bbox_2, fmt_2, expected",
        [
            ((0, 0, 5, 5), "xyXY", (3, 4, 7, 7), "xyXY", (3, 4, 5, 5)),
            (((0, 0, 5, 5), 0.9), "xyXY_s", (0, 1, 10, 3), "xywh", ((0, 1, 5, 4), 0.9)),
        ],
    )
    def test_partial_overlap(self, bbox_1, fmt_1, bbox_2, fmt_2, expected):
        assert intersect_bboxes(bbox_1, fmt_1, bbox_2, fmt_2) == expected


class Test_is_bbox:
    @pytest.mark.parametrize("wrong_type", all_types_besides("sequences"))
    def test_wrong_format(self, wrong_type):
        with pytest.raises(TypeError):
            is_bbox(wrong_type, "xyXY")

    @pytest.mark.parametrize("fmt", ["XYXY", "whxy", ""])
    def test_bad_fmt(self, fmt):
        with pytest.raises(ValueError):
            is_bbox((1, 2, 3, 4), fmt)

    @pytest.mark.parametrize("fmt, bbox", _EXAMPLES.items())
    def test_True(self, fmt, bbox):
        assert is_bbox(bbox, fmt)

    @pytest.mark.parametrize(
        "bbox, fmt",
        [
            *_check_all_besides((), []),
            *_check_all_besides(range(1), []),
            *_check_all_besides(range(2), []),
            *_check_all_besides(range(3), []),
            *_check_all_besides((*range(4), -0.1), []),
            *_check_all_besides((*range(4), 1.1), []),
            *_check_all_besides((*range(4), 2), []),
            *_check_all_besides(range(6), []),
            *_check_all_besides(((1, 2), (3, 4), (5, 6), (7, 8)), []),
            *_check_all_besides(((1, 2), (1, 1)), ["xy_wh"]),
            *_check_all_besides(((1, 2), (1, 1), 0.5), ["xy_wh_s"]),
            *_check_all_besides((1, 2, 1, 1), ["xywh"]),
            *_check_all_besides(((1, 2, 1, 1), 0.5), ["xywh_s"]),
            *_check_all_besides((1, 2, 1, 1, 0.5), ["xywhs"]),
            # There's no way to check correctly against the "wh" equivalents
            # They would return false positives and make the test fail
            *_check_all_besides((1, 2, 3, 4), ["xyXY", "xywh"]),
            *_check_all_besides(((1, 2, 3, 4), 0.5), ["xyXY_s", "xywh_s"]),
            *_check_all_besides((1, 2, 3, 4, 0.5), ["xyXYs", "xywhs"]),
            *_check_all_besides(((1, 2), (3, 4)), ["xy_XY", "xy_wh"]),
            *_check_all_besides(((1, 2), (3, 4), 0.5), ["xy_XY_s", "xy_wh_s"]),
        ],
    )
    def test_False(self, bbox, fmt):
        assert not is_bbox(bbox, fmt)
