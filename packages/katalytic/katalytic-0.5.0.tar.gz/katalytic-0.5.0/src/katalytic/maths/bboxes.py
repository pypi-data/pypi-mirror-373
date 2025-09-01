from statistics import mean

from katalytic.data import pop_max
from katalytic.data.checks import is_sequence


def calc_bbox_area(bbox, fmt):
    """Calculate the area of a bounding box.

    Args:
        bbox (sequence): The bounding box whose area is to be calculated. It should be in the format specified by 'fmt'.
        fmt (str): The format of the bounding box. It could be one of the formats defined in `_FORMATS`.

    Returns:
        float: The area of the bounding box.
    """
    bbox = convert_bbox(bbox, fmt, "xy_wh") if fmt != "xy_wh" else bbox
    (_, _), (w, h) = bbox
    return w * h


def calc_bbox_center(bbox, fmt, *, as_int=False):
    """Calculate the center of a bounding box.

    Args:
        bbox (sequence): The bounding box whose center is to be calculated. It should be in the format specified by 'fmt'.
        fmt (str): The format of the bounding box. It could be one of the formats defined in `_FORMATS`.
        as_int (bool, optional): If True, the center coordinates are returned as integers. Defaults to False.

    Returns:
        tuple:
            The center of the bounding box as a tuple of two coordinates (x, y).
            If 'as_int' is True, the coordinates are integers, otherwise they are floats.
    """
    (x, y), (X, Y) = convert_bbox(bbox, fmt, "xy_XY")
    cx, cy = (mean([x, X]), mean([y, Y]))

    if as_int:
        return (int(cx), int(cy))
    else:
        return (cx, cy)


def calc_IoB(bbox_1, fmt_1, bbox_2, fmt_2):
    """Calculate the Intersection over Bounding-box (IoB) between two bounding boxes,
    which is defined as the area of the intersection of `bbox_1` and `bbox_2` divided by
    the area of `bbox_1`.

    Args:
        bbox_1 (sequence): The first bounding box, defined in the format specified by `fmt_1`.
        fmt_1 (str): The format of the first bounding box. This defines how the coordinates in `bbox_1` are interpreted.
        bbox_2 (sequence): The second bounding box, defined in the format specified by `fmt_2`.
        fmt_2 (str): The format of the second bounding box. This defines how the coordinates in `bbox_2` are interpreted.

    Returns:
        float: The IoB between `bbox_1` and `bbox_2` If they don't intersect, returns 0.
    """
    intersection = intersect_bboxes(bbox_1, fmt_1, bbox_2, fmt_2)
    if intersection is None:
        return 0

    inter_area = calc_bbox_area(intersection, fmt_1)
    return inter_area / calc_bbox_area(bbox_1, fmt_1)


def calc_IoB_max(bbox_1, fmt_1, bbox_2, fmt_2):
    """Return the largest of (Intersection over bbox_1) and (Intersection over bbox_2).

    Args:
        bbox_1 (sequence): The first bounding box, defined in the format specified by `fmt_1`.
        fmt_1 (str): The format of the first bounding box. This defines how the coordinates in `bbox_1` are interpreted.
        bbox_2 (sequence): The second bounding box, defined in the format specified by `fmt_2`.
        fmt_2 (str): The format of the second bounding box. This defines how the coordinates in `bbox_2` are interpreted.

    Returns:
        float: The largest IoB value between `bbox_1` and `bbox_2`.
    """
    return max(calc_IoB(bbox_1, fmt_1, bbox_2, fmt_2), calc_IoB(bbox_2, fmt_2, bbox_1, fmt_1))


def calc_IoB_min(bbox_1, fmt_1, bbox_2, fmt_2):
    """Return the smallest of (Intersection over bbox_1) and (Intersection over bbox_2).

    Args:
        bbox_1 (sequence): The first bounding box, defined in the format specified by `fmt_1`.
        fmt_1 (str): The format of the first bounding box. This defines how the coordinates in `bbox_1` are interpreted.
        bbox_2 (sequence): The second bounding box, defined in the format specified by `fmt_2`.
        fmt_2 (str): The format of the second bounding box. This defines how the coordinates in `bbox_2` are interpreted.

    Returns:
        float: The smallest IoB (Intersection over Bounding-box) value between `bbox_1` and `bbox_2`.
    """
    return min(calc_IoB(bbox_1, fmt_1, bbox_2, fmt_2), calc_IoB(bbox_2, fmt_2, bbox_1, fmt_1))


