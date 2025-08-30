"""
TODO: Please, rename, refactor and move.

Opengl doesn't know how to draw a quad
or any other complex shape. The basics
that opengl can handle are triangles, 
so we use different triangles to build
our shapes (quad normally).
"""
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from yta_video_opengl.utils import frame_to_texture, get_fullscreen_quad_vao
from abc import ABC, abstractmethod
from typing import Union

import av
import moderngl
import numpy as np


class _Uniforms:
    """
    Class to wrap the functionality related to
    handling the opengl program uniforms.
    """

    @property
    def uniforms(
        self
    ) -> dict:
        """
        The uniforms in the program, as a dict, in
        the format `{key, value}`.
        """
        return {
            key: self.program[key].value
            for key in self.program
            if PythonValidator.is_instance_of(self.program[key], moderngl.Uniform)
        }

    def __init__(
        self,
        program: moderngl.Program
    ):
        self.program: moderngl.Program = program
        """
        The program instance this handler class
        belongs to.
        """

    def get(
        self,
        name: str
    ) -> Union[any, None]:
        """
        Get the value of the uniform with the
        given 'name'.
        """
        return self.uniforms.get(name, None)

    # TODO: I need to refactor these method to
    # accept a **kwargs maybe, or to auto-detect
    # the type and add the uniform as it must be
    # done
    def set(
        self,
        name: str,
        value
    ) -> '_Uniforms':
        """
        Set the provided 'value' to the normal type
        uniform with the given 'name'. Here you have
        some examples of defined uniforms we can set
        with this method:
        - `uniform float name;`

        TODO: Add more examples
        """
        if name in self.program:
            self.program[name].value = value

        return self
    
    def set_vec(
        self,
        name: str,
        values
    ) -> '_Uniforms':
        """
        Set the provided 'value' to the normal type
        uniform with the given 'name'. Here you have
        some examples of defined uniforms we can set
        with this method:
        - `uniform vec2 name;`

        TODO: Is this example ok? I didn't use it yet
        """
        if name in self.program:
            self.program[name].write(np.array(values, dtype = 'f4').tobytes())

        return self

    def set_mat(
        self,
        name: str,
        value
    ) -> '_Uniforms':
        """
        Set the provided 'value' to a `matN` type
        uniform with the given 'name'. The 'value'
        must be a NxN matrix (maybe numpy array)
        transformed to bytes ('.tobytes()').
        
        This uniform must be defined in the vertex
        like this:
        - `uniform matN name;`

        TODO: Maybe we can accept a NxN numpy 
        array and do the .tobytes() by ourselves...
        """
        if name in self.program:
            self.program[name].write(value)

        return self
    
    def print(
        self
    ) -> '_Uniforms':
        """
        Print the defined uniforms in console.
        """
        for key, value in self.uniforms.items():
            print(f'"{key}": {str(value)}')

