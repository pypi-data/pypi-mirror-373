"""
This is an example of what a video has:
- fps = 60
- time_base = 1 / 15360
- tick = fps * time_base = 256

So, the first pts is 0 and the second 
one is 256. The frame 16 will be 3840,
that is 256 * 15 (because first index
is 0).
"""
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from yta_validation.number import NumberValidator
from quicktions import Fraction
from typing import Union


class T:
    """
    Class to simplify the way we work with a
    't' time moment but using the fractions
    library to be precise and avoid any issue
    related with commas.

    This class must be used when trying to
    apply a specific 't' time moment for a 
    video or audio frame, using the fps or
    sample rate as time_base to be precise.
    """

    @property
    def truncated(
        self
    ) -> Fraction:
        """
        The 't' but as a Fraction that is multiple
        of the given 'time_base' and truncated.
        """
        return round_t(self._t, self.time_base)
    
    @property
    def rounded(
        self
    ) -> Fraction:
        """
        The 't' but as a Fraction that is multiple
        of the given 'time_base' and rounded (the
        value could be the same as truncated if it
        is closer to the previous value).
        """
        return round_t(self._t, self.time_base, do_truncate = False)
    
    @property
    def truncated_pts(
        self
    ) -> int:
        """
        The 'truncated' value but as a pts, which
        is the int value to be set in audio and 
        video frames in the pyav library to be
        displayed in that moment.
        """
        return int(self.truncated / self.time_base)
    
    @property
    def rounded_pts(
        self
    ) -> int:
        """
        The 'rounded' value but as a pts, which
        is the int value to be set in audio and 
        video frames in the pyav library to be
        displayed in that moment.
        """
        return int(self.rounded / self.time_base)

    def __init__(
        self,
        t: Union[int, float, Fraction],
        time_base: Fraction
    ):
        ParameterValidator.validate_mandatory_instance_of('t', t, [int, float, 'Fraction'])
        ParameterValidator.validate_mandatory_instance_of('time_base', time_base, 'Fraction')

        self._t: Union[int, float, Fraction] = t
        """
        The 't' time moment as it was passed as
        parameter.
        """
        self.time_base: Fraction = time_base
        """
        The time_base that will used to round the
        values to be multiples of it.
        """

    def next(
        self,
        n: int = 1
    ) -> 'T':
        """
        Get the value that is 'n' times ahead of
        the 'truncated' property of this instance.

        Useful when you need the next value for a
        range in an iteration or similar.
        """
        return T(self.truncated + n * self.time_base, self.time_base)
    
    def previous(
        self,
        n: int = 1
    ) -> 'T':
        """
        Get the value that is 'n' times before the
        'truncated' property of this instance.

        Useful when you need the previous value to
        check if the current is the next one or
        similar.

        Be careful, if the 'truncated' value is 0
        this will give you an unexpected negative
        value.
        """
        return T(self.truncated - n * self.time_base, self.time_base)
    
    @staticmethod
    def from_fps(
        t: Union[int, float, Fraction],
        fps: Union[int, float, Fraction]
    ) -> 'T':
        """
        Get the instance but providing the 'fps'
        (or sample rate) value directly, that will
        be turned into a time base.
        """
        return T(t, fps_to_time_base(fps))

    @staticmethod
    def from_pts(
        pts: int,
        time_base: Fraction
    ) -> 'T':
        """
        Get the instance but providing the 'pts'
        and the 'time_base'.
        """
        return T(pts * time_base, time_base)
    

# TODO: Careful with this below
"""
To obtain the pts step, or frame duration in
ticks, you need to apply 2 formulas that are
different according to if the frame is video
or audio:
- Audio: .samples
- Video: int(round((1 / .fps) / .time_base))
"""
    
def get_ts(
    start: Union[int, float, Fraction],
    end: Union[int, float, Fraction],
    fps: Fraction
) -> list[Fraction]:
    """
    Get all the 't' time moments between the given
    'start' and the given 'end', using the provided
    'time_base' for precision.

    The 'end' is not included, we return a range
    [start, end) because the last frame is the
    start of another time range.
    """
    start = T.from_fps(start, fps).truncated
    end = T.from_fps(end, fps).truncated

    time_base = fps_to_time_base(fps)
    return [
        start + i * time_base
        for i in range((end - start) // time_base)
    ]

def round_t(
    t: Union[int, float, Fraction],
    time_base = Fraction(1, 60),
    do_truncate: bool = True
):
    """
    Round the given 't' time moment to the most
    near multiple of the given 'time_base' (or
    the previous one if 'do_truncate' is True)
    using fractions module to be precise.

    This method is very useful to truncate 't'
    time moments in order to get the frames or
    samples for the specific and exact time 
    moments according to their fps or sample
    rate (that should be passed as the
    'time_base' parameter).

    Examples below, with `time_base = 1/5`:
    - `t = 0.25` => `0.2` (truncated or rounded)
    - `t = 0.35` => `0.2` (truncated)
    - `t = 0.45` => `0.4` (truncated or rounded)
    - `t = 0.55` => `0.6` (rounded)
    """
    t = Fraction(t).limit_denominator()
    steps = t / time_base

    snapped_steps = (
        steps.numerator // steps.denominator
        if do_truncate else
        round(steps) # round(float(steps))
    )

    return snapped_steps * time_base

def fps_to_time_base(
    fps: Union[int, float, Fraction]
) -> Fraction:
    """
    Get the pyav time base from the given
    'fps'.
    """
    return (
        Fraction(1, fps)
        if NumberValidator.is_int(fps) else
        Fraction(1, 1) / fps
        if PythonValidator.is_instance_of(fps, 'Fraction') else
        Fraction(1, 1) / Fraction.from_float(fps).limit_denominator(1000000) # if float
    )
