from yta_validation.parameter import ParameterValidator
from av.stream import Stream
from av.packet import Packet
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from av.container.output import OutputContainer
from av import open as av_open
from quicktions import Fraction
from typing import Union


class VideoWriter:
    """
    Class to write video files with the PyAv (av)
    library that uses ffmpeg on the background.
    """

    def __init__(
        self,
        filename: str,
    ):
        self.filename: str = filename
        """
        The filename we want to use to save the video
        file.
        """
        # TODO: What about this 'libx264' (?)
        self.output: OutputContainer = av_open(filename, mode = 'w')
        """
        An OutputContainer to control the writing process.
        """
        self.video_stream: VideoStream = None
        """
        The video stream.
        """
        self.audio_stream: AudioStream = None
        """
        The audio stream.
        """

    def set_video_stream(
        self,
        codec_name: Union[str, None],
        # TODO: Maybe force fps to 'int' (?)
        fps: Union[Fraction, int, float, None],
        size: Union[tuple[int, int], None] = None,
        pixel_format: Union[str, None] = None,
        options: Union[dict[str, str], None] = None
    ) -> 'VideoWriter':
        """
        Set the video stream, that will overwrite any other
        previous video stream set.
        """
        # TODO: They say that pyav accepts fps as
        # Fraction...
        fps = int(fps)

        self.video_stream: VideoStream = self.output.add_stream(
            # TODO: Maybe 'libx264' as default 'codec_name' (?)
            codec_name = codec_name,
            rate = fps,
            options = options
        )

        # We need to force this or it will not work
        self.video_stream.time_base = Fraction(1, fps)

        if size is not None:
            self.video_stream.width = size[0]
            self.video_stream.height = size[1]

        if pixel_format is not None:
            # TODO: Maybe 'yuv420p' as default 'pixel_format' (?)
            self.video_stream.pix_fmt = pixel_format

        return self

    def set_video_stream_from_template(
        self,
        template: Stream
    ) -> 'VideoWriter':
        """
        Set the video stream, that will overwrite any other
        previous video stream set.

        You can pass the video stream as it was
        obtained from the reader.
        """
        self.video_stream: VideoStream = self.output.add_stream_from_template(
            template
        )

        return self

    def set_audio_stream(
        self,
        codec_name: Union[str, None],
        fps: Union[int, float, Fraction] = 44_100.0
        # TODO: Add more if needed
    ) -> 'VideoWriter':
        """
        Set the audio stream, that will overwrite any other
        previous audio stream set.
        """
        # TODO: Check what else we can set
        self.audio_stream: AudioStream = self.output.add_stream(
            codec_name = codec_name,
            rate = int(fps)
        )

        # audio_stream = output.add_stream("aac", rate=48000)  # codec AAC, 48kHz
        # # Configurar stream
        # audio_stream.channels = 2                # número de canales
        # audio_stream.layout = "stereo"           # layout
        # audio_stream.sample_rate = 48000         # sample rate
        # audio_stream.format = "s16"              # formato de las muestras (PCM signed 16-bit)

        # TODO: Add more if needed

        return self

    def set_audio_stream_from_template(
        self,
        template: Stream
    ) -> 'VideoWriter':
        """
        Set the audio stream, that will overwrite any other
        previous audio stream set.

        You can pass the audio stream as it was
        obtained from the reader.
        """
        self.audio_stream: AudioStream = self.output.add_stream(
            codec_name = template.codec_context.name,
            rate = template.codec_context.rate
        )
        self.audio_stream.codec_context.format = template.codec_context.format
        self.audio_stream.codec_context.layout = template.codec_context.layout
        self.audio_stream.time_base = Fraction(1, template.codec_context.rate)

        return self

    def encode_video_frame(
        self,
        frame: Union[VideoFrame, None] = None
    ) -> list[Packet]:
        """
        Get the provided 'frame' but encoded for the
        video stream, or the remaining packets if the
        'frame' parameter given is None.

        The `.encode()` method with a `None` parameter
        will tell the encoder that we will not send
        more frames to encode so the remaining ones can
        be processed, emptying the buffers.
        """
        ParameterValidator.validate_instance_of('frame', frame, VideoFrame)

        return self.video_stream.encode(frame)
    
    def encode_audio_frame(
        self,
        frame: Union[AudioFrame, None] = None
    ) -> list[Packet]:
        """
        Get the provided 'frame' but encoded for the
        audio stream, or the remaining packets if the
        'frame' parameter given is None.

        The `.encode()` method with a `None` parameter
        will tell the encoder that we will not send
        more frames to encode so the remaining ones can
        be processed, emptying the buffers.
        """
        ParameterValidator.validate_instance_of('frame', frame, AudioFrame)

        return self.audio_stream.encode(frame)
    
    def mux(
        self,
        packet: Packet
    ) -> 'VideoWriter':
        """
        Add the provided video or audio 'packet'
        to the mux.

        Packets with a size of 0 will be discarded,
        as they are indicators of the end.
        """
        ParameterValidator.validate_mandatory_instance_of('packet', packet, Packet)

        # We are ignoring empty packets because they
        # are used to indicate the end or things like
        # that, not actual data... But maybe we are 
        # wrong...
        if packet.size > 0:
            try:
                self.output.mux(packet)
            except Exception as e:
                # TODO: What strategy should we adopt with
                # the packets that cannot be handled
                # properly (?)
                print('Invalid packet')
                print(packet)
                pass

        return self
    
        # TODO: This below is to test fails
        if (
            packet.size > 0 and
            # This is a new special case
            packet.dts % 1024 == 0 and
            packet.dts > 0
        ):
            # av.Packet of #0, dts=-2, pts=0; 1225 bytes at 0x1ef2d8e0680>
            # av.Packet of #0, dts=0, pts=2; 110 bytes at 0x1e1feb8c6d0>
            # av.Packet of #0, dts=1, pts=1; 182 bytes at 0x153f6b3b400>
            # are failing
            print(packet)
            print(packet.stream.type)
            self.output.mux(packet)

        return self
    
    def mux_video_frame(
        self,
        frame: Union[VideoFrame, None] = None
    ) -> 'VideoWriter':
        """
        Encode the provided 'frame' and add the
        obtained packets to the multiplexing (mux)
        process.

        If `None` provided, it will obtain the
        remaining packets and add those ones to
        the multiplexing (mux) process.

        Packets with a size of 0 will be discarded,
        as they are indicators of the end.
        """
        ParameterValidator.validate_instance_of('frame', frame, VideoFrame)

        for packet in self.encode_video_frame(frame):
            self.mux(packet)

        return self

    def mux_audio_frame(
        self,
        frame: Union[AudioFrame, None] = None
    ) -> 'VideoWriter':
        """
        Encode the provided 'frame' and add the
        obtained packets to the multiplexing (mux)
        process.

        If `None` provided, it will obtain the
        remaining packets and add those ones to
        the multiplexing (mux) process.

        Packets with a size of 0 will be discarded,
        as they are indicators of the end.
        """
        ParameterValidator.validate_instance_of('frame', frame, AudioFrame)

        for packet in self.encode_audio_frame(frame):
            self.mux(packet)

        return self
        

"""
# TODO: Check 'https://www.youtube.com/watch?v=OlNWCpFdVMA'
# for ffmpeg with mp3 access
"""