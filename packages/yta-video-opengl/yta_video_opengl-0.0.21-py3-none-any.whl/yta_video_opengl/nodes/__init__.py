from yta_validation.parameter import ParameterValidator
from typing import Union
from abc import ABC, abstractmethod

import av
import moderngl


class Node(ABC):
    """
    Base class to represent a node, which
    is an entity that processes frames
    individually.

    This class must be inherited by any 
    video or audio node class.
    """

    # TODO: What about the types?
    @abstractmethod
    def process(
        frame: Union[av.VideoFrame, av.AudioFrame, moderngl.Texture],
        t: float
        # TODO: Maybe we need 'fps' and 'number_of_frames'
        # to calculate progressions or similar...
    ) -> Union[av.VideoFrame, av.AudioFrame, moderngl.Texture]:
        pass

class TimedNode:
    """
    Class to represent a Node wrapper to
    be able to specify the time range in
    which we want the node to be applied.

    If the 't' time moment is not inside
    this range, the frame will be returned
    as it is, with no change.

    A 't' time moment inside the range has
    this condition:
    - `start <= t < end`

    We are not including the end because
    the next TimedNode could start on that
    specific value, and remember that the
    first time moment is 0.

    This is the class that has to be applied
    when working with videos and not a Node
    directly.

    The 'start' and 'end' values by default
    """

    def __init__(
        self,
        node: Node,
        start: float = 0.0,
        end: Union[float, None] = None
    ):
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_positive_number('end', end, do_include_zero = False)

        if (
            end is not None and
            end < start
        ):
            raise Exception('The "end" parameter provided must be greater or equal to the "start" parameter.')

        self.node: Node = node
        """
        The node we are wrapping and we want to
        apply as a modification of the frame in
        which we are in a 't' time moment.
        """
        self.start: float = start
        """
        The 't' time moment in which the Node must
        start being applied (including it).
        """
        self.end: Union[float, None] = end
        """
        The 't' time moment in which the Node must
        stop being applied (excluding it).
        """

    def is_within_time(
        self,
        t: float
    ) -> bool:
        """
        Flag to indicate if the 't' time moment provided
        is in the range of this TimedNode instance, 
        which means that it fits this condition:
        - `start <= t < end`
        """
        return (
            self.start <= t < self.end
            if self.end is not None else
            self.start <= t
        )

    def process(
        self,
        frame: Union[av.VideoFrame, av.AudioFrame, moderngl.Texture],
        t: float
        # TODO: Maybe we need 'fps' and 'number_of_frames'
        # to calculate progressions or similar...
    ) -> Union['VideoFrame', 'AudioFrame', 'Texture']:
        """
        Process the frame if the provided 't' time
        moment is in the range of this TimedNode
        instance.
        """
        return (
            self.node.process(frame, t)
            if self.is_within_time(t) else
            frame
        )