# TODO: Moved to 'nodes.opengl.py'
class BaseNode:
    """
    The basic class of a node to manipulate frames
    as opengl textures. This node will process the
    frame as an input texture and will generate 
    also a texture as the output.

    Nodes can be chained and the result from one
    node can be applied on another node.
    """

    @property
    @abstractmethod
    def vertex_shader(
        self
    ) -> str:
        """
        The code of the vertex shader.
        """
        pass

    @property
    @abstractmethod
    def fragment_shader(
        self
    ) -> str:
        """
        The code of the fragment shader.
        """
        pass

    def __init__(
        self,
        context: moderngl.Context,
        size: tuple[int, int],
        **kwargs
    ):
        ParameterValidator.validate_mandatory_instance_of('context', context, moderngl.Context)
        # TODO: Validate size

        self.context: moderngl.Context = context
        """
        The context of the program.
        """
        self.size: tuple[int, int] = size
        """
        The size we want to use for the frame buffer
        in a (width, height) format.
        """
        # Compile shaders within the program
        self.program: moderngl.Program = self.context.program(
            vertex_shader = self.vertex_shader,
            fragment_shader = self.fragment_shader
        )

        # Create the fullscreen quad
        self.quad = get_fullscreen_quad_vao(
            context = self.context,
            program = self.program
        )

        # Create the output fbo
        self.output_tex = self.context.texture(self.size, 4)
        self.output_tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.fbo = self.context.framebuffer(color_attachments = [self.output_tex])

        self.uniforms: _Uniforms = _Uniforms(self.program)
        """
        Shortcut to the uniforms functionality.
        """
        # Auto set uniforms dynamically if existing
        for key, value in kwargs.items():
            self.uniforms.set(key, value)

    def process(
        self,
        input: Union[moderngl.Texture, 'VideoFrame', 'np.ndarray']
    ) -> moderngl.Texture:
        """
        Apply the shader to the 'input', that
        must be a frame or a texture, and return
        the new resulting texture.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        # TODO: Maybe we can accept a VideoFrame
        # or a numpy array and transform it here
        # into a texture, ready to be used:
        # frame_to_texture(
        #     # TODO: Do not use Pillow
        #     frame = np.array(Image.open("input.jpg").convert("RGBA")),
        #     context = self.context,
        #     numpy_format = 'rgba'
        # )
        if PythonValidator.is_instance_of(input, ['VideoFrame', 'ndarray']):
            # TODO: What about the numpy format (?)
            input = frame_to_texture(input, self.context)

        self.fbo.use()
        self.context.clear(0.0, 0.0, 0.0, 0.0)

        input.use(location = 0)

        if 'texture' in self.program:
            self.program['texture'] = 0

        self.quad.render()

        return self.output_tex
    
class WavingNode(BaseNode):
    """
    Just an example, without the shaders code
    actually, to indicate that we can use
    custom parameters to make it work.
    """

    @property
    def vertex_shader(
        self
    ) -> str:
        return (
            '''
            #version 330
            in vec2 in_vert;
            in vec2 in_texcoord;
            out vec2 v_uv;
            void main() {
                v_uv = in_texcoord;
                gl_Position = vec4(in_vert, 0.0, 1.0);
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
            uniform float amplitude;
            uniform float frequency;
            uniform float speed;
            in vec2 v_uv;
            out vec4 f_color;
            void main() {
                float wave = sin(v_uv.x * frequency + time * speed) * amplitude;
                vec2 uv = vec2(v_uv.x, v_uv.y + wave);
                f_color = texture(tex, uv);
            }
            '''
        )

    def __init__(
        self,
        context: moderngl.Context,
        size: tuple[int, int],
        amplitude: float = 0.05,
        frequency: float = 10.0,
        speed: float = 2.0
    ):
        super().__init__(
            context = context,
            size = size,
            amplitude = amplitude,
            frequency = frequency,
            speed = speed
        )

    # This is just an example and we are not
    # using the parameters actually, but we
    # could set those specific uniforms to be
    # processed by the code
    def process(
        self,
        input: Union[moderngl.Texture, 'VideoFrame', 'np.ndarray'],
        t: float = 0.0,
    ) -> moderngl.Texture:
        """
        Apply the shader to the 'input', that
        must be a frame or a texture, and return
        the new resulting texture.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        self.uniforms.set('time', t)

        return super().process(input)



"""
TODO: I should try to use the Node classes
to manipulate the frames because this is how
Davinci Resolve and other editors work.
"""


