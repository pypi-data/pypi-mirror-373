"""
A video reader using the PyAv (av) library
that, using ffmpeg, detects the video.
"""
from yta_video_opengl.reader.cache.video import VideoFrameCache
from yta_video_opengl.reader.cache.audio import AudioFrameCache
from yta_video_opengl.utils import iterate_stream_frames_demuxing
from yta_video_opengl.t import T
from yta_validation import PythonValidator
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from av.packet import Packet
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from av.container.input import InputContainer
from quicktions import Fraction
from av import open as av_open
from typing import Union
from dataclasses import dataclass


@dataclass
class VideoReaderFrame:
    """
    Class to wrap a frame of a video that is
    being read, that can be a video or audio
    frame, and has been decoded.
    """

    @property
    def is_video(
        self
    ):
        """
        Flag to indicate if the instance is a video
        frame.
        """
        return PythonValidator.is_instance_of(self.value, VideoFrame)
    
    @property
    def is_audio(
        self
    ):
        """
        Flag to indicate if the instance is an audio
        frame.
        """
        return PythonValidator.is_instance_of(self.value, AudioFrame)
    
    @property
    def as_numpy(
        self
    ):
        """
        The frame as a numpy array.
        """
        return self.value.to_ndarray(format = self.pixel_format)
    
    def __init__(
        self,
        # TODO: Add the type, please
        frame: any,
        t: Union[int, float, Fraction] = None,
        pixel_format: str = 'rgb24'
    ):
        self.value: Union[AudioFrame, VideoFrame] = frame
        """
        The frame content, that can be audio or video
        frame.
        """
        self.t: Fraction = Fraction(t)
        """
        The 't' time moment of the frame.
        """
        self.pixel_format: str = pixel_format
        """
        The pixel format of the frame.
        """

@dataclass
class VideoReaderPacket:
    """
    Class to wrap a packet of a video that is
    being read, that can contain video or audio
    frames.
    """

    @property
    def is_video(
        self
    ) -> bool:
        """
        Flag to indicate if the packet includes video
        frames or not.
        """
        return self.value.stream.type == 'video'
    
    @property
    def is_audio(
        self
    ) -> bool:
        """
        Flag to indicate if the packet includes audio
        frames or not.
        """
        return self.value.stream.type == 'audio'

    def __init__(
        self,
        packet: Packet
    ):
        self.value: Packet = packet
        """
        The packet, that can include video or audio
        frames and can be decoded.
        """

    def decode(
        self
    ) -> list['SubtitleSet']:
        """
        Get the frames but decoded, perfect to make
        modifications and encode to save them again.
        """
        return self.value.decode()
        

