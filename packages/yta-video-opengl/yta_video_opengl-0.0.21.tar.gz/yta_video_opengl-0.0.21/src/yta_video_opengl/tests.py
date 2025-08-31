"""
Manual tests that are working and are interesting
to learn about the code, refactor and build
classes.
"""
"""
Interesting information:
| Abrev.  | Nombre completo            | Uso principal                          |
| ------- | -------------------------- | -------------------------------------- |
| VAO     | Vertex Array Object        | Esquema de datos de vértices           |
| VBO     | Vertex Buffer Object       | Datos crudos de vértices en GPU        |
| FBO     | Frame Buffer Object        | Renderizar fuera de pantalla           |
| UBO     | Uniform Buffer Object      | Variables `uniform` compartidas        |
| EBO/IBO | Element / Index Buffer Obj | Índices para reutilizar vértices       |
| PBO     | Pixel Buffer Object        | Transferencia rápida de imágenes       |
| RBO     | Render Buffer Object       | Almacén intermedio (profundidad, etc.) |

"""
from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator
from yta_video_opengl.reader import VideoReader
from yta_video_opengl.writer import VideoWriter
from yta_timer import Timer
from yta_video_frame_time import T
from abc import abstractmethod
from typing import Union

import av
import moderngl
import numpy as np


class OpenglVertexShader:
    """
    The vertex shader, for opengl renders.
    """

    def __init__(
        self,
        context: moderngl.Context,
        code: str
    ):
        self.context: moderngl.Context = context
        """
        The context of the vertex.
        """
        self.code: str = code
        """
        The code that builts the vertex shader.
        """

class OpenglFragmentShader:
    """
    The fragment shader, for opengl renders.
    """

    def __init__(
        self,
        context: moderngl.Context,
        code: str
    ):
        self.context: moderngl.Context = context
        """
        The context of the vertex.
        """
        self.code: str = code
        """
        The code that builts the vertex shader.
        """

class OpenglProgram:
    """
    The program, for opengl renders.
    """

    @property
    def program(
        self
    ) -> moderngl.Program:
        """
        The opengl program to load variables and use to
        modify the frams.
        """
        if not hasattr(self, '_program'):
            self._program = self.context.program(
                vertex_shader = self.vertex_shader,
                fragment_shader = self.fragment_shader
            )

        return self._program
    
    @property
    def vbo(
        self
    ) -> moderngl.Buffer:
        """
        The vertex buffer object.

        Block of memory in the GPU in which we
        store the information about the vertices
        (positions, colors, texture coordinates,
        etc.). The VAO points to one or more VBOs
        to obtain the information.
        """
        if not hasattr(self, '_vbo'):
            self._vbo = self.create_vbo(self.vertices)

        return self._vbo

    @property
    def vao(
        self
    ):
        """
        The vertex array object.

        Store the state of how the vertices
        information is organized.
        """
        if not hasattr(self, '_vao'):
            self._vao = self.create_vao(self.vbo)

        return self._vao
    
    def __init__(
        self,
        context: moderngl.Context,
        vertex_shader: OpenglVertexShader,
        fragment_shader: OpenglFragmentShader,
        vertices: 'np.ndarray'
    ):
        self.context: moderngl.Context = context
        """
        The opengl context.
        """
        self.vertex_shader: OpenglVertexShader = vertex_shader
        """
        The vertex shader.
        """
        self.fragment_shader: OpenglFragmentShader = fragment_shader
        """
        The fragment shader.
        """
        """
        TODO: A program will include the context, one
        vertex shader, one fragment shader and one or
        more vertices. So, this need to be refactor to
        accept more than one vertices, and also to
        provide one vbo for each vertices item.
        """
        self.vertices: Union[list['np.ndarray'], 'np.ndarray'] = vertices
        """
        The vertices we need to use.
        """

    def set_value(
        self,
        name: str,
        value: any
    ) -> 'OpenglProgram':
        """
        Set the provided 'value' as the value of the
        program property (uniform) with the name given
        as 'name' parameter.
        """
        self.program[name].value = value

        return self

    def create_vao(
        self,
        vbo: moderngl.Buffer
    ) -> moderngl.VertexArray:
        """
        Create a vertex array with the given 'vbo'
        (vertex array object) parameter.
        """
        ParameterValidator.validate_mandatory_instance_of('vbo', vbo, moderngl.Buffer)

        return self.context.vertex_array(self.program, vbo, 'in_pos', 'in_uv')
    
    def create_vbo(
        self,
        vertices: np.ndarray
    ) -> moderngl.Buffer:
        """
        Create a buffer with the given 'vertices'
        parameter.
        """
        ParameterValidator.validate_mandatory_numpy_array('vertices', vertices)

        return self.context.buffer(vertices.tobytes())
    
