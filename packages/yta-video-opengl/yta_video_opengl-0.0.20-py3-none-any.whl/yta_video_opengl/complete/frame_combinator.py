"""
TODO: I don't like the name nor the
location of this file, but it is here
to encapsulate some functionality 
related to combining video frames.

Module to contain methods that combine
video frames. Call them with the 2
frames you want to combine and you 
will get the combined frame as return.
"""
from av.audio.resampler import AudioResampler
from av.audio.frame import AudioFrame

import numpy as np


class VideoFrameCombinator:
    """
    Class to wrap the functionality related
    to combine different video frames.
    """

    @staticmethod
    def blend_alpha(
        bottom: np.ndarray,
        top: np.ndarray,
        alpha = 0.5
    ):
        return (alpha * top + (1 - alpha) * bottom).astype(np.uint8)

    @staticmethod
    def blend_add(
        bottom: np.ndarray,
        top: np.ndarray
    ):
        """
        Aclara la imagen combinada, como si superpusieras dos proyectores de luz.
        """
        return np.clip(bottom.astype(np.int16) + top.astype(np.int16), 0, 255).astype(np.uint8)

    @staticmethod
    def blend_multiply(
        bottom: np.ndarray,
        top: np.ndarray
    ):
        """
        Oscurece, como proyectar dos transparencias juntas.
        """
        return ((bottom.astype(np.float32) * top.astype(np.float32)) / 255).astype(np.uint8)

    @staticmethod
    def blend_screen(
        bottom: np.ndarray,
        top: np.ndarray
    ):
        """
        Hace lo contrario a Multiply, aclara la imagen.
        """
        return (255 - ((255 - bottom.astype(np.float32)) * (255 - top.astype(np.float32)) / 255)).astype(np.uint8)

    @staticmethod
    def blend_overlay(
        bottom: np.ndarray,
        top: np.ndarray
    ):
        """
        Mezcla entre Multiply y Screen según el brillo de cada píxel.
        """
        b = bottom.astype(np.float32) / 255
        t = top.astype(np.float32) / 255
        mask = b < 0.5
        result = np.zeros_like(b)
        result[mask] = 2 * b[mask] * t[mask]
        result[~mask] = 1 - 2 * (1 - b[~mask]) * (1 - t[~mask])

        return (result * 255).astype(np.uint8)

    @staticmethod
    def blend_difference(
        bottom: np.ndarray,
        top: np.ndarray
    ):
        """
        Resalta las diferencias entre los dos frames.
        """
        return np.abs(bottom.astype(np.int16) - top.astype(np.int16)).astype(np.uint8)

    # TODO: This one needs a mask, thats why
    # it is commented
    # @staticmethod
    # def blend_mask(
    #     bottom,
    #     top,
    #     mask
    # ):
    #     """
    #     En lugar de un alpha fijo, puedes pasar una máscara (por ejemplo, un degradado o un canal alfa real)

    #     mask: array float32 entre 0 y 1, mismo tamaño que frame.
    #     """
    #     return (mask * top + (1 - mask) * bottom).astype(np.uint8)