def calc_IoU(bbox_1, fmt_1, bbox_2, fmt_2):
    """Calculate the Intersection over Union (IoU) between two bounding boxes, defined
    as the area of their intersection divided by the area of their union.

    Args:
        bbox_1 (sequence): The first bounding box, defined in the format specified by `fmt_1`.
        fmt_1 (str): The format of the first bounding box. This defines how the coordinates in `bbox_1` are interpreted.
        bbox_2 (sequence): The second bounding box, defined in the format specified by `fmt_2`.
        fmt_2 (str): The format of the second bounding box. This defines how the coordinates in `bbox_2` are interpreted.

    Returns:
        float: The IoU of `bbox_1` and `bbox_2`. Returns 0 if `bbox_1` and `bbox_2` do not intersect.
    """
    intersection = intersect_bboxes(bbox_1, fmt_1, bbox_2, fmt_2)
    if intersection is None:
        return 0

    a1 = calc_bbox_area(bbox_1, fmt_1)
    a2 = calc_bbox_area(bbox_2, fmt_2)
    inter_area = calc_bbox_area(intersection, fmt_1)

    # the overlapping area is counted twice. Subtract it once
    union_area = a1 + a2 - inter_area
    return inter_area / union_area


def non_max_suppression(bboxes, format, *, max_IoU=0.5, scores=None):
    """Apply non-maximum suppression on a sequence of bounding boxes.

    Args:
        bboxes (list): A list of bounding boxes to perform non-maximum suppression on.
        format (str): The format in which the bounding boxes are specified.
        max_IoU (float, optional): The maximum IoU (Intersection over Union) value to consider a bounding box as a duplicate. Defaults to 0.5.
        scores (list, optional): A list of scores associated with each bounding box. If provided, must be the same length as `bboxes`.

    Raises:
        ValueError: If the format doesn't contain scores, and no `scores` argument is provided.

    Returns:
        list: The list of remaining bounding boxes after non-maximum suppression has been applied.
    """
    if not bboxes:
        return bboxes
    elif not format.endswith("s"):
        if scores:
            bboxes = set_bbox_scores(bboxes, scores, format, "xyXYs")
        else:
            raise ValueError(
                "If the format doesn't contain scores, either change the call "
                "to non_max_suppression(..., scores=...) or use set_bbox_scores()."
            )

    if format.endswith("s") and format != "xyXYs":
        # standardise the format to simplify the implementation
        bboxes = [convert_bbox(bbox, format, "xyXYs") for bbox in bboxes]

    kept, bboxes = pop_max(bboxes, condition=lambda bbox: bbox[-1])

    # remove bboxes with IoU > max_IoU than the kept bbox
    bboxes = [b for b in bboxes if calc_IoU(b, "xyXYs", kept, "xyXYs") < max_IoU]

    # call recursively on the remaining bboxes
    kept = [kept, *non_max_suppression(bboxes, "xyXYs", max_IoU=max_IoU)]

    if format != "xyXYs":
        # convert to the original format
        kept = [convert_bbox(bbox, "xyXYs", format) for bbox in kept]

    return kept


def set_bbox_scores(bboxes, scores, before, after):
    """Insert or change the existing scores of a list of bounding boxes.

    Args:
        bboxes (list): A list of bounding boxes to set scores for.
        scores (list): A list of scores to set for each bounding box. Must have the same length as `bboxes`.
        before (str): The format in which the bounding boxes are currently specified.
        after (str): The desired format for the bounding boxes after the scores have been set. This format must end with 's'.

    Raises:
        ValueError: If `bboxes` and `scores` don't have the same length, if the `after` format doesn't end with 's', or if any score is not within the range [0, 1].

    Returns:
        list: The list of bounding boxes with scores set, in the specified `after` format.
    """
    if len(bboxes) != len(scores):
        raise ValueError("bboxes and scores must have the same length")
    elif not after.endswith("s"):
        raise ValueError("after format must be one of xyXYs, xyXY_s, xy_XY_s, xywhs, xywh_s, xy_wh_s")
    elif not all(0 <= s <= 1 for s in scores):
        raise ValueError("scores must be in the range [0, 1]")

    if before != "xyXY":
        bboxes = [convert_bbox(bbox, before, "xyXY") for bbox in bboxes]

    bboxes = [(*bbox, s) for bbox, s in zip(bboxes, scores, strict=False)]
    if after == "xyXYs":
        return bboxes
    else:
        return [convert_bbox(bbox, "xyXYs", after) for bbox in bboxes]