class FrameShaderBase(ABC):
    """
    Class to be inherited by any of our own
    custom opengl program classes.

    This shader base class must be used by all
    the classes that are modifying the frames
    one by one.
    """

    @property
    @abstractmethod
    def vertex_shader(
        self
    ) -> str:
        """
        Source code of the vertex shader.
        """
        pass

    @property
    @abstractmethod
    def fragment_shader(
        self
    ) -> str:
        """
        Source code of the fragment shader.
        """
        pass

    def __init__(
        self,
        size: tuple[int, int],
        first_frame: Union['VideoFrame', 'np.ndarray'],
        context: Union[moderngl.Context, None] = None,
    ):
        context = (
            moderngl.create_context(standalone = True)
            if context is None else
            context
        )

        self.size: tuple[int, int] = size
        """
        The size we want to use for the frame buffer
        in a (width, height) format.
        """
        self.first_frame: Union['VideoFrame', 'np.ndarray'] = first_frame
        """
        The first frame of the video in which we will
        apply the effect. Needed to build the texture.
        """
        self.context: moderngl.Context = context
        """
        The context of the program.
        """
        self.program: moderngl.Program = None
        """
        The opengl program.
        """
        self.fbo: moderngl.Framebuffer = None
        """
        The frame buffer object.
        """
        self.uniforms: _Uniforms = None
        """
        Shortcut to the uniforms functionality.
        """

        self._initialize_program()

    def _initialize_program(
        self
    ):
        """
        This method is to allow the effects to
        change their '__init__' method to be able
        to provide parameters that will be set as
        uniforms.
        """
        # Compile shaders within the program
        self.program: moderngl.Program = self.context.program(
            vertex_shader = self.vertex_shader,
            fragment_shader = self.fragment_shader
        )

        # Create frame buffer
        self.fbo = self.context.simple_framebuffer(self.size)
        # Create quad vertex array
        self.vao: moderngl.VertexArray = get_fullscreen_quad_vao(self.context, self.program)
        self.uniforms: _Uniforms = _Uniforms(self.program)

        # TODO: How do I manage these textures (?)
        self.textures = {}

        # TODO: Should we do this here (?)
        texture: moderngl.Texture = frame_to_texture(self.first_frame, self.context)
        texture.build_mipmaps()

    # TODO: I'm not using this method, but sounds
    # interesting to simplify the 'process_frame'
    # method in different mini actions
    def load_texture(
        self,
        image: np.ndarray,
        uniform_name: str,
        texture_unit = 0
    ):
        """
        Load a texture with the given 'image' and set
        it to the uniform with the given 'uniform_name'.

        TODO: Understand better the 'texture_unit'
        """
        # This is to receive a path (str) to an image
        #img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM).convert("RGBA")
        image = np.flipud(image)
        tex = self.context.texture((image.shape[1], image.shape[0]), 4, image.tobytes())
        tex.use(texture_unit)
        self.textures[uniform_name] = tex
        self.uniforms.set(uniform_name, texture_unit)

    @abstractmethod
    def _prepare_frame(
        self,
        t: float
    ):
        """
        Set the uniforms we need to process that
        specific frame and the code to calculate
        those uniforms we need.
        """
        pass

    def process_frame(
        self,
        frame: Union['VideoFrame', np.ndarray],
        t: float,
        numpy_format: str = 'rgb24'
    ) -> 'VideoFrame':
        # TODO: This method accepts 'np.ndarray' to 
        # prepare it to frames coming from other source
        # different than reading a video here (that 
        # will be processed as VideoFrame). Check the
        # sizes and [0], [1] indexes.
        ParameterValidator.validate_mandatory_instance_of('frame', frame, ['VideoFrame', 'ndarray'])

        # By now I call this here because I don't need
        # to send nothing specific when calculating the
        # frame...
        self._prepare_frame(t)

        # Set frame as a texture
        texture = frame_to_texture(frame, self.context, numpy_format)
        # TODO: Why 0 (?)
        #texture.use(0) 
        texture.use() 

        # # TODO: Check this
        # if 'u_texture' in self.program:
        #     self.program['u_texture'].value = 0

        # Set the frame buffer a a whole black frame
        self.context.clear(0.0, 0.0, 0.0)
        # TODO: No 'self.fbo.use()' here (?)
        self.fbo.use()
        self.vao.render(moderngl.TRIANGLE_STRIP)

        # Read output of fbo
        output = np.flipud(
            np.frombuffer(
                self.fbo.read(components = 3, alignment = 1), 
                dtype = np.uint8
            ).reshape((texture.size[1], texture.size[0], 3))
            #).reshape((self.size[1], self.size[0], 3))
        )

        # We want a VideoFrame instance because we
        # we can send it directly to the mux to
        # write
        output: 'VideoFrame' = av.VideoFrame.from_ndarray(output, format = numpy_format)

        return output

