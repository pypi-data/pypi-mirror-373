from yta_constants.enum import YTAEnum as Enum
from yta_validation.parameter import ParameterValidator


class AudioChannel(Enum):
    """
    Simple Enum class to handle the audio channels
    easier.
    """

    LEFT = -1.0
    RIGHT = 1.0

class StereoAudioFormatMode(Enum):
    """
    Class to wrap the formats we accept
    to format an stereo numpy audio
    (which means how do we want to extract
    the channels).
    """

    LEFT = 'left'
    """
    We will obtain only the left channel.
    """
    RIGHT = 'right'
    """
    We will obtain only the right channel.
    """
    MIX_FIRST_LEFT = 'mix_first_left'
    """
    We will mix the left and the right 
    channel in only one that will be:
    - `L0, R0, L1, R1, L2, R2`
    """
    MIX_FIRST_RIGHT = 'mix_first_right'
    """
    We will mix the right and the left 
    channel in only one that will be:
    - `R0, L0, R1, L1, R2, L2`
    """
    # These below are numpy original
    NUMPY_C = 'numpy_c'
    """
    Flatten by traversing rows first (as
    stored in C). This is the default value.
    This is the 'C' option in numpy.
    
    Example:
    - `np.array([[1, 2], [3, 4]]).flatten(order = 'C')`
    -> Result: `[1 2 3 4]`
    """
    NUMPY_F = 'numpy_f'
    """
    Flatten by traversing columns first (as
    Fortran does). This is the 'F' option in
    numpy.

    Example:
    - `np.array([[1, 2], [3, 4]]).flatten(order = 'F')` 
    -> Result: `[1 3 2 4]`
    """
    NUMPY_A = 'numpy_a'
    """
    If the array is C-contiguous, it behaves
    like 'MIX_C'. If it is Fortran-contiguous,
    it behaves like 'MIX_F'. Use it when you
    don't want to force a new order if it's
    already optimized.
    """
    NUMPY_K = 'NUMPY_K'
    """
    Flattens according to the order in which
    the data is actually stored in memory. It
    may look similar to 'MIX_C' or 'MIX_F' but
    it respects complex structures such as
    slices, views, etc. It may include
    non-obvious results if the array is not
    contiguous.
    """

    # TODO: This method needs numpy...
    def format_audio(
        self,
        audio: 'np.ndarray'
    ) -> 'np.ndarray':
        """
        Format the audio to this mode or raise
        an Exception if not a valid 'audio'.

        This method will return a numpy array
        of only one dimension, corresponding to
        the expected format.
        """
        ParameterValidator.validate_mandatory_numpy_array('audio', audio)

        if (
            audio.ndim > 2 or
            (
                audio.ndim == 2 and
                audio.shape[1] not in [1, 2]
            )
        ):
            raise Exception('The audio is not mono or stereo.')

        return (
            audio
            if audio.ndim == 1 else
            audio[:, 0]
            if self == StereoAudioFormatMode.LEFT else
            audio[:, 1]
            if self == StereoAudioFormatMode.RIGHT else
            audio.T.flatten(order = 'F')
            if self == StereoAudioFormatMode.MIX_FIRST_LEFT else
            audio[:, [1, 0]].T.flatten(order = 'F')
            if self == StereoAudioFormatMode.MIX_FIRST_RIGHT else
            # These below are numpy original
            audio.flatten(order = 'C') 
            if self == StereoAudioFormatMode.NUMPY_C else
            audio.flatten(order = 'F')
            if self == StereoAudioFormatMode.NUMPY_F else
            audio.flatten(order = 'A') 
            if self == StereoAudioFormatMode.NUMPY_A else
            audio.flatten(order = 'K')
            if self == StereoAudioFormatMode.NUMPY_K else
            # TODO: Raise exception (?)
            None
        )