def convert_bbox(bbox, before, after):
    """Convert a bounding box from one format to another.

    Args:
        bbox (sequence): The bounding box to convert. This should be in the format specified by `before`.
        before (str): The current format of the bounding box. This must be one of the recognized formats.
        after (str): The desired format for the bounding box. This must be one of the recognized formats.

    Raises:
        ValueError: If `before` or `after` are not recognized formats, if `bbox` is not in the `before` format, if `before` and `after` are the same, or if attempting to convert to a format that includes scores from a format that does not.

    Returns:
        sequence: The bounding box, converted to the `after` format.
    """
    if before not in _FORMATS:
        raise ValueError(f"Unknown before format {before!r}")
    elif after not in _FORMATS:
        raise ValueError(f"Unknown after format {after!r}")
    elif not is_bbox(bbox, before):
        raise ValueError(f"{bbox!r} is not in the {before!r} format")
    elif before == after:
        # I could just return the bbox, but I prefer to fail early
        # so the dev knows there might be a bug in his code
        # It makes the easy thing harder and the hard thing (debugging) easy
        raise ValueError(f"before and after formats are the same: {before!r}")
    elif after.endswith("s") and not before.endswith("s"):
        raise ValueError(f"Cannot convert from {before} to {after}")

    x = y = X = Y = w = h = s = None
    if before == "xywh":
        x, y, w, h = bbox
    elif before == "xywhs":
        x, y, w, h, s = bbox
    elif before == "xywh_s":
        (x, y, w, h), s = bbox
    elif before == "xy_wh":
        (x, y), (w, h) = bbox
    elif before == "xy_wh_s":
        (x, y), (w, h), s = bbox
    elif before == "xyXY":
        x, y, X, Y = bbox
    elif before == "xyXYs":
        x, y, X, Y, s = bbox
    elif before == "xyXY_s":
        (x, y, X, Y), s = bbox
    elif before == "xy_XY":
        (x, y), (X, Y) = bbox
    elif before == "xy_XY_s":
        (x, y), (X, Y), s = bbox

    if X is None:
        X = x + w
        Y = y + h
    elif w is None:
        w = X - x
        h = Y - y

    if after == "xywh":
        return x, y, w, h
    elif after == "xywhs":
        return x, y, w, h, s
    elif after == "xywh_s":
        return (x, y, w, h), s
    elif after == "xy_wh":
        return (x, y), (w, h)
    elif after == "xy_wh_s":
        return (x, y), (w, h), s
    elif after == "xyXY":
        return x, y, X, Y
    elif after == "xyXYs":
        return x, y, X, Y, s
    elif after == "xyXY_s":
        return (x, y, X, Y), s
    elif after == "xy_XY":
        return (x, y), (X, Y)
    elif after == "xy_XY_s":
        return (x, y), (X, Y), s


def intersect_bboxes(bbox_1, fmt_1, bbox_2, fmt_2):
    """Calculate the intersection of two bounding boxes.

    Args:
        bbox_1 (sequence): The first bounding box.
        fmt_1 (str): The format of the first bounding box.
        bbox_2 (sequence): The second bounding box.
        fmt_2 (str): The format of the second bounding box.

    Returns:
        list or None: The intersection of the two bounding boxes in the format of `fmt_1`, or `None` if the bounding boxes do not intersect.
    """
    if fmt_1.endswith("s"):
        s = bbox_1[-1]

    bbox_1 = convert_bbox(bbox_1, fmt_1, "xy_XY") if fmt_1 != "xy_XY" else bbox_1
    bbox_2 = convert_bbox(bbox_2, fmt_2, "xy_XY") if fmt_2 != "xy_XY" else bbox_2

    (x1, y1), (X1, Y1) = bbox_1
    (x2, y2), (X2, Y2) = bbox_2

    x3, y3 = max(x1, x2), max(y1, y2)
    X3, Y3 = min(X1, X2), min(Y1, Y2)

    if (0 <= x3 < X3) and (0 <= y3 < Y3):
        bbox_3 = [(x3, y3), (X3, Y3)]
        if fmt_1.endswith("s"):
            bbox_3 = convert_bbox([*bbox_3, s], "xy_XY_s", fmt_1)
        elif fmt_1 != "xy_XY":
            bbox_3 = convert_bbox(bbox_3, "xy_XY", fmt_1)

        return type(bbox_1)(bbox_3)
    else:
        return None


