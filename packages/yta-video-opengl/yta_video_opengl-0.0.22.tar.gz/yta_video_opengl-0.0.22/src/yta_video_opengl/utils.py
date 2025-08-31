from yta_video_opengl.t import fps_to_time_base
from yta_validation import PythonValidator
from av.container import InputContainer
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from av.video.frame import VideoFrame
from quicktions import Fraction
from typing import Union

import av
import numpy as np
import moderngl


def frame_to_texture(
    frame: Union['VideoFrame', 'np.ndarray'],
    context: moderngl.Context,
    numpy_format: str = 'rgb24'
):
    """
    Transform the given 'frame' to an opengl
    texture. The frame can be a VideoFrame
    instance (from pyav library) or a numpy
    array.
    """
    # To numpy RGB inverted for opengl
    frame: np.ndarray = (
        np.flipud(frame.to_ndarray(format = numpy_format))
        if PythonValidator.is_instance_of(frame, 'VideoFrame') else
        np.flipud(frame)
    )

    return context.texture(
        size = (frame.shape[1], frame.shape[0]),
        components = frame.shape[2],
        data = frame.tobytes()
    )

# TODO: I should make different methods to
# obtain a VideoFrame or a numpy array frame
def texture_to_frame(
    texture: moderngl.Texture
) -> 'VideoFrame':
    """
    Transform an opengl texture into a pyav
    VideoFrame instance.
    """
    # RGBA8
    data = texture.read(alignment = 1)
    frame = np.frombuffer(data, dtype = np.uint8).reshape((texture.size[1], texture.size[0], 4))
    # Opengl gives it with the y inverted
    frame = np.flipud(frame)
    # TODO: This can be returned as a numpy frame

    # This is if we need an 'av' VideoFrame (to
    # export through the demuxer, for example)
    frame = av.VideoFrame.from_ndarray(frame, format = 'rgba')
    # TODO: Make this customizable
    frame = frame.reformat(format = 'yuv420p')

    return frame

def get_fullscreen_quad_vao(
    context: moderngl.Context,
    program: moderngl.Program
) -> moderngl.VertexArray:
    """
    Get the vertex array object of a quad, by
    using the vertices, the indexes, the vbo,
    the ibo and the vao content.
    """
    # Quad vertices in NDC (-1..1) with texture
    # coords (0..1)
    """
    The UV coordinates to build the quad we
    will use to represent the frame by 
    applying it as a texture.
    """
    vertices = np.array([
        # pos.x, pos.y, tex.u, tex.v
        -1.0, -1.0, 0.0, 0.0,  # vertex 0 - bottom left
        1.0, -1.0, 1.0, 0.0,  # vertex 1 - bottom right
        -1.0,  1.0, 0.0, 1.0,  # vertex 2 - top left
        1.0,  1.0, 1.0, 1.0,  # vertex 3 - top right
    ], dtype = 'f4')

    """
    The indexes of the vertices (see 'vertices'
    property) to build the 2 opengl triangles
    that will represent the quad we need for
    the frame.
    """
    indices = np.array([
        0, 1, 2,
        2, 1, 3
    ], dtype = 'i4')

    vbo = context.buffer(vertices.tobytes())
    ibo = context.buffer(indices.tobytes())

    vao_content = [
        # 2 floats position, 2 floats texcoords
        (vbo, '2f 2f', 'in_vert', 'in_texcoord'),
    ]

    return context.vertex_array(program, vao_content, ibo)

def iterate_streams_packets(
    container: 'InputContainer',
    video_stream: 'VideoStream',
    audio_stream: 'AudioStream',
    video_start_pts: int = 0,
    video_end_pts: Union[int, None] = None,
    audio_start_pts: int = 0,
    audio_end_pts: Union[int, None] = None
):
    """
    Iterate over the provided 'stream' packets
    and yield the ones in the expected range.
    This is nice when trying to copy a stream
    without modifications.
    """
    # 'video_start_pts' and 'audio_start_pts' must
    # be 0 or a positive tps

    if (
        video_stream is None and
        audio_stream is None
    ):
        raise Exception('No streams provided.')
    
    # We only need to seek on video
    if video_stream is not None:
        container.seek(video_start_pts, stream = video_stream)
    if audio_stream is not None:
        container.seek(audio_start_pts, stream = audio_stream)
    
    stream = [
        stream
        for stream in (video_stream, audio_stream)
        if stream
    ]

    """
    Apparently, if we ignore some packets based
    on the 'pts', we can be ignoring information
    that is needed for the next frames to be 
    decoded, so we need to decode them all...

    If we can find some strategy to seek not for
    the inmediate but some before and read from
    that one to avoid reading all of the packets
    we could save some time, but at what cost? 
    We cannot skip any crucial frame so we need
    to know how many we can skip, and that sounds
    a bit difficult depending on the codec.
    """
    stream_finished: str = ''
    for packet in container.demux(stream):
        if packet.pts is None:
            continue

        # TODO: We cannot skip like this, we need to
        # look for the nearest keyframe to be able 
        # to decode the frames later. Take a look at
        # the VideoFrameCache class and use it.

        # start_pts = (
        #     video_start_pts
        #     if packet.stream.type == 'video' else
        #     audio_start_pts
        # )
        # end_pts = (
        #     video_end_pts
        #     if packet.stream.type == 'video' else
        #     audio_end_pts
        # )

        # if packet.pts < start_pts:
        #     continue

        # if (
        #     end_pts is not None and
        #     packet.pts > end_pts
        # ):
        #     if (
        #         stream_finished != '' and
        #         (
        #             # Finish if only one stream
        #             stream_finished != packet.stream.type or
        #             video_stream is None or
        #             audio_stream is None
        #         )
        #     ):
        #         # We have yielded all the frames in the
        #         # expected range, no more needed
        #         return
            
        #     stream_finished = packet.stream.type
        #     continue
        
        yield packet