# Example classes below
class WavingFrame(FrameShaderBase):
    """
    The frame but waving as a flag.
    """

    @property
    def vertex_shader(
        self
    ) -> str:
        return (
            '''
            #version 330
            in vec2 in_vert;
            in vec2 in_texcoord;
            out vec2 v_uv;
            void main() {
                v_uv = in_texcoord;
                gl_Position = vec4(in_vert, 0.0, 1.0);
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
    
    def __init__(
        self,
        size,
        first_frame,
        context = None,
        amplitude: float = 0.05,
        frequency: float = 10.0,
        speed: float = 2.0
    ):
        super().__init__(size, first_frame, context)

        # TODO: Use automatic way of detecting the
        # parameters that are not 'self', 'size',
        # 'first_frame' nor 'context' and set those
        # as uniforms automatically
    
        self.uniforms.set('amp', amplitude)
        self.uniforms.set('freq', frequency)
        self.uniforms.set('speed', speed)
    
    def _prepare_frame(
        self,
        t: float
    ) -> 'WavingFrame':
        """
        Precalculate all the things we need to process
        a frame, like the uniforms, etc.
        """
        self.uniforms.set('time', t)

        return self

class BreathingFrame(FrameShaderBase):
    """
    The frame but as if it was breathing.
    """

    @property
    def vertex_shader(
        self
    ) -> str:
        return (
            '''
            #version 330
            in vec2 in_vert;
            in vec2 in_texcoord;
            out vec2 v_text;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                v_text = in_texcoord;
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
            in vec2 v_text;
            out vec4 f_color;
            // Use uniforms to be customizable

            void main() {
                // Dynamic zoom scaled with t
                float scale = 1.0 + 0.05 * sin(time * 2.0);  // 5% de zoom
                vec2 center = vec2(0.5, 0.5);

                // Recalculate coords according to center
                vec2 uv = (v_text - center) / scale + center;

                // Clamp to avoid artifacts
                uv = clamp(uv, 0.0, 1.0);

                f_color = texture(tex, uv);
            }
            '''
        )
    
    def _prepare_frame(
        self,
        t: float
    ) -> 'BreathingFrame':
        # TODO: Use automatic way of detecting the
        # parameters that are not 'self', 'size',
        # 'first_frame' nor 'context' and set those
        # as uniforms automatically
    
        self.uniforms.set('time', t)

        return self

class HandheldFrame(FrameShaderBase):
    """
    The frame but as if it was being recorder by
    someone holding a camera, that is not 100%
    stable.
    """

    @property
    def vertex_shader(
        self
    ) -> str:
        return (
            '''
            #version 330
            in vec2 in_vert;
            in vec2 in_texcoord;
            out vec2 v_text;

            uniform mat3 transform;

            void main() {
                vec3 pos = vec3(in_vert, 1.0);
                pos = transform * pos;
                gl_Position = vec4(pos.xy, 0.0, 1.0);
                v_text = in_texcoord;
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
            in vec2 v_text;
            out vec4 f_color;

            void main() {
                f_color = texture(tex, v_text);
            }
            '''
        )
    
    def _prepare_frame(
        self,
        t: float
    ) -> 'HandheldFrame':
        import math
        def handheld_matrix_exaggerated(t):
            # Rotación más notoria
            angle = smooth_noise(t, freq=0.8, scale=0.05)  # antes 0.02

            # Traslaciones más grandes
            tx = smooth_noise(t, freq=1.1, scale=0.04)     # antes 0.015
            ty = smooth_noise(t, freq=1.4, scale=0.04)

            # Zoom más agresivo
            zoom = 1.0 + smooth_noise(t, freq=0.5, scale=0.06)  # antes 0.02

            cos_a, sin_a = math.cos(angle), math.sin(angle)

            return np.array([
                [ cos_a * zoom, -sin_a * zoom, tx],
                [ sin_a * zoom,  cos_a * zoom, ty],
                [ 0.0,           0.0,          1.0]
            ], dtype="f4")

        def smooth_noise(t, freq=1.5, scale=1.0):
            """Pequeño ruido orgánico usando senos y cosenos mezclados"""
            return (
                math.sin(t * freq) +
                0.5 * math.cos(t * freq * 0.5 + 1.7) +
                0.25 * math.sin(t * freq * 0.25 + 2.5)
            ) * scale

        def handheld_matrix(t):
            # Rotación ligera (en radianes)
            angle = smooth_noise(t, freq=0.8, scale=0.02)

            # Traslación horizontal/vertical
            tx = smooth_noise(t, freq=1.1, scale=0.015)
            ty = smooth_noise(t, freq=1.4, scale=0.015)

            # Zoom (escala)
            zoom = 1.0 + smooth_noise(t, freq=0.5, scale=0.02)

            cos_a, sin_a = math.cos(angle), math.sin(angle)

            # Matriz de transformación: Zoom * Rotación + Traslación
            return np.array([
                [ cos_a * zoom, -sin_a * zoom, tx],
                [ sin_a * zoom,  cos_a * zoom, ty],
                [ 0.0,           0.0,          1.0]
            ], dtype = "f4")
        
        self.uniforms.set_mat('transform', handheld_matrix_exaggerated(t).tobytes())

        return self
    
class OrbitingFrame(FrameShaderBase):
    """
    The frame but orbiting around the camera.
    """

    @property
    def vertex_shader(
        self
    ) -> str:
        return (
            '''
            #version 330

            in vec2 in_vert;
            in vec2 in_texcoord;

            out vec2 v_uv;

            uniform mat4 mvp;   // Model-View-Projection matrix

            void main() {
                v_uv = in_texcoord;
                // El quad está en XY, lo pasamos a XYZ con z=0
                vec4 pos = vec4(in_vert, 0.0, 1.0);
                gl_Position = mvp * pos;
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
            in vec2 v_uv;
            out vec4 f_color;

            void main() {
                f_color = texture(tex, v_uv);
            }
            '''
        )
    
    def _prepare_frame(
        self,
        t: float
    ) -> 'OrbitingFrame':
        def perspective(fov_y_rad, aspect, near, far):
            f = 1.0 / np.tan(fov_y_rad / 2.0)
            m = np.zeros((4,4), dtype='f4')
            m[0,0] = f / aspect
            m[1,1] = f
            m[2,2] = (far + near) / (near - far)
            m[2,3] = (2 * far * near) / (near - far)
            m[3,2] = -1.0
            return m
        
        def look_at(eye, target, up=(0,1,0)):
            eye = np.array(eye, dtype='f4')
            target = np.array(target, dtype='f4')
            up = np.array(up, dtype='f4')

            f = target - eye
            f = f / np.linalg.norm(f)
            s = np.cross(f, up)
            s = s / np.linalg.norm(s)
            u = np.cross(s, f)

            m = np.eye(4, dtype='f4')
            m[0,0:3] = s
            m[1,0:3] = u
            m[2,0:3] = -f
            m[0,3] = -np.dot(s, eye)
            m[1,3] = -np.dot(u, eye)
            m[2,3] =  np.dot(f, eye)
            return m

        def translate(x, y, z):
            m = np.eye(4, dtype='f4')
            m[0,3] = x
            m[1,3] = y
            m[2,3] = z
            return m

        def rotate_y(angle):
            c, s = np.cos(angle), np.sin(angle)
            m = np.eye(4, dtype='f4')
            m[0,0], m[0,2] =  c,  s
            m[2,0], m[2,2] = -s,  c
            return m
        
        def scale_uniform(k):
            m = np.eye(4, dtype='f4')
            m[0,0] = m[1,1] = m[2,2] = k
            return m
        
        def carousel_mvp(t, *,
                 aspect,
                 fov_deg=60.0,
                 radius=4.0,
                 center_z=-6.0,
                 speed=1.0,
                 face_center_strength=1.0,
                 extra_scale=1.0):
            """
            t: tiempo en segundos
            aspect: width/height del framebuffer
            radius: radio en XZ
            center_z: desplaza el carrusel entero hacia -Z para que esté frente a cámara
            speed: velocidad angular
            face_center_strength: 1.0 = panel mira al centro; 0.0 = no gira con la órbita
            """

            # Proyección y vista (cámara en el origen mirando hacia -Z)
            proj = perspective(np.radians(fov_deg), aspect, 0.1, 100.0)
            view = np.eye(4, dtype='f4')  # o look_at((0,0,0), (0,0,-1))

            # Ángulo de órbita (elige el offset para que "entre" por la izquierda)
            theta = speed * t - np.pi * 0.5

            # Órbita en XZ con el centro desplazado a center_z
            # x = radius * np.cos(theta)
            # z = radius * np.sin(theta) + center_z
            x = radius * np.cos(theta)
            z = (radius * 0.2) * np.sin(theta) + center_z

            # Yaw para que el panel apunte al centro (0,0,center_z)
            # El vector desde panel -> centro es (-x, 0, center_z - z)
            yaw_to_center = np.arctan2(-x, (center_z - z))  # atan2(X, Z)
            yaw = face_center_strength * yaw_to_center

            model = translate(x, 0.0, z) @ rotate_y(yaw) @ scale_uniform(extra_scale)

            # ¡IMPORTANTE! OpenGL espera column-major: transponemos al escribir
            mvp = proj @ view @ model
            return mvp
        
        aspect = self.size[0] / self.size[1]
        mvp = carousel_mvp(t, aspect=aspect, radius=4.0, center_z=-4.0, speed=1.2, face_center_strength=1.0, extra_scale = 1.0)

        self.uniforms.set_mat('mvp', mvp.T.tobytes())

        return self
    
class RotatingInCenterFrame(FrameShaderBase):
    """
    The frame but orbiting around the camera.
    """

    @property
    def vertex_shader(
        self
    ) -> str:
        return (
            '''
            #version 330

            in vec2 in_vert;
            in vec2 in_texcoord;
            out vec2 v_uv;

            uniform float time;
            uniform float speed;

            void main() {
                v_uv = in_texcoord;

                // Rotación alrededor del eje Y
                float angle = time * speed;              // puedes usar time directamente, o time * speed
                float cosA = cos(angle);
                float sinA = sin(angle);

                // Convertimos el quad a 3D (x, y, z)
                vec3 pos = vec3(in_vert.xy, 0.0);

                // Rotación Y
                mat3 rotY = mat3(
                    cosA, 0.0, sinA,
                    0.0 , 1.0, 0.0,
                -sinA, 0.0, cosA
                );

                pos = rotY * pos;

                gl_Position = vec4(pos, 1.0);
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

            in vec2 v_uv;
            out vec4 f_color;

            uniform sampler2D tex;

            void main() {
                f_color = texture(tex, v_uv);
            }
            '''
        )
    
    def __init__(
        self,
        size,
        first_frame,
        context = None,
        speed: float = 30
    ):
        super().__init__(size, first_frame, context)

        self.uniforms.set('speed', speed)

    def _prepare_frame(
        self,
        t: float
    ) -> 'BreathingFrame':
        self.uniforms.set('time', t)

        return self

class StrangeTvFrame(FrameShaderBase):
    """
    Nice effect like a tv screen or something...
    """

    @property
    def vertex_shader(
        self
    ) -> str:
        return (
            '''
            #version 330
            in vec2 in_vert;
            in vec2 in_texcoord;
            out vec2 v_uv;

            void main() {
                v_uv = in_texcoord;
                gl_Position = vec4(in_vert, 0.0, 1.0);
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

            // ---- Parámetros principales (ajústalos en runtime) ----
            uniform float aberr_strength;  // 0..3   (fuerza del RGB split radial)
            uniform float barrel_k;        // -0.5..0.5  (distorsión de lente; positivo = barrel)
            uniform float blur_radius;     // 0..0.02 (radio de motion blur en UV)
            uniform float blur_angle;      // en radianes (dirección del arrastre)
            uniform int   blur_samples;    // 4..24  (taps del blur)
            uniform float vignette_strength; // 0..2
            uniform float grain_amount;    // 0..0.1
            uniform float flicker_amount;  // 0..0.2
            uniform float scanline_amount; // 0..0.2

            in vec2 v_uv;
            out vec4 f_color;

            // --- helpers ---
            float rand(vec2 co){
                return fract(sin(dot(co, vec2(12.9898,78.233))) * 43758.5453);
            }

            // Barrel distortion (simple, k>0 curva hacia fuera)
            vec2 barrel(vec2 uv, float k){
                // map to [-1,1]
                vec2 p = uv * 2.0 - 1.0;
                float r2 = dot(p, p);
                p *= (1.0 + k * r2);
                // back to [0,1]
                return p * 0.5 + 0.5;
            }

            // Aberración cromática radial
            vec3 sample_chromatic(sampler2D t, vec2 uv, vec2 center, float strength){
                // Offset radial según distancia al centro
                vec2 d = uv - center;
                float r = length(d);
                vec2 dir = (r > 1e-5) ? d / r : vec2(0.0);
                // Cada canal se desplaza un poco distinto
                float s = strength * r * 0.005; // escala fina
                float sr = s * 1.0;
                float sg = s * 0.5;
                float sb = s * -0.5; // azul hacia dentro para contraste

                float rC = texture(t, uv + dir * sr).r;
                float gC = texture(t, uv + dir * sg).g;
                float bC = texture(t, uv + dir * sb).b;
                return vec3(rC, gC, bC);
            }

            void main(){
                vec2 uv = v_uv;
                vec2 center = vec2(0.5, 0.5);

                // Lente (barrel/pincushion)
                uv = barrel(uv, barrel_k);

                // Early out si nos salimos mucho (fade de bordes)
                vec2 uv_clamped = clamp(uv, 0.0, 1.0);
                float edge = smoothstep(0.0, 0.02, 1.0 - max(max(-uv.x, uv.x-1.0), max(-uv.y, uv.y-1.0)));

                // Dirección del motion blur
                vec2 dir = vec2(cos(blur_angle), sin(blur_angle));
                // Pequeña variación temporal para que “respire”
                float jitter = (sin(time * 13.0) * 0.5 + 0.5) * 0.4 + 0.6;

                // Acumulación de blur con pesos
                vec3 acc = vec3(0.0);
                float wsum = 0.0;

                int N = max(1, blur_samples);
                for(int i = 0; i < 64; ++i){         // hard cap de seguridad
                    if(i >= N) break;
                    // t de -1..1 distribuye muestras a ambos lados
                    float fi = float(i);
                    float t = (fi / float(N - 1)) * 2.0 - 1.0;

                    // curva de pesos (gauss approx)
                    float w = exp(-t*t * 2.5);
                    // offset base
                    vec2 ofs = dir * t * blur_radius * jitter;

                    // micro-jitter por muestra para romper banding
                    ofs += vec2(rand(uv + fi)*0.0005, rand(uv + fi + 3.14)*0.0005) * blur_radius;

                    // muestreo con aberración cromática
                    vec3 c = sample_chromatic(tex, uv + ofs, center, aberr_strength);

                    acc += c * w;
                    wsum += w;
                }
                vec3 col = acc / max(wsum, 1e-6);

                // Scanlines + flicker
                float scan = 1.0 - scanline_amount * (0.5 + 0.5 * sin((uv.y + time*1.7)*3.14159*480.0));
                float flick = 1.0 + flicker_amount * (sin(time*60.0 + uv.x*10.0) * 0.5 + 0.5);
                col *= scan * flick;

                // Vignette (radial)
                float r = distance(uv, center);
                float vig = 1.0 - smoothstep(0.7, 1.0, r * (1.0 + 0.5*vignette_strength));
                col *= mix(1.0, vig, vignette_strength);

                // Grano
                float g = (rand(uv * (time*37.0 + 1.0)) - 0.5) * 2.0 * grain_amount;
                col += g;

                // Fade de bordes por clamp/warp
                col *= edge;

                f_color = vec4(col, 1.0);
            }
            '''
        )
    
    def __init__(
        self,
        size,
        first_frame,
        context = None,
        aberr_strength = 1.5,
        barrel_k = 0.08,
        blur_radius = 0.006,
        blur_angle = 0.0, # (0 = horizontal, 1.57 ≈ vertical)
        blur_samples = 12,
        vignette_strength = 0.8,
        grain_amount = 0.02,
        flicker_amount = 0.05,
        scanline_amount = 0.05
    ):
        super().__init__(size, first_frame, context)

        self.uniforms.set('aberr_strength', aberr_strength)
        self.uniforms.set('barrel_k', barrel_k)
        self.uniforms.set('blur_radius', blur_radius)
        self.uniforms.set('blur_angle', blur_angle)
        self.uniforms.set('blur_samples', blur_samples)
        self.uniforms.set('vignette_strength', vignette_strength)
        self.uniforms.set('grain_amount', grain_amount)
        self.uniforms.set('flicker_amount', flicker_amount)
        self.uniforms.set('scanline_amount', scanline_amount)

    def _prepare_frame(
        self,
        t: float
    ) -> 'BreathingFrame':
        self.uniforms.set('time', t)

        return self
    
class GlitchRgbFrame(FrameShaderBase):
    """
    Nice effect like a tv screen or something...
    """

    @property
    def vertex_shader(
        self
    ) -> str:
        return (
            '''
            #version 330

            // ----------- Vertex Shader -----------
            in vec2 in_vert;
            in vec2 in_texcoord;

            out vec2 v_uv;

            void main() {
                v_uv = in_texcoord;
                gl_Position = vec4(in_vert, 0.0, 1.0);
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

            // ----------- Fragment Shader -----------
            uniform sampler2D tex;
            uniform float time;

            // Intensidades del efecto
            uniform float amp;      // amplitud de distorsión
            uniform float freq;     // frecuencia de la onda
            uniform float glitchAmp; // fuerza del glitch
            uniform float glitchSpeed;

            in vec2 v_uv;
            out vec4 f_color;

            void main() {
                // Distorsión sinusoidal en Y
                float wave = sin(v_uv.x * freq + time * 2.0) * amp;

                // Pequeño desplazamiento aleatorio (shake)
                float shakeX = (fract(sin(time * 12.9898) * 43758.5453) - 0.5) * 0.01;
                float shakeY = (fract(sin(time * 78.233) * 12345.6789) - 0.5) * 0.01;

                // Coordenadas base con distorsión
                vec2 uv = vec2(v_uv.x + shakeX, v_uv.y + wave + shakeY);

                // Glitch con separación RGB
                float glitch = sin(time * glitchSpeed) * glitchAmp;
                vec2 uv_r = uv + vec2(glitch, 0.0);
                vec2 uv_g = uv + vec2(-glitch * 0.5, glitch * 0.5);
                vec2 uv_b = uv + vec2(0.0, -glitch);

                // Muestreo canales desplazados
                float r = texture(tex, uv_r).r;
                float g = texture(tex, uv_g).g;
                float b = texture(tex, uv_b).b;

                f_color = vec4(r, g, b, 1.0);
            }
            '''
        )
    
    def __init__(
        self,
        size,
        first_frame,
        context = None,
        amp = 0.02,
        freq = 25.0,
        glitchAmp = 0.02,
        glitchSpeed = 30.0
    ):
        super().__init__(size, first_frame, context)

        self.uniforms.set('amp', amp)
        self.uniforms.set('freq', freq)
        self.uniforms.set('glitchAmp', glitchAmp)
        self.uniforms.set('glitchSpeed', glitchSpeed)

    def _prepare_frame(
        self,
        t: float
    ) -> 'BreathingFrame':
        self.uniforms.set('time', t)

        return self
    