class AudioFrameCombinator:
    """
    Class to wrap the functionality related
    to combine different audio frames.
    """

    @staticmethod
    def sum_tracks_frames(
        tracks_frames: list[AudioFrame],
        sample_rate: int = 44100,
        layout: str = 'stereo',
        format: str = 'fltp',
        do_normalize: bool = True
    ) -> AudioFrame:
        """
        Sum all the audio frames from the different
        tracks that are given in the 'tracks_frames'
        list (each column is a single audio frame of
        a track). This must be a list that should 
        come from a converted matrix that was
        representing each track in a row and the
        different audio frames for that track on each
        column.

        This method is to sum audio frames of one
        specific 't' time moment of a video.

        The output will be the sum of all the audio
        frames and it will be normalized to avoid
        distortion if 'do_normalize' is True (it is
        recommended).
        """
        if len(tracks_frames) == 0:
            raise Exception('The "tracks_frames" list of audio frames is empty.')
        
        arrays = []
        resampler: AudioResampler = AudioResampler(
            format = format,
            layout = layout,
            rate = sample_rate
        )

        for track_frame in tracks_frames:
            # Resample to output format
            # TODO: What if the resampler creates more
            # than one single frame? I don't know what
            # to do... I'll see when it happens
            track_frame = resampler.resample(track_frame)
            
            if len(track_frame) > 1:
                print('[ ! ]   The resampler has given more than 1 frame...')

            track_frame_array = track_frame[0].to_ndarray()

            # Transform to 'float32' [-1, 1]
            # TODO: I think this is because the output
            # is 'fltp' but we have more combinations
            # so this must be refactored
            if track_frame_array.dtype == np.int16:
                track_frame_array = track_frame_array.astype(np.float32) / 32768.0
            elif track_frame_array.dtype != np.float32:
                track_frame_array = track_frame_array.astype(np.float32)

            # Mono to stereo if needed
            # TODO: What if source is 'stereo' and we
            # want mono (?)
            if (
                track_frame_array.shape[0] == 1 and
                layout == 'stereo'
            ):
                track_frame_array = np.repeat(track_frame_array, 2, axis = 0)

            arrays.append(track_frame_array)

        # Same length and fill with zeros if needed
        max_len = max(a.shape[1] for a in arrays)
        stacked = []
        for a in arrays:
            # TODO: Again, this 'float32' is because output
            # is 'fltp' I think...
            buf = np.zeros((a.shape[0], max_len), dtype = np.float32)
            buf[:, :a.shape[1]] = a
            stacked.append(buf)

        # Sum all the sounds
        mix = np.sum(stacked, axis = 0)
        if do_normalize:
            # Avoid distortion and saturation
            mix /= len(stacked)

        # Avoid clipping
        mix = np.clip(mix, -1.0, 1.0)

        out = AudioFrame.from_ndarray(
            array = mix,
            format = format,
            layout = layout
        )
        out.sample_rate = sample_rate

        return out

# TODO: This method below has been refactored
# to the 'sum_tracks_frames', so delete it 
# when the one above is working well
def mix_audio_frames_by_index(
    tracks_frames,
    sample_rate: int,
    layout = 'stereo',
):
    """
    Combine all the columns of the given
    matrix of audio frames 'tracks_frames'.
    The rows are the different tracks and
    the columns are the frame at that 't'
    moment of each of those tracks.

    The 'tracks_frames' matrix needs to be
    pre-processed to have only 1 single
    frame to combine, so we concatenate
    all the frames if more than 1 per 
    column.
    """
    # TODO: Please, improve and clean all this
    # code is so sh*tty, and make utils to
    # combine and those things, not here...
    # Also the formats, make them dynamic and
    # based on the output that is defined here
    # in the Timeline class.
    mixed_frames = []

    # Iterate by columns (each row is a track)
    for frames_at_index in zip(*tracks_frames):
        arrays = []
        for f in frames_at_index:
            # Resample to output expected values
            # TODO: This must be dynamic depending
            # on the track values
            resampler = AudioResampler(format = 'fltp', layout = 'stereo', rate = sample_rate)
            arr = resampler.resample(f)

            arr = f.to_ndarray()

            # TODO: This below must change depending
            # on the expected output, for us and now
            # it is float32, fltp, stereo, 44_100
            # Same format
            if arr.dtype == np.int16:
                arr = arr.astype(np.float32) / 32768.0

            # Same layout (number of channels)
            if arr.shape[0] == 1:
                return np.repeat(arr, 2, axis = 0)
            # elif arr.dtype == np.float32:
            #     # Ya está en [-1,1], no lo toques
            #     pass

            arrays.append(arr)

        # Alinear longitudes
        max_len = max(a.shape[1] for a in arrays)
        stacked = []
        for a in arrays:
            buf = np.zeros((a.shape[0], max_len), dtype = np.float32)
            buf[:, :a.shape[1]] = a
            stacked.append(buf)

        # Mezcla
        mix = np.sum(stacked, axis = 0) / len(stacked)
        #mix = np.sum(stacked, axis = 0) 

        # Limitar al rango [-1,1]
        mix = np.clip(mix, -1.0, 1.0)

        # Crear frame de salida
        # TODO: What about the 'format' if they
        # are all different (?)
        out = AudioFrame.from_ndarray(mix, format = 'fltp', layout = layout)
        out.sample_rate = sample_rate
        # TODO: This will be written later when
        # encoding
        # out.pts = frames_at_index[0].pts
        # out.time_base = frames_at_index[0].time_base

        print(mix.min(), mix.max())

        mixed_frames.append(out)

    return mixed_frames

