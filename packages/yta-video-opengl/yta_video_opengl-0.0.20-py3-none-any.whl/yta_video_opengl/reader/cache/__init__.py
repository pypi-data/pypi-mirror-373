"""
The pyav container stores the information based
on the packets timestamps (called 'pts'). Some
of the packets are considered key_frames because
they include those key frames.

Also, this library uses those key frames to start
decodifying from there to the next one, obtaining
all the frames in between able to be read and
modified.

This cache system will look for the range of 
frames that belong to the key frame related to the
frame we are requesting in the moment, keeping in
memory all those frames to be handled fast. It
will remove the old frames if needed to use only
the 'size' we set when creating it.

A stream can have 'fps = 60' but use another
different time base that make the pts values go 0,
 256, 512... for example. The 'time_base' is the
only accurate way to obtain the pts.

Feel free to move this explanation to other
place, its about the duration.

The stream 'duration' parameter is measured
on ticks, the amount of ticks that the
stream lasts. Here below is an example:

- Duration raw: 529200
- Time base: 1/44100
- Duration (seconds): 12.0
"""
from av.container import InputContainer
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from av.packet import Packet
from yta_validation.parameter import ParameterValidator
from quicktions import Fraction
from collections import OrderedDict
from typing import Union
from abc import abstractmethod, ABC

import numpy as np
import math


class FrameCache(ABC):
    """
    Class to manage the frames cache of a video
    or audio.
    """

    @property
    @abstractmethod
    def fps(
        self
    ) -> Union[int, Fraction, None]:
        """
        The frames per second.
        """
        pass
    
    @property
    def time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the stream.
        """
        return self.stream.time_base

    def __init__(
        self,
        container: InputContainer,
        stream: Union[VideoStream, AudioStream],
        size: Union[int, None] = None
    ):
        ParameterValidator.validate_mandatory_instance_of('container', container, InputContainer)
        ParameterValidator.validate_mandatory_instance_of('stream', stream, [VideoStream, AudioStream])
        ParameterValidator.validate_number_between('size', size, 1, 120)

        self.container: InputContainer = container
        """
        The pyav container.
        """
        self.stream: Union[VideoStream, AudioStream] = stream
        """
        The pyav stream.
        """
        self.cache: OrderedDict = OrderedDict()
        """
        The cache ordered dictionary.
        """
        self.key_frames_pts: list[int] = []
        """
        The list that contains the timestamps of the
        key frame packets, ordered from begining to
        end.
        """
        self.size: int = size
        """
        The size of the cache.
        """

        self._last_packet_accessed: Union[Packet, None] = None
        """
        The last packet that has been accessed
        """

        self._prepare()

    def _prepare(
        self
    ):
        # Index key frames
        for packet in self.container.demux(self.stream):
            if packet.is_keyframe:
                self.key_frames_pts.append(packet.pts)

        # The cache size will be auto-calculated to
        # use the amount of frames of the biggest
        # interval of frames that belongs to a key
        # frame, or a value by default
        # TODO: Careful if this is too big
        # Intervals, but in number of frames
        intervals = np.diff(
            # Intervals of time between keyframes
            np.array(self.key_frames_pts) * self.time_base
        ) * self.fps

        self.size = (
            math.ceil(np.max(intervals))
            if intervals.size > 0 else
            (
                self.size
                if self.size is not None else
                # TODO: Make this a setting (?)
                60
            )
        )
        
        self.container.seek(0)

    def _get_nearest_keyframe_pts(
        self,
        pts: int
    ):
        """
        Get the fps of the keyframe that is the
        nearest to the provided 'pts'. Useful to
        seek and start decoding frames from that
        keyframe.
        """
        return max([
            key_frame_pts
            for key_frame_pts in self.key_frames_pts
            if key_frame_pts <= pts
        ])

    def _store_frame_in_cache(
        self,
        frame: Union[VideoFrame, AudioFrame]
    ) -> Union[VideoFrame, AudioFrame]:
        """
        Store the provided 'frame' in cache if it
        is not on it, removing the first item of
        the cache if full.
        """
        if frame.pts not in self.cache:
            self.cache[frame.pts] = frame

            # Clean cache if full
            if len(self.cache) > self.size:
                self.cache.popitem(last = False)

        return frame
    
    def _seek(
        self,
        pts: int
    ):
        """
        Seek to the given 'pts' This is useful
        when working with 'container.demux' and
        iterating over packets, not when using
        'stream.decode' and getting frames 
        directly.
        """
        self.container.seek(
            offset = pts,
            stream = self.stream
        )

    def clear(
        self
    ) -> 'VideoFrameCache':
        """
        Clear the cache by removing all the items.
        """
        self.cache.clear()

        return self

    def get_frame(
        self,
        t: Union[int, float, Fraction]
    ) -> Union[VideoFrame, AudioFrame]:
        """
        Get the single frame that is in the 't'
        time moment provided.
        """
        for frame in self.get_frames(t):
            return frame
        
    @abstractmethod
    def get_frames(
        self,
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction]
    ):
        pass


"""
There is a way of editing videos being
able to arbitrary access to frames, that
is transforming the source videos to
intra-frame videos. This is a ffmpeg
command that can do it:

- `ffmpeg -i input.mp4 -c:v libx264 -x264opts keyint=1 -preset fast -crf 18 -c:a copy output_intra.mp4`

Once you have the 'output_intra.mp4',
each packet can decodify its frame 
depending not on the previous one, being
able to seek and jump easy.

There are 3 type of video codifications,
the I-frame (intra-coded), in which any
frame can be decoded by itself, P-frame
(predicted), that need one or more 
previous frames to be decoded, and 
B-frame (bidirectional predicted), that
needs previous and future frames.
"""