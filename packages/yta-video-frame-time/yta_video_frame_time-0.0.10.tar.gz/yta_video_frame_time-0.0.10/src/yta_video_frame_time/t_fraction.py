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
from yta_validation.number import NumberValidator
from yta_validation import PythonValidator
from quicktions import Fraction
from typing import Union

import math


# TODO: This T class has to be removed
# and replaced by the THandler
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
    

# TODO: This below is interesting, above
# is old...

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
    thandler = THandler(fps)

    start = thandler.t.truncated(start)
    end = thandler.t.truncated(end)

    return [
        start + i * thandler.time_base
        for i in range((end - start) // thandler.time_base)
    ]

def round_t(
    t: Union[int, float, Fraction],
    time_base = Fraction(1, 60),
    do_truncate: bool = True
) -> Fraction:
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

    return parse_fraction(snapped_steps * time_base)

def round_pts(
    pts: int,
    fps: Union[int, float, Fraction] = 60,
    time_base = Fraction(1, 60),
    do_truncate: bool = True
) -> int:
    """
    Round the given 'pts' presentation
    timestamp to the most near index 
    corresponding pts value (or the previous
    one always if 'do_truncate' is True).

    This method is very useful to truncate 
    'pts' values in order to get the frames or
    samples for the specific and exact time 
    moments according to their fps or sample
    rate (that should be passed as the
    'time_base' parameter).

    Pts value is calculated based on the 'fps'
    and 'time_base', but here is an easier
    example using the time moments.

    (!) This is valid only for video.

    Examples below, with `time_base = 1/5`:
    - `t = 0.25` => `0.2` (truncated or rounded)
    - `t = 0.35` => `0.2` (truncated)
    - `t = 0.45` => `0.4` (truncated or rounded)
    - `t = 0.55` => `0.6` (rounded)
    """
    ticks_per_frame = get_ticks_per_frame(fps, time_base)

    frame_index = pts / ticks_per_frame

    frame_index = (
        math.floor(frame_index)
        if do_truncate else
        round(frame_index)
    )
    
    return int(frame_index * ticks_per_frame)

"""
When we are working with the 't' time
moment we need to use the fps, and when
we are working with the 'pts' we need 
to use the 'time_base'.
"""

class _T:
    """
    Internal class to be used by the THandler
    as a shortcut to the functionality 
    related with 't' values.
    """

    def __init__(
        self,
        t_handler: 'THandler'
    ):
        self._t_handler: THandler = t_handler
        """
        Instance of the parent THandler to
        access to its properties.
        """

    def from_pts(
        self,
        pts: int,
        do_truncate: Union[bool, None] = True
    ) -> Fraction:
        """
        Get the 't' time moment for the frame
        defined by the 'pts' presentation
        timestamp.

        If 't' is in a [start, end) range, we
        will obtain the 'start' value if 't'
        value is closer to it than to the 'end
        value.

        If 'do_truncate' is True, we will
        always receive the 'start' value. If
        None, we will not make any conversion
        and the value received could be useless
        because it is in the middle of a range.

        The formula:
        - `pts * time_base`
        """
        t = Fraction(pts * self._t_handler.time_base)

        return (
            self._t_handler.t.truncated(t)
            if do_truncate is True else
            self._t_handler.t.rounded(t)
            if do_truncate is False else
            t # if None
        )

        # TODO: Remove this below in the next
        # commit
        pts = (
            self._t_handler.pts.truncated(pts)
            if do_truncate is True else
            self._t_handler.pts.rounded(pts)
            if do_truncate is False else
            pts # if None
        )

        return Fraction(pts * self._t_handler.time_base)
    
    def to_pts(
        self,
        t: Union[int, float, Fraction],
        do_truncate: Union[bool, None] = True
    ) -> int:
        """
        Transform the given 't' to a 'pts' value
        truncating, rounding or applying no 
        variation.

        The formula:
        - `int(t / time_base)`
        """
        return self._t_handler.pts.from_t(t, do_truncate)
    
    def to_index(
        self,
        t: Union[int, float, Fraction],
        do_truncate: Union[bool, None] = True
    ) -> int:
        """
        Transform the given 't' to a index value
        truncating, rounding or applying no
        variation.

        The formula:
        - `int(round(t * fps))`
        """
        t = (
            self.truncated(t)
            if do_truncate is True else
            self.rounded(t)
            if do_truncate is False else
            t
        )

        return frame_t_to_index(t, self.fps)
    
    def from_index(
        self,
        index: int
    ) -> Fraction:
        """
        Transform the given index to a 't' time
        moment value.

        The formula:
        - `frame_index * (1 / fps)`
        """
        return frame_index_to_t(index, self.fps)

    def truncated(
        self,
        t: Union[int, float, Fraction]
    ):
        """
        Get the 't' value provided but truncated.

        This means that if 't' is in a
        [start, end) range, we will obtain the
        'start' value always.
        """
        return round_t(t, Fraction(1, self._t_handler.fps), do_truncate = True)
    
    def rounded(
        self,
        t: Union[int, float, Fraction]
    ):
        """
        Get the 't' value provided but rounded.

        This means that if 't' is in a
        [start, end) range, we will obtain
        the 'start' or the 'end' value according
        to which one is closer to the that 't'
        value provided.
        """
        return round_t(t, Fraction(1, self._t_handler.fps), do_truncate = False)
    
    def next(
        self,
        t: Union[int, float, Fraction],
        n: int = 1,
        do_truncate: bool = True
    ) -> Fraction:
        """
        Get the value that is 'n' times ahead of
        the 't' property of this instance 
        (truncated or rounded according to the
        'do_truncate' parameter provided).

        Useful when you need the next value for a
        range in an iteration or similar.

        The formula:
        - `t + n * (1 / fps)`
        """
        t = (
            self.truncated(t)
            if do_truncate else
            self.rounded(t)
        )

        return t + n * (1 / self._t_handler.fps)
    
    def previous(
        self,
        t: Union[int, float, Fraction],
        n: int = 1,
        do_truncate: bool = True
    ) -> Fraction:
        """
        Get the value that is 'n' times before
        the 't' property of this instance 
        (truncated or rounded according to the
        'do_truncate' parameter provided).

        Useful when you need the previous value to
        check if the current is the next one or
        similar.

        Be careful, if the 'truncated' value is 0
        this will give you an unexpected negative
        value.

        The formula:
        - `t - n * (1 / fps)`
        """
        t = (
            self.truncated(t)
            if do_truncate else
            self.rounded(t)
        )

        return t - n * (1 / self._t_handler.fps)
    
class _Pts:
    """
    Internal class to be used by the THandler
    as a shortcut to the functionality 
    related with 'pts' values.
    """

    def __init__(
        self,
        t_handler: 'THandler'
    ):
        self._t_handler: THandler = t_handler
        """
        Instance of the parent THandler to
        access to its properties.
        """

    def from_t(
        self,
        t: Union[int, float, Fraction],
        do_truncate: Union[bool, None] = True
    ) -> int:
        """
        Get the pts (the amount of accumulated
        ticks, also called presentation timestamp),
        for the frame defined by the 't' time
        moment provided.

        If 't' is in a [start, end) range, we
        will obtain the 'start' value if 't'
        value is closer to it than to the 'end
        value.

        If 'do_truncate' is True, we will
        always receive the 'start' value. If
        None, we will not make any conversion
        and the value received could be useless
        because it is in the middle of a range.

        The formula:
        - `int(t / time_base)`
        """
        t = (
            self._t_handler.t.truncated(t)
            if do_truncate is True else
            self._t_handler.t.rounded(t)
            if do_truncate is False else
            t # if None
        )

        return int(t / self._t_handler.time_base)
    
    def to_t(
        self,
        pts: int,
        do_truncate: Union[bool, None] = True
    ) -> Fraction:
        """
        Transform the given 'pts' to a 't' value
        truncating, rounding or applying no 
        variation.

        The formula:
        - `pts * time_base`
        """
        return self._t_handler.t.from_pts(pts, do_truncate)
    
    def to_index(
        self,
        pts: int,
        do_truncate: Union[bool, None] = True
    ) -> int:
        """
        Transform the given 'pts' to a index value
        truncating, rounding or applying no
        variation.

        The formula:
        - `int(round((pts * time_base) * fps))`
        """
        return self._t_handler.t.to_index(
            self.to_t(pts, do_truncate = None),
            do_truncate = do_truncate
        )
    
    def from_index(
        self,
        index: int
    ) -> Fraction:
        """
        Transform the given index to a 't' time
        moment value.

        The formula:
        - `int((frame_index * (1 / fps)) * time_base)`
        """
        return self.from_t(
            t = self._t_handler.t.from_index(index),
            do_truncate = True
        )
    
    """
    These 2 methods below are here because they
    seem to work for videos, but I think they
    could work not if the video has dynamic frame
    rate or in some other situations, thats why
    this is here as a reminder.

    I found one video that had audio_fps=44100
    and time_base=256/11025, so it was impossible
    to make a conversion using this formula with
    the audio. With video seems to be ok, but...

    Use these methods below at your own risk.
    """

    def truncated(
        self,
        pts: int
    ):
        """
        (!) This is valid only for video and/or 
        could work not properly. Use it at your
        own risk.

        Get the 'pts' value provided but truncated.

        This means that if 't' is in a
        [start, end) range, we will obtain the
        'start' value always.
        """
        return round_pts(
            pts = pts,
            fps = self._t_handler.fps,
            time_base = self._t_handler.time_base,
            do_truncate = True
        )
    
    def rounded(
        self,
        pts: int
    ) -> int:
        """
        (!) This is valid only for video and/or 
        could work not properly. Use it at your
        own risk.

        Get the 'pts' value provided but rounded.

        This means that if 't' is in a
        [start, end) range, we will obtain
        the 'start' or the 'end' value according
        to which one is closer to the that 't'
        value provided.
        """
        return round_pts(
            pts = pts,
            fps = self._t_handler.fps,
            time_base = self._t_handler.time_base,
            do_truncate = False
        )
    
    def next(
        self,
        pts: int,
        n: int = 1,
        do_truncate: bool = True
    ) -> int:
        """
        (!) This is valid only for video and/or 
        could work not properly. Use it at your
        own risk.

        Get the value that is 'n' times ahead of
        the 'pts' value provided (truncated or
        rounded according to the 'do_truncate'
        parameter provided).

        Useful when you need the next value for a
        range in an iteration or similar.

        The formula:
        - `pts + n * ticks_per_frame`
        """
        pts = (
            self.truncated(pts)
            if do_truncate else
            self.rounded(pts)
        )

        return pts + n * get_ticks_per_frame(self._t_handler.fps, self._t_handler.time_base)
    
    def previous(
        self,
        pts: int,
        n: int = 1,
        do_truncate: bool = True
    ) -> int:
        """
        (!) This is valid only for video and/or 
        could work not properly. Use it at your
        own risk.

        Get the value that is 'n' times before
        the 't' property of this instance 
        (truncated or rounded according to the
        'do_truncate' parameter provided).

        Useful when you need the previous value to
        check if the current is the next one or
        similar.

        Be careful, if the 'truncated' value is 0
        this will give you an unexpected negative
        value.

        The formula:
        - `pts - n * ticks_per_frame`
        """
        pts = (
            self.truncated(pts)
            if do_truncate else
            self.rounded(pts)
        )

        return pts - n * get_ticks_per_frame(self._t_handler.fps, self._t_handler.time_base)
    
class THandler:
    """
    Class to simplify the way we work with
    pyav frames time moments, indexes and
    pts values.

    This is an example of what a video has:
    - `fps = 60`
    - `time_base = 1 / 15360`
    - `tick = fps * time_base = 256`

    So, considering this above:
    - Frame #1: `pts[0] = 256 * 0 = 0`
    - Frame #2: `pts[1] = 256 * 1 = 256`
    - Frame #16: `pts[15] = 256 * 15 = 3840`
    """

    def __init__(
        self,
        fps: Union[int, float, Fraction],
        time_base: Union[Fraction, None] = None
    ):
        """
        If the 'time_base' provided is None it will
        be automatically `1/fps`.
        """
        ParameterValidator.validate_mandatory_positive_number('fps', fps, do_include_zero = False)
        ParameterValidator.validate_instance_of('time_base', time_base, 'Fraction')

        self.fps: Fraction = parse_fraction(fps)
        """
        The frames per second.
        """
        self.time_base: Fraction = (
            time_base
            if time_base is not None else
            fps_to_time_base(self.fps)
        )
        """
        The time base.
        """
        self.t: _T = _T(self)
        """
        Shortcut to the instance that handles
        the 't' related functionality.
        """
        self.pts: _Pts = _Pts(self)
        """
        Shortcut to the instance that handles
        the 'pts' related functionality.
        """

# TODO: I think I should create a THandler
# that receives 'fps' and 'time_base' and
# then, by passing a 't' value, we can 
# calculate everything we need, so we
# simplify all these processes
def frame_t_to_index(
    t: Union[float, int, Fraction],
    fps: Union[float, int, Fraction]
) -> int:
    """
    Get the index of the frame with the 
    given 't' time moment, based on the
    also provided 'fps'.

    The formula:
    - `int(round(t * fps))`
    """
    return int(round(t * fps))

def frame_index_to_t(
    index: int,
    fps: Union[float, int, Fraction] 
):
    """
    Get the 't' time moment for the frame
    with the given 'index', based on the
    also provided 'fps'.

    The formula:
    - `frame_index * (1 / fps)`
    """
    return index * parse_fraction(1, parse_fraction(fps))

def frame_t_to_pts(
    t: Union[float, int, Fraction],
    fps: Union[float, int, Fraction],
    time_base: Fraction
):
    """
    Get the pts (the amount of accumulated
    ticks, also called presentation timestamp),
    for the frame defined by the 't' time
    moment provided, based on the also provided
    'fps' and 'time_base'.

    (!) This is valid only for videos.

    The formula:
    - `frame_index * ticks_per_frame`
    """
    return frame_t_to_index(t, fps) * get_ticks_per_frame(fps, time_base)

def frame_pts_to_t(
    pts: int,
    time_base: Fraction 
) -> Fraction:
    """
    Get the 't' time moment of the frame with
    the given 'pts' (the amount of accumulated
    ticks, also called presentation timestamp),
    based on the also provided 'time_base'.

    The formula:
    - `pts * time_base`
    """
    return parse_fraction(pts * time_base)

def get_audio_frame_duration(
    samples: int,
    audio_fps: Fraction
) -> Fraction:
    """
    Get the audio frame duration by giving the
    number of '.samples' and also the rate (that
    we call 'audio_fps').

    This is useful when trying to guess the next
    pts or t.

    The formula:
    - `samples / audio_fps`
    """
    return Fraction(samples / audio_fps)
    
def get_ticks_per_frame(
    fps: Union[float, int, Fraction],
    time_base: Fraction
) -> int:
    """
    Get the amount of ticks per frame. A
    tick is the minimum amount of time we
    spend from one frame to the next.

    (!) This is only valid for video
    apparently.

    The formula:
    - `1 / (fps * time_base)`
    """
    return int(Fraction(1, 1) / (fps * time_base))

def fps_to_frame_duration(
    fps: Union[float, int, Fraction]
) -> Fraction:
    """
    Get the frame duration based on the 'fps'
    provided.

    The formula:
    - `1 / fps`
    """
    return Fraction(1, parse_fraction(fps))

def fps_to_time_base(
    fps: Union[float, int, Fraction]
) -> Fraction:
    """
    Get the time base based on the given 'fps',
    that will be basically `1/fps`. This is a
    bit useless, just when we don't want to
    think too much to use a time base and we
    want to use the fps.

    The formula:
    - `1 / fps`
    """
    return Fraction(1, parse_fraction(fps))
    
def parse_fraction(
    value: Union[float, int, Fraction]
) -> Fraction:
    """
    Parse the provided 'value' as a Fraction
    and limits its denominator.
    """
    fraction = Fraction(value)#.limit_denominator(100_000)

    return fraction
    