def iterate_stream_frames_demuxing(
    container: 'InputContainer',
    video_stream: 'VideoStream',
    audio_stream: 'AudioStream',
    video_start_pts : int = 0,
    video_end_pts: Union[int, None] = None,
    audio_start_pts: int = 0,
    audio_end_pts: Union[int, None] = None
):
    """
    Iterate over the provided 'stream' packets
    and decode only the ones in the expected
    range, so only those frames are decoded
    (which is an expensive process).

    This method returns a tuple of 3 elements:
    - `frame` as a `VideoFrame` instance
    - `t` as the frame time moment
    - `index` as the frame index

    You can easy transform the frame received
    to a numpy array by using this:
    - `frame.to_ndarray(format = format)`
    """
    # 'start_pts' must be 0 or a positive tps
    # 'end_pts' must be None or a positive tps

    # We cannot skip packets or we will lose
    # information needed to build the video
    for packet in iterate_streams_packets(
        container = container,
        video_stream = video_stream,
        audio_stream = audio_stream,
        video_start_pts = video_start_pts,
        video_end_pts = video_end_pts,
        audio_start_pts = audio_start_pts,
        audio_end_pts = audio_end_pts
    ):
        # Only valid and in range packets here
        # Here only the accepted ones
        stream_finished: str = ''
        for frame in packet.decode():
            if frame.pts is None:
                continue

            time_base = (
                video_stream.time_base
                if PythonValidator.is_instance_of(frame, VideoFrame) else
                audio_stream.time_base 
            )

            average_rate = (
                video_stream.average_rate
                if PythonValidator.is_instance_of(frame, VideoFrame) else
                audio_stream.rate
            )

            start_pts = (
                video_start_pts
                if packet.stream.type == 'video' else
                audio_start_pts
            )

            end_pts = (
                video_end_pts
                if packet.stream.type == 'video' else
                audio_end_pts
            )

            if frame.pts < start_pts:
                continue

            if (
                end_pts is not None and
                frame.pts > end_pts
            ):
                if (
                    stream_finished != '' and
                    (
                        # Finish if only one stream
                        stream_finished != packet.stream.type or
                        video_stream is None or
                        audio_stream is None
                    )
                ):
                    # We have yielded all the frames in the
                    # expected range, no more needed
                    return
                
                stream_finished = packet.stream.type
                continue
            
            time_base = (
                video_stream.time_base
                if PythonValidator.is_instance_of(frame, VideoFrame) else
                audio_stream.time_base 
            )

            average_rate = (
                video_stream.average_rate
                if PythonValidator.is_instance_of(frame, VideoFrame) else
                audio_stream.rate
            )

            # TODO: Maybe send a @dataclass instead (?)
            yield (
                frame,
                pts_to_t(frame.pts, time_base),
                pts_to_index(frame.pts, time_base, average_rate)
            )

# TODO: These methods below have to be
# removed because we created the new T
# class that is working with Fractions
# to be precise
def t_to_pts(
    t: Union[int, float, Fraction],
    stream_time_base: Fraction
 ) -> int:
    """
    Transform a 't' time moment (in seconds) to
    a packet timestamp (pts) understandable by
    the pyav library.
    """
    return int((t + 0.000001) / stream_time_base)

def pts_to_index(
    pts: int,
    stream_time_base: Fraction,
    fps: Union[float, Fraction]
) -> int:
    """
    Transform a 'pts' packet timestamp to a 
    frame index.
    """
    return int(round(pts_to_t(pts, stream_time_base) * fps))