class OpenglContext:
    """
    Class to wrap an opengl context to handle
    it properly and modify videos.

    TODO: This is ready to apply only one 
    change per context because the shaders are
    limited to one.
    """

    def __init__(
        self,
        vertex_shader: OpenglVertexShader,
        fragment_shader: OpenglFragmentShader,
        vertices: 'np.ndarray'
    ):
        self.context: moderngl.Context = moderngl.create_standalone_context()
        """
        The headless context.
        """
        self.program: OpenglProgram = OpenglProgram(
            context = self.context,
            vertex_shader = vertex_shader,
            fragment_shader = fragment_shader,
            vertices = vertices
        )
        """
        The program custom class instance that is
        able to use the vao, vbo, etc.
        """

    def fbo(
        self,
        frame_size: tuple[int, int]
    ) -> moderngl.Framebuffer:
        """
        Get a frame buffer object (fbo) for the
        given 'frame_size'.

        A frame buffero bject is a virtual screen
        in which you can render out of the screen
        to lately do this:
        - Save as a texture
        - Apply post-processing methods
        - Store to a file
        """
        return self.context.simple_framebuffer(frame_size)

from dataclasses import dataclass
from abc import ABC
@dataclass
class OpenglEffectProgram(ABC):
    """
    The abstract class to be inherited by any
    of our opengl frame effect methods, that
    are actually programs.
    """

    @property
    @abstractmethod
    def vertex_shader(
        self
    ) -> str:
        pass

    @property
    @abstractmethod
    def fragment_shader(
        self
    ) -> str:
        pass

    @property
    @abstractmethod
    def vertices(
        self
    ) -> 'np.ndarray':
        pass

    def __init__(
        self
    ):
        pass

@dataclass
class WavingEffectProgram(OpenglEffectProgram):

    # TODO: I think this has to be a different
    # thing...
    @property
    def vertex_shader(
        self
    ) -> str:
        return (
            '''
            #version 330
            in vec2 in_pos;
            in vec2 in_uv;
            out vec2 v_uv;
            void main() {
                v_uv = in_uv;
                gl_Position = vec4(in_pos, 0.0, 1.0);
            }
            '''
        )
    
    @property
    def fragment_shader(
        self
    ) -> str:
        return (
            '''
            #version 330
            uniform sampler2D tex;
            uniform float time;
            uniform float amp;
            uniform float freq;
            uniform float speed;
            in vec2 v_uv;
            out vec4 f_color;
            void main() {
                float wave = sin(v_uv.x * freq + time * speed) * amp;
                vec2 uv = vec2(v_uv.x, v_uv.y + wave);
                f_color = texture(tex, uv);
            }
            '''
        )
    
    @property
    def vertices(
        self
    ) -> 'np.ndarray':
        # TODO: This should be an array of them because
        # we can have more than one, but by now I leave
        # it being only one
        return np.array([
            -1, -1, 0.0, 0.0,
            1, -1, 1.0, 0.0,
            -1,  1, 0.0, 1.0,
            1,  1, 1.0, 1.0,
        ], dtype = 'f4')

NUMPY_FORMAT = 'rgb24'