def is_bbox(bbox, fmt):
    """Check if the provided bounding box is of the specified format.

    Args:
        bbox (sequence): The bounding box to be checked.
        fmt (str): The format to check against.

    Returns:
        bool: `True` if the bounding box is of the specified format, `False` otherwise.

    Raises:
        ValueError: If the specified format is not recognized.
    """
    if fmt not in _FORMATS:
        available = ", ".join(_FORMATS)
        raise ValueError(f"Unknown format {fmt!r}. Available formats: {available}")

    return _FORMATS[fmt](bbox)


def _is_xy_wh(bbox):
    """WARNING:
    Returns True if the bbox has the xy_XY format
    There's no way to check against that case

    Kept hidden to avoid cluttering the namespace
    """
    if not is_sequence(bbox):
        raise TypeError(f"Expected a sequence, got {type(bbox)}")

    try:
        (x, y), (w, h) = bbox
        return (x >= 0) and (y >= 0) and (w > 0) and (h > 0)
    except ValueError as e:
        if str(e).startswith("not enough values to unpack") or str(e).startswith("too many values to unpack"):
            return False
        else:
            raise
    except TypeError as e:
        if (
            str(e).startswith("cannot unpack non-iterable")
            or "not supported between instances of" in str(e)
            or "object is not iterable" in str(e)
        ):
            return False
        else:
            raise


def _is_xy_wh_s(bbox):
    """WARNING:
    Returns True if the bbox has the xy_XY format
    There's no way to check against that case

    Kept hidden to avoid cluttering the namespace
    """
    if not is_sequence(bbox):
        raise TypeError(f"Expected a sequence, got {type(bbox)}")

    try:
        (x, y), (w, h), s = bbox
        return (x >= 0) and (y >= 0) and (w > 0) and (h > 0) and 0 <= s <= 1
    except ValueError as e:
        if str(e).startswith("not enough values to unpack") or str(e).startswith("too many values to unpack"):
            return False
        else:
            raise
    except TypeError as e:
        if (
            str(e).startswith("cannot unpack non-iterable")
            or "not supported between instances of" in str(e)
            or "object is not iterable" in str(e)
        ):
            return False
        else:
            raise


def _is_xy_XY(bbox):
    """WARNING:
    Returns True if the bbox has the xy_wh format and x < w and y < h
    There's no way to check against that case

    Kept hidden to avoid cluttering the namespace
    """
    if not is_sequence(bbox):
        raise TypeError(f"Expected a sequence, got {type(bbox)}")

    try:
        (x, y), (X, Y) = bbox
        return (0 <= x < X) and (0 <= y < Y)
    except ValueError as e:
        if str(e).startswith("not enough values to unpack") or str(e).startswith("too many values to unpack"):
            return False
        else:
            raise
    except TypeError as e:
        if (
            str(e).startswith("cannot unpack non-iterable")
            or "not supported between instances of" in str(e)
            or "object is not iterable" in str(e)
        ):
            return False
        else:
            raise


def _is_xy_XY_s(bbox):
    """WARNING:
    Returns True if the bbox has the xywh format and x < w and y < h
    There's no way to check against that case

    Kept hidden to avoid cluttering the namespace
    """
    if not is_sequence(bbox):
        raise TypeError(f"Expected a sequence, got {type(bbox)}")

    try:
        (x, y), (X, Y), s = bbox
        return (0 <= x < X) and (0 <= y < Y) and 0 <= s <= 1
    except ValueError as e:
        if str(e).startswith("not enough values to unpack") or str(e).startswith("too many values to unpack"):
            return False
        else:
            raise
    except TypeError as e:
        if (
            str(e).startswith("cannot unpack non-iterable")
            or "not supported between instances of" in str(e)
            or "object is not iterable" in str(e)
        ):
            return False
        else:
            raise


def _is_xywh(bbox):
    """WARNING:
    Returns True if the bbox has the xyXY format
    There's no way to check against that case

    Kept hidden to avoid cluttering the namespace
    """
    if not is_sequence(bbox):
        raise TypeError(f"Expected a sequence, got {type(bbox)}")

    try:
        (x, y, w, h) = bbox
        return (x >= 0) and (y >= 0) and (w > 0) and (h > 0)
    except ValueError as e:
        if str(e).startswith("not enough values to unpack") or str(e).startswith("too many values to unpack"):
            return False
        else:
            raise
    except TypeError as e:
        if (
            str(e).startswith("cannot unpack non-iterable")
            or "not supported between instances of" in str(e)
            or "object is not iterable" in str(e)
        ):
            return False
        else:
            raise