def index_to_pts(
    index: int,
    stream_time_base: Fraction,
    fps: Union[float, Fraction]
) -> int:
    """
    Transform a frame index into a 'pts' packet
    timestamp.
    """
    return int(index / fps / stream_time_base)

def pts_to_t(
    pts: int,
    stream_time_base: Fraction
) -> float:
    """
    Transform a 'pts' packet timestamp to a 't'
    time moment.
    """
    return pts * stream_time_base


# TODO: Move this to another utils
def get_silent_audio_frame(
    sample_rate: int,
    layout = 'stereo',
    number_of_samples: int = 1024,
    format = 's16'
):
    # TODO: This could be a utils or something to
    # directly transform format into dtype
    dtype = {
        's16': np.int16,
        'flt': np.float32,
        'fltp': np.float32
    }.get(format, None)

    if dtype is None:
        raise Exception(f'The format "{format}" is not accepted.')

    number_of_channels = len(av.AudioLayout(layout).channels)
    # TODO: I think the option above is better
    # number_of_channels = (
    #     2
    #     if layout == 'stereo' else
    #     1
    # )

    # For packed (or planar) formats we apply:
    # (1, samples * channels). This is the same
    # amount of data but planar, in 1D only
    # TODO: This wasn't in the previous version
    # and it was working, we were sending the
    # same 'number_of_samples' even when 'fltp'
    # that includes the 'p'
    # TODO: This is making the audio last 2x
    # if 'p' in format:
    #     number_of_samples *= number_of_channels

    silent_array = np.zeros((number_of_channels, number_of_samples), dtype = dtype)
    frame = av.AudioFrame.from_ndarray(silent_array, format = format, layout = layout)
    frame.sample_rate = sample_rate
    
    return frame

def get_black_background_video_frame(
    size: tuple[int, int] = (1920, 1080),
    format: str = 'rgb24',
    pts: Union[int, None] = None,
    time_base: Union[Fraction, None] = None
):
    """
    Get a pyav VideoFrame that is a completely black
    frame. If the 'pts' and/or 'time_base' parameters
    are provided, they will be set to the frame that
    is returned with them. If not, remember to set
    later because they are needed to be sent to the
    pyav muxer.
    """
    frame = av.VideoFrame.from_ndarray(
        # TODO: What if we want alpha (?)
        # Size must be inverted
        array = np.zeros((size[1], size[0], 3), dtype = np.uint8),
        format = format
    )

    frame.pts = (
        pts
        if pts is not None else
        frame.pts
    )

    frame.time_base = (
        time_base
        if time_base is not None else
        frame.time_base
    )

    return frame

def get_audio_frame_pts_range(
    frame: av.AudioFrame,
    do_in_seconds: bool = False
):
    """
    Get the [start_pts, end_pts) range of the
    pyav AudioFrame, or in seconds if the
    'do_in_seconds' parameter is True.
    """
    if frame.pts is None:
        raise Exception('No "pts" found.')

    # First and last sample. Remember that
    # the last one is not included
    start_pts = frame.pts
    end_pts = frame.pts + frame.samples

    # Time base for the seconds conversion
    time_base = (
        frame.time_base
        if frame.time_base else
        Fraction(1, frame.sample_rate)
    )

    start_time = (
        float(start_pts * time_base)
        if do_in_seconds else
        start_time
    )
    end_time = (
        float(end_pts * time_base)
        if do_in_seconds else
        end_time
    )

    return (
        start_time,
        end_time
    )

def audio_frames_and_remainder_per_video_frame(
    # TODO: Maybe force 'fps' as int (?)
    video_fps: Union[float, Fraction],
    sample_rate: int, # audio_fps
    number_of_samples_per_audio_frame: int
) -> tuple[int, int]:
    """
    Get how many full silent audio frames we
    need and the remainder for the last one
    (that could be not complete), according
    to the parameters provided.

    This method returns a tuple containing
    the number of full silent audio frames
    we need and the number of samples we need
    in the last non-full audio frame.
    """
    # Video frame duration (in seconds)
    time_base = fps_to_time_base(video_fps)
    sample_rate = Fraction(int(sample_rate), 1)

    # Example:
    # 44_100 / 60 = 735  ->  This means that we
    # will have 735 samples of sound per each
    # video frame
    # The amount of samples per frame is actually
    # the amount of samples we need, because we
    # are generating it...
    samples_per_frame = sample_rate * time_base
    # The 'nb_samples' is the amount of samples
    # we are including on each audio frame
    full_audio_frames_needed = samples_per_frame // number_of_samples_per_audio_frame
    remainder = samples_per_frame % number_of_samples_per_audio_frame
    
    return int(full_audio_frames_needed), int(remainder)