# TODO: Maybe rename as ContextHandler (?)
class VideoProcessor:
    """
    Class to read a video, process it (maybe
    applying some effects) and writing the 
    results in a new video.
    """

    @property
    def fbo(
        self
    ) -> moderngl.Framebuffer:
        """
        The frame buffer object for the video frame
        size.
        """
        if not hasattr(self, '_fbo'):
            self._fbo = self.context.fbo(self.reader.size)

        return self._fbo
    
    @property
    def vao(
        self
    ) -> moderngl.VertexArray:
        """
        Shortcut to the program vao.
        """
        return self.program.vao

    @property
    def first_frame(
        self
    ) -> Union['VideoFrame', None]:
        """
        The first frame of the video as a VideoFrame.
        """
        if not hasattr(self, '_first_frame'):
            # Framebuffer to render
            self.fbo.use()
            self._first_frame = self.reader.next_frame
            # Reset the reader
            self.reader.reset()

        return self._first_frame
    
    @property
    def first_frame_as_texture(
        self
    ) -> moderngl.Texture:
        """
        The first frame of the video as a texture.
        This is needed to start the process.
        """
        if not hasattr(self, '_first_frame_as_texture'):
            self._first_frame_as_texture = self.frame_to_texture(self.first_frame, NUMPY_FORMAT)
            self._first_frame_as_texture.build_mipmaps()

        return self._first_frame_as_texture
    
    @property
    def program(
        self
    ) -> OpenglProgram:
        """
        Shortcut to the context program custom class
        instance.
        """
        return self.context.program

    def __init__(
        self,
        filename: str,
        output_filename: str
    ):
        self.filename: str = filename
        """
        The filename of the video we want to read and
        process.
        """
        self.output_filename: str = output_filename
        """
        The filename of the video we want to generate
        and store once the original one has been
        processed.
        """
        # TODO: Hardcoded by now
        effect = WavingEffectProgram()
        self.context: OpenglContext = OpenglContext(
            vertex_shader = effect.vertex_shader,
            fragment_shader = effect.fragment_shader,
            vertices = effect.vertices
        )
        """
        The headless context as a custom class instance.
        """
        self.reader: VideoReader = VideoReader(self.filename)
        """
        The video reader instance.
        """
        # TODO: This has to be dynamic, but
        # according to what (?)
        
        # TODO: Where do we obtain this from (?)
        VIDEO_CODEC_NAME = 'libx264'
        # TODO: Where do we obtain this from (?)
        PIXEL_FORMAT = 'yuv420p'
        self.writer: VideoWriter = (
            VideoWriter(output_filename)
            .set_video_stream(VIDEO_CODEC_NAME, self.reader.fps, self.reader.size, PIXEL_FORMAT)
            .set_audio_stream_from_template(self.reader.audio_stream)
        )
        """
        The video writer instance.
        """

    # TODO: This should be a utils
    def frame_to_texture(
        self,
        frame: 'VideoFrame',
        numpy_format: str = 'rgb24'
    ):
        """
        Transform the given 'frame' to an opengl
        texture.
        """
        # To numpy RGB inverted for OpenGL
        # TODO: Maybe we can receive normal frames
        # here, as np.ndarray, from other libraries
        frame: np.ndarray = np.flipud(frame.to_ndarray(format = numpy_format))

        return self.context.context.texture((frame.shape[1], frame.shape[0]), 3, frame.tobytes())

    def process(
        self
    ):
        """
        Process the video and generate the new one.

        TODO: Should I pass some effects to apply (?)
        """
        # [ 1 ] Initialize fbo and texture mipmaps
        self.first_frame_as_texture # This forces it in the code

        # [ 2 ] Set general program uniforms
        AMP = 0.05
        FREQ = 10.0
        SPEED = 2.0
        (
            self.context.program
            .set_value('amp', AMP)
            .set_value('freq', FREQ)
            .set_value('speed', SPEED)
        )

        # [ 3 ] Process the frames
        frame_index = 0
        for frame_or_packet in self.reader.iterate_with_audio(
            do_decode_video = True,
            do_decode_audio = False
        ):
            # This below is because of the parameters we
            # passed to the method
            is_video_frame = PythonValidator.is_instance_of(frame_or_packet, 'VideoReaderFrame')
            is_audio_packet = PythonValidator.is_instance_of(frame_or_packet, 'VideoReaderPacket')

            # To simplify the process
            if frame_or_packet is not None:
                frame_or_packet = frame_or_packet.data
            if is_audio_packet:
                self.writer.mux(frame_or_packet)
            elif is_video_frame:
                with Timer(is_silent_as_context = True) as timer:
                    # Check this link:
                    # https://stackoverflow.com/a/63153755

                    def process_frame(
                        frame: 'VideoFrame'
                    ):
                        # [ 4 ] Add specific program uniforms
                        self.program.set_value('time', T.video_frame_index_to_video_frame_time(frame_index, float(self.reader.fps)))
                        
                        # Create texture
                        texture = self.frame_to_texture(frame)
                        texture.use()

                        # Activate frame buffer
                        self.fbo.use()

                        # Render, captured by the fbo
                        self.vao.render(moderngl.TRIANGLE_STRIP)

                        # Processed GPU result (from fbo) to numpy
                        processed_data = np.frombuffer(
                            self.fbo.read(components = 3, alignment = 1), dtype = np.uint8
                        )

                        # Invert numpy to normal frame
                        processed_data = np.flipud(
                            processed_data.reshape((texture.size[1], texture.size[0], 3))
                        )

                        # To VideoFrame and to buffer
                        frame = av.VideoFrame.from_ndarray(processed_data, format = NUMPY_FORMAT)
                        # TODO: What is this for (?)
                        #out_frame.pict_type = 'NONE'

                        return frame

                    self.writer.mux_video_frame(process_frame(frame_or_packet))

                print(f'Frame {str(frame_index)}: {timer.time_elapsed_str}s')
                frame_index += 1

        # While this code can be finished, the work in
        # the muxer could be not finished and have some
        # packets waiting to be written. Here we tell
        # the muxer to process all those packets.
        self.writer.mux_video_frame(None)

        # TODO: Maybe move this to the '__del__' (?)
        self.writer.output.close()
        self.reader.container.close()
        print(f'Saved as "{self.output_filename}".')

