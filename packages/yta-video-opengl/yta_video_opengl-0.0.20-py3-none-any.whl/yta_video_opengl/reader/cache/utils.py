from av.audio.frame import AudioFrame
from quicktions import Fraction
from typing import Union


def trim_audio_frame(
    frame: AudioFrame,
    start: Union[int, float, Fraction],
    end: Union[int, float, Fraction],
    time_base: Fraction
) -> AudioFrame:
    """
    Trim an audio frame to obtain the part between
    [start, end), that is provided in seconds.
    """
    # (channels, n_samples)
    samples = frame.to_ndarray()  
    n_samples = samples.shape[1]

    # In seconds
    frame_start = frame.pts * float(time_base)
    frame_end = frame_start + (n_samples / frame.sample_rate)

    # Overlapping 
    cut_start = max(frame_start, float(start))
    cut_end = min(frame_end, float(end))

    if cut_start >= cut_end:
        # No overlapping
        return None  

    # To sample indexes
    start_index = int(round((cut_start - frame_start) * frame.sample_rate))
    end_index = int(round((cut_end - frame_start) * frame.sample_rate))

    new_frame = AudioFrame.from_ndarray(
        # end_index is not included: so [start, end)
        array = samples[:, start_index:end_index],
        format = frame.format,
        layout = frame.layout
    )

    # Set needed attributes
    new_frame.sample_rate = frame.sample_rate
    new_frame.time_base = time_base
    new_frame.pts = int(round(cut_start / float(time_base)))

    return new_frame