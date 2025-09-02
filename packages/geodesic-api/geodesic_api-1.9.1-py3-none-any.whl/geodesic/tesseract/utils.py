import datetime
from typing import Union
import numpy as np
from geodesic.bases import _APIObject
from geodesic.descriptors import _DatetimeDescr, _TimeDeltaDescr
from geodesic.tesseract.components import StridedBinning, BinSelection
from geodesic.utils import DeferredImport

plt = DeferredImport("matplotlib.pyplot")
mpl = DeferredImport("matplotlib")
animation = DeferredImport("matplotlib.animation")

display = DeferredImport("IPython.display")


def create_strided_binning(
    start: Union[datetime.datetime, np.datetime64, str],
    end: Union[datetime.datetime, np.datetime64, str],
    stride: Union[datetime.timedelta, np.timedelta64, str],
    duration: Union[datetime.timedelta, np.timedelta64, str],
):
    """Creates a StridedBinning object given start, end, stride, and duration.

    This creates a StridedBinning object that can be used in any step of a Tesseract job that uses
    temporal binning. Strided binning is the most commonly used way to create uniformly spaced and
    sized time bins. This utility helps create bins between a start and end with a given stride and
    duration.

    Bins will begin at `start`, the starts will be spaced in intervals of `stride`, be `duration`
    wide and end before or equal to `end`.

    Args:
        start: the start datetime for the binning
        end: the end datetime for the binning
        stride: the time apart each of the left bin edges will be spaced
        duration: how long each bin will be

    Returns:
        a StridedBinning object.
    """

    class Bounds(_APIObject):
        start = _DatetimeDescr()
        end = _DatetimeDescr()
        duration = _TimeDeltaDescr()
        stride = _TimeDeltaDescr()

    bounds = Bounds(start=start, end=end, stride=stride, duration=duration)

    total_seconds = (bounds.end - bounds.start).total_seconds()
    duration_seconds = bounds.duration.total_seconds()
    stride_seconds = bounds.stride.total_seconds()

    count = 1 + int((total_seconds - duration_seconds) / stride_seconds)

    return StridedBinning(
        from_selection=BinSelection(datetime=start),
        duration=bounds["duration"],
        stride=bounds["stride"],
        count=count,
    )