class VideoReader:
    """
    Class to read video files with the PyAv (av)
    library that uses ffmpeg on the background.
    """

    @property
    def frame_iterator(
        self
    ) -> 'Iterator[VideoFrame]':
        """
        Iterator to iterate over all the video frames
        decodified.
        """
        return self.container.decode(self.video_stream)
    
    # TODO: Remove this when possible, we are not
    # using 'next' properties
    @property
    def next_frame(
        self
    ) -> Union[VideoFrame, None]:
        """
        Get the next video frame (decoded) from the
        iterator.
        """
        return next(self.frame_iterator)

    @property
    def audio_frame_iterator(
        self
    ) -> 'Iterator[AudioFrame]':
        """
        Iterator to iterate over all the audio frames
        decodified.
        """
        return self.container.decode(self.audio_stream)
        
    @property
    def packet_iterator(
        self
    ) -> 'Iterator[Packet]':
        """
        Iterator to iterate over all the video frames
        as packets (not decodified).
        """
        return self.container.demux(self.video_stream)
    
    @property
    def audio_packet_iterator(
        self
    ) -> 'Iterator[Packet]':
        """
        Iterator to iterate over all the audio frames
        as packets (not decodified).
        """
        return self.container.demux(self.audio_stream)
    
    @property
    def packet_with_audio_iterator(
        self
    ) -> 'Iterator[Packet]':
        """
        Iterator to iterate over all the video frames
        as packets (not decodified) including also the
        audio as packets.
        """
        return self.container.demux((self.video_stream, self.audio_stream))

    @property
    def has_video(
        self
    ) -> bool:
        """
        Flag to indicate if there is a video stream
        or not.
        """
        return self.video_stream is not None

    @property
    def has_audio(
        self
    ) -> bool:
        """
        Flag to indicate if there is an audio stream
        or not.
        """
        return self.audio_stream is not None

    @property
    def codec_name(
        self
    ) -> Union[str, None]:
        """
        Get the name of the video codec.
        """
        return (
            self.video_stream.codec_context.name
            if self.has_video else
            None
        )
    
    @property
    def audio_codec_name(
        self
    ) -> str:
        """
        Get the name of the audio codec.
        """
        return (
            self.audio_stream.codec_context.name
            if self.has_audio else
            None
        )

    @property
    def number_of_frames(
        self
    ) -> Union[int, None]:
        """
        The number of frames in the video.
        """
        return (
            self.video_stream.frames
            if self.has_video else
            None
        )
    
    @property
    def number_of_audio_frames(
        self
    ) -> Union[int, None]:
        """
        The number of frames in the audio.
        """
        return (
            self.audio_stream.frames
            if self.has_audio else
            None
        )
    
    @property
    def fps(
        self
    ) -> Union[Fraction, None]:
        """
        The fps of the video.
        """
        return (
            self.video_stream.average_rate
            if self.has_video else
            None
        )
    
    @property
    def audio_fps(
        self
    ) -> Union[int, None]:
        """
        The fps of the audio.
        """
        return (
            self.audio_stream.rate
            if self.has_audio else
            None
        )
    
    @property
    def time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the video.
        """
        return (
            self.video_stream.time_base
            if self.has_video else
            None
        )

    @property
    def audio_time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the audio.
        """
        return (
            self.audio_stream.time_base
            if self.has_audio else
            None
        )
    
    @property
    def duration(
        self
    ) -> Union[float, None]:
        """
        The duration of the video.
        """
        # TODO: What to do in the case we have
        # video stream but not 'duration' 
        # attribute (?)
        return (
            float(self.video_stream.duration * self.video_stream.time_base)
            if (
                self.has_video and
                self.video_stream.duration
            ) else
            None
        )

    @property
    def audio_duration(
        self
    ) -> Union[float, None]:
        """
        The duration of the audio.
        """
        # TODO: What to do in the case we have
        # audio stream but not 'duration' 
        # attribute (?)
        return (
            float(self.audio_stream.duration * self.audio_stream.time_base)
            if (
                self.has_audio and
                self.audio_stream.duration
            ) else
            None
        )
    
    @property
    def size(
        self
    ) -> Union[tuple[int, int], None]:
        """
        The size of the video in a (width, height) format.
        """
        return (
            (
                self.video_stream.width,
                self.video_stream.height
            )
            if self.has_video else
            None
        )
    
    @property
    def width(
        self
    ) -> Union[int, None]:
        """
        The width of the video, in pixels.
        """
        return (
            self.size[0]
            if self.size is not None else
            None
        )
    
    @property
    def height(
        self
    ) -> Union[int, None]:
        """
        The height of the video, in pixels.
        """
        return (
            self.size[1]
            if self.size is not None else
            None
        )
    
    # Any property related to audio has to
    # start with 'audio_property_name'

    def __init__(
        self,
        filename: str,
        # Use 'rgba' if alpha channel
        pixel_format: str = 'rgb24'
    ):
        self.filename: str = filename
        """
        The filename of the video source.
        """
        self.pixel_format: str = pixel_format
        """
        The pixel format.
        """
        self.container: InputContainer = None
        """
        The av input general container of the
        video (that also includes the audio) we
        are reading.
        """
        self.video_stream: Union[VideoStream, None] = None
        """
        The stream that includes the video. If
        no video stream this will be None.
        """
        self.audio_stream: Union[AudioStream, None] = None
        """
        The stream that includes the audio. If
        no audio stream this will be None.
        """
        self.video_cache: VideoFrameCache = None
        """
        The video frame cache system to optimize
        the way we access to the frames.
        """
        self.audio_cache: AudioFrameCache = None
        """
        The audio frame cache system to optimize
        the way we access to the frames.
        """

        # TODO: Maybe we can read the first 
        # frame, store it and reset, so we have
        # it in memory since the first moment.
        # We should do it here because if we
        # iterate in some moment and then we
        # want to obtain it... it will be 
        # difficult.
        # Lets load the variables
        self.reset()

    def reset(
        self
    ) -> 'VideoReader':
        """
        Reset all the instances, closing the file
        and opening again.

        This will also return to the first frame.
        """
        if self.container is not None:
            # TODO: Maybe accept forcing it (?)
            self.container.seek(0)
            #self.container.close()
        else:
            self.container = av_open(self.filename)
            
            self.video_stream = (
                self.container.streams.video[0]
                if self.container.streams.video else
                None
            )
            # TODO: Should this be 'AUTO' (?)
            self.video_stream.thread_type = 'AUTO'

            self.audio_stream = (
                self.container.streams.audio[0]
                if self.container.streams.audio else
                None
            )
            # TODO: Should this be 'AUTO' (?)
            self.audio_stream.thread_type = 'AUTO'

            if (
                self.video_stream is None and
                self.audio_stream is None
            ):
                raise Exception(f'No video nor audio stream found in the "{self.filename}" file.')

            self.video_cache = VideoFrameCache(self.container, self.video_stream)
            self.audio_cache = AudioFrameCache(self.container, self.audio_stream)

    def seek(
        self,
        pts: int,
        stream = None
    ) -> 'VideoReader':
        """
        Call the container '.seek()' method with
        the given 'pts' packet time stamp. By
        default, the video stream is the one in
        which we apply the seek.
        """
        stream = (
            self.video_stream
            if stream is None else
            stream
        )

        # TODO: Is 'offset' actually a 'pts' (?)
        self.container.seek(
            offset = pts,
            stream = stream
        )

        return self

    def iterate(
        self
    ) -> 'Iterator[Union[VideoFrame, AudioFrame]]':
        """
        Iterator to iterate over the video frames
        (already decoded).
        """
        for frame in self.frame_iterator:
            yield VideoReaderFrame(
                frame = frame,
                # TODO: Maybe use util to transform it (?)
                t = frame.pts * self.time_base,
                pixel_format = self.pixel_format
            )

    def iterate_with_audio(
        self,
        do_decode_video: bool = True,
        do_decode_audio: bool = False
    ) -> 'Iterator[Union[VideoReaderFrame, VideoReaderPacket, None]]':
        """
        Iterator to iterate over the video and audio
        packets, decoded only if the parameters are
        set as True.

        If the packet is decoded, it will return each
        frame individually as a VideoReaderFrame 
        instance. If not, the whole packet as a
        VideoReaderPacket instance.
        """
        for packet in self.packet_with_audio_iterator:
            is_video = packet.stream.type == 'video'

            do_decode = (
                (
                    is_video and
                    do_decode_video
                ) or
                (
                    not is_video and
                    do_decode_audio
                )
            )

            if do_decode:
                for frame in packet.decode():
                    # Return each frame decoded
                    yield VideoReaderFrame(frame)
            else:
                # Return the packet as it is
                yield VideoReaderPacket(packet)        

    # These methods below are using the demux
    def iterate_video_frames(
        self,
        start_pts: int = 0,
        end_pts: Union[int, None] = None
    ):
        """
        Iterate over the video stream packets and
        decode only the ones in the expected range,
        so only those frames are decoded (which is
        an expensive process).

        This method returns a tuple of 3 elements:
        - `frame` as a `VideoFrame` instance
        - `t` as the frame time moment
        - `index` as the frame index
        """
        for frame in iterate_stream_frames_demuxing(
            container = self.container,
            video_stream = self.video_stream,
            audio_stream = None,
            start_pts = start_pts,
            end_pts = end_pts
        ):
            yield frame

    def iterate_audio_frames(
        self,
        start_pts: int = 0,
        end_pts: Union[int, None] = None
    ):
        """
        Iterate over the audio stream packets and
        decode only the ones in the expected range,
        so only those frames are decoded (which is
        an expensive process).

        This method returns a tuple of 3 elements:
        - `frame` as a `AudioFrame` instance
        - `t` as the frame time moment
        - `index` as the frame index
        """
        for frame in iterate_stream_frames_demuxing(
            container = self.container,
            video_stream = None,
            audio_stream = self.audio_stream,
            start_pts = start_pts,
            end_pts = end_pts
        ):
            yield frame

    def get_frame(
        self,
        t: Union[int, float, Fraction]
    ) -> VideoFrame:
        """
        Get the video frame that is in the 't' time
        moment provided.
        """
        return self.video_cache.get_frame(t)

    def get_frames(
        self,
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None
    ):
        """
        Iterator to get the video frames in between
        the provided 'start' and 'end' time moments.
        """
        for frame in self.video_cache.get_frames(start, end):
            yield frame

    def get_audio_frame_from_t(
        self,
        t: Union[int, float, Fraction]
    ) -> 'AudioFrame':
        """
        Get the audio frame with the given 't' time
        moment, using the audio cache system.
        """
        return self.audio_cache.get_frame(t)
    
    def get_audio_frames_from_t(
        self,
        t: Union[int, float, Fraction]
    ):
        """
        Get the sequence of audio frames for the 
        given video 't' time moment, using the
        audio cache system.

        This is useful when we want to write a
        video frame with its audio, so we obtain
        all the audio frames associated to it
        (remember that a video frame is associated
        with more than 1 audio frame).
        """
        t: T = T.from_fps(t, self.fps)
        # We want all the audios that must be played
        # during the video frame that starts in the
        # 't' time moment
        for frame in self.get_audio_frames(t.truncated, t.next(1).truncated):
            yield frame

    def get_audio_frames(
        self,
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None
    ):
        """
        Iterator to get the audio frames in between
        the provided 'start' and 'end' time moments.
        """
        for frame in self.audio_cache.get_frames(start, end):
            yield frame
    
    def close(
        self
    ) -> None:
        """
        Close the container to free it.
        """
        self.container.close()


"""
When reading packets directly from the stream
we can receive packets with size=0, but we need
to process them and decode (or yield them). It
is only when we are passing packets to the mux
when we need to ignore teh ones thar are empty
(size=0).

TODO: Do we need to ignore all? By now, ignoring
not is causing exceptions, and ignoring them is
making it work perfectly.
"""