def video_modified_stored():
    # This path below was trimmed in an online platform
    # and seems to be bad codified and generates error
    # when processing it, but it is readable in the
    # file explorer...
    #VIDEO_PATH = 'test_files/test_1_short_broken.mp4'
    # This is short but is working well
    VIDEO_PATH = "test_files/test_1_short_2.mp4"
    # Long version below, comment to test faster
    #VIDEO_PATH = "test_files/test_1.mp4"
    OUTPUT_PATH = "test_files/output.mp4"
    # TODO: This has to be dynamic, but
    # according to what (?)
    NUMPY_FORMAT = 'rgb24'
    # TODO: Where do we obtain this from (?)
    VIDEO_CODEC_NAME = 'libx264'
    # TODO: Where do we obtain this from (?)
    PIXEL_FORMAT = 'yuv420p'

    from yta_video_opengl.classes import WavingFrame, BreathingFrame, HandheldFrame, OrbitingFrame, RotatingInCenterFrame, StrangeTvFrame, GlitchRgbFrame, WavingNode
    from yta_video_opengl.utils import texture_to_frame, frame_to_texture
    from yta_video_opengl.video import Video
    from yta_video_opengl.complete.timeline import Timeline

    # TODO: This test below is just to validate
    # that it is cropping and placing correctly
    # but the videos are only in one track
    # video = Video(VIDEO_PATH, 0.25, 0.75)
    # timeline = Timeline()
    # timeline.add_video(Video(VIDEO_PATH, 0.25, 1.0), 0.5)
    # # This is successfully raising an exception
    # #timeline.add_video(Video(VIDEO_PATH, 0.25, 0.75), 0.6)
    # timeline.add_video(Video(VIDEO_PATH, 0.25, 0.75), 1.75)
    # timeline.add_video(Video('C:/Users/dania/Downloads/Y2meta.app-TOP 12 SIMPLE LIQUID TRANSITION _ GREEN SCREEN TRANSITION PACK-(1080p60).mp4', 4.0, 5.0), 3)
    # # timeline.add_video(Video('C:/Users/dania/Downloads/Y2meta.app-10 Smooth Transitions Green Screen Template For Kinemaster, Alight Motion, Filmora, premiere pro-(1080p).mp4', 2.25, 3.0), 3)
    # timeline.render(OUTPUT_PATH)

    # # Testing concatenating
    # timeline = Timeline()
    # # When you concat like this, some of the
    # # videos have frames that cannot be accessed
    # # and I don't know why...
    # timeline.add_video(Video('test_files/glitch_rgb_frame.mp4'))
    # timeline.add_video(Video('test_files/output.mp4'))
    # timeline.add_video(Video('test_files/output_render.mp4'))
    # timeline.add_video(Video('test_files/strange_tv_frame.mp4'))
    # timeline.add_video(Video('test_files/test_1.mp4'))
    # timeline.add_video(Video('test_files/test_1_short_2.mp4'))
    # timeline.add_video(Video('test_files/test_audio_1st_track_solo_v0_0_15.mp4'))
    # timeline.add_video(Video('test_files/test_audio_2nd_track_solo_v0_0_15.mp4'))
    # timeline.add_video(Video('test_files/test_audio_combined_tracks_v0_0_015.mp4'))
    # timeline.add_video(Video('test_files/test_audio_combined_v0_0_15.mp4'))
    # timeline.add_video(Video('test_files/test_blend_add_v0_0_16.mp4'))
    # timeline.add_video(Video('test_files/test_blend_difference_v0_0_16.mp4'))
    # timeline.add_video(Video('test_files/test_blend_multiply_v0_0_16.mp4'))
    # timeline.add_video(Video('test_files/test_blend_overlay_v0_0_16.mp4'))
    # timeline.add_video(Video('test_files/test_blend_screen_v0_0_16.mp4'))
    # timeline.add_video(Video('test_files/test_combine_skipping_empty_using_priority_v0_0_18.mp4'))
    # timeline.add_video(Video('test_files/test_ok_v0_0_13.mp4'))

    # timeline.render('test_files/concatenated.mp4')


    # return

    # TODO: This test will add videos that
    # must be played at the same time
    video = Video(VIDEO_PATH, 0.25, 0.75)
    timeline = Timeline()

    transitions_30fps = 'C:/Users/dania/Downloads/Y2meta.app-10 Smooth Transitions Green Screen Template For Kinemaster, Alight Motion, Filmora, premiere pro-(1080p).mp4'
    simpsons_60fps = 'C:/Users/dania/Downloads/Y_una_porra_los_simpsons_castellano_60fps.mp4'

    # Track 1
    timeline.add_video(Video(VIDEO_PATH, 0.25, 1.0), 0.75, track_index = 0)
    timeline.add_video(Video(simpsons_60fps, 1.5, 2.0), 3.0, track_index = 0)
    timeline.add_video(Video(VIDEO_PATH, 0.5, 1.0), 2.0, track_index = 0)

    #timeline.tracks[0].mute()

    # Track 2
    timeline.add_video(Video(VIDEO_PATH, 0.5, 1.0), 2.7, track_index = 1)
    timeline.add_video(Video(simpsons_60fps, 5.8, 7.8), 0.6, track_index = 1)
    # 30fps
    # timeline.add_video(Video('C:/Users/dania/Downloads/Y2meta.app-TOP 12 SIMPLE LIQUID TRANSITION _ GREEN SCREEN TRANSITION PACK-(1080p60).mp4', 0.25, 1.5), 0.25, do_use_second_track = True)
    # 29.97fps
    # timeline.add_video(Video('C:/Users/dania/Downloads/Y_una_porra_los_simpsons_castellano.mp4', 5.8, 6.8), 3.6, do_use_second_track = True)
    
    timeline.render(OUTPUT_PATH)

    return

    Video(VIDEO_PATH, 0.25, 0.75).save_as(OUTPUT_PATH)

    return

    video = VideoReader(VIDEO_PATH)
    video_writer = (
        VideoWriter(OUTPUT_PATH)
        #.set_video_stream(VIDEO_CODEC_NAME, video.fps, video.size, PIXEL_FORMAT)
        .set_video_stream_from_template(video.video_stream)
        .set_audio_stream_from_template(video.audio_stream)
    )
    
    #effect = WavingFrame(size = video.size)
    #effect = BreathingFrame(size = video.size)
    #effect = HandheldFrame(size = video.size)
    # effect = OrbitingFrame(
    #     size = video.size,
    #     first_frame = video.next_frame
    # )
    # effect = RotatingInCenterFrame(
    #     size = video.size,
    #     first_frame = video.next_frame
    # )
    effect = GlitchRgbFrame(
        size = video.size,
        first_frame = video.next_frame
    )
    context = moderngl.create_context(standalone = True)
    
    # New way, with nodes
    node = WavingNode(context, video.size, amplitude = 0.2, frequency = 9, speed = 3)
    # We need to reset it to being again pointing
    # to the first frame...
    # TODO: Improve this by, maybe, storing the first
    # frame in memory so we can append it later, or
    # using the '.seek(0)' even when it could be not
    # accurate
    video.reset()

    frame_index = 0
    for frame_or_packet in video.iterate_with_audio(
        do_decode_video = True,
        do_decode_audio = False
    ):
        # This below is because of the parameters we
        # passed to the method
        is_video_frame = PythonValidator.is_instance_of(frame_or_packet, 'VideoReaderFrame')
        is_audio_packet = PythonValidator.is_instance_of(frame_or_packet, 'VideoReaderPacket')

        # To simplify the process
        if frame_or_packet is not None:
            frame_or_packet = frame_or_packet.value

        if is_audio_packet:
            video_writer.mux(frame_or_packet)
        elif is_video_frame:
            with Timer(is_silent_as_context = True) as timer:
                t = T.video_frame_index_to_video_frame_time(frame_index, float(video.fps))
                # This is another way of getting 't'
                #t = float(frame_or_packet.pts * video.time_base)
                
                video_writer.mux_video_frame(
                    frame = texture_to_frame(
                        texture = node.process(
                            input = frame_or_packet,
                            t = t
                        )
                    )
                )
                
                # video_writer.mux_video_frame(
                #     effect.process_frame(
                #         frame = frame_or_packet,
                #         t = t,
                #         numpy_format = NUMPY_FORMAT
                #     )
                # )

                frame_index += 1

            print(f'Frame {str(frame_index)}: {timer.time_elapsed_str}s')

    video_writer.mux_video_frame(None)

    # TODO: Maybe move this to the '__del__' (?)
    video_writer.output.close()
    video.container.close()
    print(f'Saved as "{OUTPUT_PATH}".')

    return

    # # TODO: By now this is applying an effect
    # # by default
    # VideoProcessor(
    #     filename = VIDEO_PATH,
    #     output_filename = OUTPUT_PATH
    # ).process()

    # return

    
    AMP = 0.05
    FREQ = 10.0
    SPEED = 2.0

    # Get the information about the video
    video = VideoReader(VIDEO_PATH)

    # ModernGL context without window
    context = moderngl.create_standalone_context()

    waving_frame_effect = WavingFrame(
        context = context,
        frame_size = video.size
    )

    vao = waving_frame_effect.vao

    # TODO: This has to be dynamic, but
    # according to what (?)
    NUMPY_FORMAT = 'rgb24'
    # TODO: Where do we obtain this from (?)
    VIDEO_CODEC_NAME = 'libx264'
    # TODO: Where do we obtain this from (?)
    PIXEL_FORMAT = 'yuv420p'

    # Framebuffer to render
    fbo = waving_frame_effect.fbo
    fbo.use()

    # Decode first frame and use as texture
    first_frame = video.next_frame
    # We need to reset it to being again pointing
    # to the first frame...
    # TODO: Improve this by, maybe, storing the first
    # frame in memory so we can append it later, or
    # using the '.seek(0)' even when it could be not
    # accurate
    video = VideoReader(VIDEO_PATH)

    # Most of OpenGL textures expect origin in lower
    # left corner
    # TODO: What if alpha (?)
    # TODO: Move this to the OpenglFrameEffect maybe (?)
    
    texture: moderngl.Texture = frame_to_texture(first_frame, waving_frame_effect.context)
    texture.build_mipmaps()

    # These properties can be set before 
    # iterating the frames or maybe for 
    # each iteration... depending on the
    # effect.
    # Uniforms (properties)
    (
        waving_frame_effect
        .set_value('amp', AMP)
        .set_value('freq', FREQ)
        .set_value('speed', SPEED)
    )

    # Writer with H.264 codec
    video_writer = (
        VideoWriter(OUTPUT_PATH)
        .set_video_stream(VIDEO_CODEC_NAME, video.fps, video.size, PIXEL_FORMAT)
        .set_audio_stream_from_template(video.audio_stream)
    )

    frame_index = 0
    for frame_or_packet in video.iterate_with_audio(
        do_decode_video = True,
        do_decode_audio = False
    ):
        # This below is because of the parameters we
        # passed to the method
        is_video_frame = PythonValidator.is_instance_of(frame_or_packet, 'VideoReaderFrame')
        is_audio_packet = PythonValidator.is_instance_of(frame_or_packet, 'VideoReaderPacket')

        # To simplify the process
        if frame_or_packet is not None:
            frame_or_packet = frame_or_packet.data

        if is_audio_packet:
            video_writer.mux(frame_or_packet)
        elif is_video_frame:
            with Timer(is_silent_as_context = True) as timer:

                def process_frame(
                    frame: 'VideoFrame'
                ):
                    # Add some variables if we need, for the
                    # opengl change we are applying (check the
                    # program code)
                    waving_frame_effect.set_value('time', T.video_frame_index_to_video_frame_time(frame_index, float(video.fps)))
                    
                    # Create texture
                    texture = frame_to_texture(frame, waving_frame_effect.context)
                    texture.use()

                    # Render with shader to frame buffer
                    fbo.use()
                    vao.render(moderngl.TRIANGLE_STRIP)

                    # Processed GPU result to numpy
                    processed_data = np.frombuffer(
                        fbo.read(components = 3, alignment = 1), dtype = np.uint8
                    )

                    # Invert numpy to normal frame
                    # TODO: Can I use the texture.size to fill
                    # these 'img_array.shape[0]' (?)
                    processed_data = np.flipud(
                        processed_data.reshape((texture.size[1], texture.size[0], 3))
                    )

                    # To VideoFrame and to buffer
                    frame = av.VideoFrame.from_ndarray(processed_data, format = NUMPY_FORMAT)
                    # TODO: What is this for (?)
                    #out_frame.pict_type = 'NONE'
                    return frame

                video_writer.mux_video_frame(process_frame(frame_or_packet))

            print(f'Frame {str(frame_index)}: {timer.time_elapsed_str}s')
            frame_index += 1

    # While this code can be finished, the work in
    # the muxer could be not finished and have some
    # packets waiting to be written. Here we tell
    # the muxer to process all those packets.
    video_writer.mux_video_frame(None)

    # TODO: Maybe move this to the '__del__' (?)
    video_writer.output.close()
    video.container.close()
    print(f'Saved as "{OUTPUT_PATH}".')