from yta_video_opengl.utils import frame_to_texture, get_fullscreen_quad_vao
from yta_video_opengl.nodes import Node
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from abc import abstractmethod
from typing import Union

import numpy as np
import moderngl


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

class OpenglNode(Node):
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
    
class WavingNode(OpenglNode):
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