def _is_xywh_s(bbox):
    """WARNING:
    Returns True if the bbox has the xyXY format
    There's no way to check against that case

    Kept hidden to avoid cluttering the namespace
    """
    if not is_sequence(bbox):
        raise TypeError(f"Expected a sequence, got {type(bbox)}")

    try:
        (x, y, w, h), s = bbox
        return (x >= 0) and (y >= 0) and (w > 0) and (h > 0) and 0 <= s <= 1
    except ValueError as e:
        if str(e).startswith("not enough values to unpack") or str(e).startswith("too many values to unpack"):
            return False
        else:
            raise
    except TypeError as e:
        if (
            str(e).startswith("cannot unpack non-iterable")
            or "not supported between instances of" in str(e)
            or "object is not iterable" in str(e)
        ):
            return False
        else:
            raise


def _is_xywhs(bbox):
    """WARNING:
    Returns True if the bbox has the xyXY format
    There's no way to check against that case

    Kept hidden to avoid cluttering the namespace
    """
    if not is_sequence(bbox):
        raise TypeError(f"Expected a sequence, got {type(bbox)}")

    try:
        (x, y, w, h, s) = bbox
        return (x >= 0) and (y >= 0) and (w > 0) and (h > 0) and 0 <= s <= 1
    except ValueError as e:
        if str(e).startswith("not enough values to unpack") or str(e).startswith("too many values to unpack"):
            return False
        else:
            raise
    except TypeError as e:
        if (
            str(e).startswith("cannot unpack non-iterable")
            or "not supported between instances of" in str(e)
            or "object is not iterable" in str(e)
        ):
            return False
        else:
            raise


def _is_xyXY(bbox):
    """WARNING:
    Returns True if the bbox has the xywh format and x < w and y < h
    There's no way to check against that case

    Kept hidden to avoid cluttering the namespace
    """
    if not is_sequence(bbox):
        raise TypeError(f"Expected a sequence, got {type(bbox)}")

    try:
        (x, y, X, Y) = bbox
        return (0 <= x < X) and (0 <= y < Y)
    except ValueError as e:
        if str(e).startswith("not enough values to unpack") or str(e).startswith("too many values to unpack"):
            return False
        else:
            raise
    except TypeError as e:
        if (
            str(e).startswith("cannot unpack non-iterable")
            or "not supported between instances of" in str(e)
            or "object is not iterable" in str(e)
        ):
            return False
        else:
            raise


def _is_xyXY_s(bbox):
    """WARNING:
    Returns True if the bbox has the xywh format and x < w and y < h
    There's no way to check against that case

    Kept hidden to avoid cluttering the namespace
    """
    if not is_sequence(bbox):
        raise TypeError(f"Expected a sequence, got {type(bbox)}")

    try:
        (x, y, X, Y), s = bbox
        return (0 <= x < X) and (0 <= y < Y) and 0 <= s <= 1
    except ValueError as e:
        if str(e).startswith("not enough values to unpack") or str(e).startswith("too many values to unpack"):
            return False
        else:
            raise
    except TypeError as e:
        if (
            str(e).startswith("cannot unpack non-iterable")
            or "not supported between instances of" in str(e)
            or "object is not iterable" in str(e)
        ):
            return False
        else:
            raise


def _is_xyXYs(bbox):
    """WARNING:
    Returns True if the bbox has the xywh format and x < w and y < h
    There's no way to check against that case

    Kept hidden to avoid cluttering the namespace
    """
    if not is_sequence(bbox):
        raise TypeError(f"Expected a sequence, got {type(bbox)}")

    try:
        (x, y, X, Y, s) = bbox
        return (0 <= x < X) and (0 <= y < Y) and 0 <= s <= 1
    except ValueError as e:
        if str(e).startswith("not enough values to unpack") or str(e).startswith("too many values to unpack"):
            return False
        else:
            raise
    except TypeError as e:
        if (
            str(e).startswith("cannot unpack non-iterable")
            or "not supported between instances of" in str(e)
            or "object is not iterable" in str(e)
        ):
            return False
        else:
            raise


# Define at the end of the file because it requires
# the functions to be already defined
_FORMATS = {
    "xyXY": _is_xyXY,
    "xyXY_s": _is_xyXY_s,
    "xyXYs": _is_xyXYs,
    "xy_XY": _is_xy_XY,
    "xy_XY_s": _is_xy_XY_s,
    "xy_wh": _is_xy_wh,
    "xy_wh_s": _is_xy_wh_s,
    "xywh": _is_xywh,
    "xywh_s": _is_xywh_s,
    "xywhs": _is_xywhs,
}
