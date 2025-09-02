from yta_constants.image import COLOR_TEMPERATURE_CHANGE_LIMIT, BRIGHTNESS_LIMIT, CONTRAST_LIMIT, SHARPNESS_LIMIT, WHITE_BALANCE_LIMIT, SPEED_FACTOR_LIMIT
from yta_constants.enum import YTAEnum as Enum


MAX_TIMELINE_LAYER_DURATION = 1200
"""
The maximum duration, in seconds, that a
timeline layer can have according to all
the subclips on it. This value can change
to allow longer timeline layers.
"""
VOLUME_LIMIT = (0, 300)
"""
The limit of the volumen adjustment. Zero (0) means
silence, 100 means the original audio volume and
300 means 3 times higher volume.
"""
ZOOM_LIMIT = (1, 500)
"""
The limit of the zoom adjustment. One (1) means a
zoom out until the video is a 1% of its original 
size, 100 means the original size and 500 means a
zoom in to reach 5 times the original video size.
"""
ROTATION_LIMIT = (-360, 360)
"""
The limit of the rotation adjustment. Zero (0) 
means no rotation, while 90 means rotated 90 
degrees to the left, 180 means flipped vertically
and 360 means no rotation.
"""
COLOR_TEMPERATURE_LIMIT = COLOR_TEMPERATURE_CHANGE_LIMIT
"""
The limit of the color temperature adjustment. Zero
(0) means no change, while -50 means...

TODO: Fulfill this as it depends on another const
"""
BRIGHTNESS_LIMIT = BRIGHTNESS_LIMIT
"""
The limit of the image brightness adjustment.
"""
CONTRAST_LIMIT = CONTRAST_LIMIT
"""
The limit of the image contrast adjustment.
"""
SHARPNESS_LIMIT = SHARPNESS_LIMIT
"""
The limit of the image sharpness adjustment.
"""
WHITE_BALANCE_LIMIT = WHITE_BALANCE_LIMIT
"""
The limit of the image white balance adjustment.
"""
SPEED_FACTOR_LIMIT = SPEED_FACTOR_LIMIT
"""
The limit of the speed factor adjustment.
"""

class VideoCombinatorAudioMode(Enum):
    """
    The mode in which the audio of the videos
    must be handled when combining them.
    """

    BOTH_CLIPS_AUDIO = 'both_clips_audio'
    """
    Both, the main clip and the added clip audios 
    are preserved.
    """
    ONLY_MAIN_CLIP_AUDIO = 'only_main_clip_audio'
    """
    Only the main clip audio is preserved. The one
    from the added clip is not included.
    """
    ONLY_ADDED_CLIP_AUDIO = 'only_added_clip_audio'
    """
    Only the added clip audio is preserved. The one
    from the main clip is not included.
    """

class ExtendVideoMode(Enum):
    """
    The strategy to follow when extending 
    the duration of a video.
    """

    LOOP = 'loop'
    """
    The video will loop (restart from the
    begining) until it reaches the 
    expected duration.
    """
    FREEZE_LAST_FRAME = 'freeze_last_frame'
    """
    Freeze the last frame of the video and
    repeat it until it reaches the 
    expected duration.
    """
    SLOW_DOWN = 'slow_down'
    """
    Change the speed of the video by
    deccelerating it until it reaches the
    expected duration.

    This mode changes the whole video
    duration so the result could be
    unexpected. Use it carefully.
    """
    BLACK_TRANSPARENT_BACKGROUND = 'black_background'
    """
    Add a black and transparent background
    clip the rest of the time needed to
    fulfil the required duration. This is
    useful when we need to composite
    different clips with different 
    durations so we can force all of them
    to have the same.
    """

class EnshortVideoMode(Enum):
    """
    The strategy to follow when enshorting 
    the duration of a video.
    """
    
    CROP = 'crop'
    """
    Remove the last part of the clip until
    it fits the expected duration.
    """
    SPEED_UP = 'speed_up'
    """
    Speed the video up to fit the expected
    duration. Good option for transitions.

    This mode changes the whole video
    duration so the result could be
    unexpected. Use it carefully.
    """

class MoviepyFrameMaskingMethod(Enum):
    """
    The method to be used when transforming
    a moviepy normal video frame into a
    moviepy mask video frame.
    """

    MEAN = 'mean'
    """
    Calculate the mean value of the RGB pixel color
    values and use it as a normalized value between
    0.0 and 1.0 to set as the transparency.
    """
    PURE_BLACK_AND_WHITE = 'pure_black_and_white'
    """
    Apply a threshold and turn pixels into pure black
    and white pixels, setting them to pure 1.0 or 0.0
    values to be completely transparent or opaque.
    """

    # We don't want functionality here to
    # to avoid dependencies.
    # def to_mask_frame(
    #     self,
    #     frame: np.ndarray
    # ):
    #     """
    #     Process the provided video normal 'frame'
    #     according to this type of masking
    #     processing method and turns it into a frame
    #     that can be used as a mask frame.
    #     """
    #     frame = ImageParser.to_numpy(frame)

    #     if not MoviepyVideoFrameHandler.is_normal_frame(frame):
    #         raise Exception('The provided "frame" is not actually a moviepy normal video frame.')

    #     return {
    #         FrameMaskingMethod.MEAN: np.mean(frame, axis = -1) / 255.0,
    #         FrameMaskingMethod.PURE_BLACK_AND_WHITE: pure_black_and_white_image_to_moviepy_mask_numpy_array(frame_to_pure_black_and_white_image(frame))
    #     }[self]

class ResizeMode(Enum):
    """
    The strategies we can apply when
    resizing a video.
    """

    RESIZE_KEEPING_ASPECT_RATIO = 'resize_keeping_aspect_ratio'
    """
    Resize the video to fit the expected
    larger size by keeping the aspect
    ratio, that means that a part of the
    video can be lost because of cropping
    it.
    """
    RESIZE = 'resize'
    """
    Resize the video to fit the expected
    larger size by keeping not the aspect
    ratio, so the whole video will be
    visible but maybe not properly. Use
    another option if possible.
    """
    FIT_LIMITING_DIMENSION = 'fit_limiting_dimension'
    """
    Resize the video to fit the most
    limiting dimension and it is placed
    over a black background of the
    expected size.
    """
    BACKGROUND = 'background'
    """
    The video is just placed over a black
    background clip, in the center. The
    background has the expected dimensions.
    This will work exactly as the
    FIT_LIMITING_DIMENSION if the video
    provided is larger than the expected
    size.
    """

class FrameExtractionType(Enum):
    """
    The strategy we want to apply when
    extracting frames from videos.
    """

    FRAME_TIME_MOMENT = 'frame_time_moment'
    """
    Use the frame time moments, which
    are the moments in which the frames
    are being displayed according to the
    video duration and fps.
    """
    FRAME_INDEX = 'frame_index'
    """
    Use the frame indexes, which are the
    position of each frame in the video.
    """


class FfmpegAudioCodec(Enum):
    """
    TODO: Fill this

    Should be used in the "**-c:a {codec}**" flag.
    """

    AAC = 'aac'
    """
    Default encoder.
    """
    AC3 = 'ac3'
    """
    More info: https://www.ffmpeg.org/ffmpeg-codecs.html#toc-ac3-and-ac3_005ffixed
    """
    AC3_FIXED = 'ac3_fixed'
    """
    More info: https://www.ffmpeg.org/ffmpeg-codecs.html#toc-ac3-and-ac3_005ffixed
    """
    FLAC = 'flac'
    """
    FLAC (Free Lossless Audio Codec) Encoder.

    More info: https://www.ffmpeg.org/ffmpeg-codecs.html#toc-flac-2
    """
    OPUS = 'opus'
    """
    This is a native FFmpeg encoder for the Opus format. Currently, it's
    in development and only implements the CELT part of the codec. Its
    quality is usually worse and at best is equal to the libopus encoder.

    More info: https://www.ffmpeg.org/ffmpeg-codecs.html#toc-opus
    """
    LIBFDK_AAC = 'libfdk_aac'
    """
    libfdk-aac AAC (Advanced Audio Coding) encoder wrapper. The libfdk-aac
    library is based on the Fraunhofer FDK AAC code from the Android project.

    More info: https://www.ffmpeg.org/ffmpeg-codecs.html#toc-libfdk_005faac
    """
    LIBLC3 = 'liblc3'
    """
    liblc3 LC3 (Low Complexity Communication Codec) encoder wrapper.
    
    More info: https://www.ffmpeg.org/ffmpeg-codecs.html#toc-liblc3
    """
    LIBMP3LAME = 'libmp3lame'
    """
    LAME (Lame Ain't an MP3 Encoder) MP3 encoder wrapper.

    More info: https://www.ffmpeg.org/ffmpeg-codecs.html#toc-libmp3lame-1
    """
    LIBOPENCORE_AMRNB = 'libopencore_amrnb'
    """
    OpenCORE Adaptive Multi-Rate Narrowband encoder.
    
    More info: https://www.ffmpeg.org/ffmpeg-codecs.html#toc-libopencore_002damrnb-1ss
    """
    LIBOPUS = 'libopus'
    """
    libopus Opus Interactive Audio Codec encoder wrapper.
    
    More info: https://www.ffmpeg.org/ffmpeg-codecs.html#toc-libopus-1
    """
    LIBSHINE = 'libshine'
    """
    Shine Fixed-Point MP3 encoder wrapper.
    
    More info: https://www.ffmpeg.org/ffmpeg-codecs.html#toc-libshine-1
    """
    LIBTWOLAME = 'libtwolame'
    """
    TwoLAME MP2 encoder wrapper.
    
    More info: https://www.ffmpeg.org/ffmpeg-codecs.html#toc-libtwolame
    """
    LIBVO_AMRWBENC = 'libvo-amrwbenc'
    """
    VisualOn Adaptive Multi-Rate Wideband encoder.
    
    More info: https://www.ffmpeg.org/ffmpeg-codecs.html#toc-libvo_002damrwbenc
    """
    LIBVORBIS = 'libvorbis'
    """
    libvorbis encoder wrapper.
    
    More info: https://www.ffmpeg.org/ffmpeg-codecs.html#toc-libvorbis
    """
    MJPEG = 'mjpeg'
    """
    Motion JPEG encoder.

    More info: https://www.ffmpeg.org/ffmpeg-codecs.html#toc-mjpeg
    """
    WAVPACK = 'wavpack'
    """
    WavPack lossless audio encoder.
    
    More info: https://www.ffmpeg.org/ffmpeg-codecs.html#toc-wavpack
    """
    COPY = 'copy'
    """
    Indicates that the codec must be copied from 
    the input.
    """

class FfmpegVideoCodec(Enum):
    """
    These are the video codecs available as Enums. The amount of codecs
    available depends on the ffmpeg built version.
    
    Should be used in the "**-c:v {codec}**" flag.
    """

    A64_MULTI = 'a64_multi'
    """
    A64 / Commodore 64 multicolor charset encoder. a64_multi5 is extended with 5th color (colram).

    More info:
    https://www.ffmpeg.org/ffmpeg-codecs.html#toc-a64_005fmulti_002c-a64_005fmulti5
    """
    A64_MULTI5 = 'a64_multi5'
    """
    A64 / Commodore 64 multicolor charset encoder. a64_multi5 is extended with 5th color (colram).

    More info:
    https://www.ffmpeg.org/ffmpeg-codecs.html#toc-a64_005fmulti_002c-a64_005fmulti5
    """
    CINEPAK = 'Cinepak'
    """
    Cinepak aka CVID encoder. Compatible with Windows 3.1 and vintage MacOS.
    
    More info:
    https://www.ffmpeg.org/ffmpeg-codecs.html#toc-Cinepak
    """
    GIF = 'GIF'
    """
    GIF image/animation encoder.

    More info:
    https://www.ffmpeg.org/ffmpeg-codecs.html#toc-Cinepak
    """
    HAP = 'Hap'
    """
    Vidvox Hap video encoder.

    More info:
    https://www.ffmpeg.org/ffmpeg-codecs.html#toc-Hap
    """
    JPEG2000 = 'jpeg2000'
    """
    The native jpeg 2000 encoder is lossy by default

    More info:
    https://www.ffmpeg.org/ffmpeg-codecs.html#toc-jpeg2000
    """
    LIBX264 = 'libx264'
    """
    x264 H.264/MPEG-4 AVC encoder wrapper.

    More info:
    https://www.ffmpeg.org/ffmpeg-codecs.html#libx264_002c-libx264rgb
    """
    MJPEG = 'mjpeg'
    """
    Motion JPEG encoder.

    More info:
    https://www.ffmpeg.org/ffmpeg-codecs.html#mjpeg
    """
    LIBRAV1E = 'librav1e'
    """
    rav1e AV1 encoder wrapper.

    More info:
    https://www.ffmpeg.org/ffmpeg-codecs.html#toc-librav1e
    """
    LIBAOM_AV1 = 'libaom-av1'
    """
    libaom AV1 encoder wrapper.
    
    More info:
    https://www.ffmpeg.org/ffmpeg-codecs.html#toc-libaom_002dav1
    """
    # TODO: Continue with this (https://www.ffmpeg.org/ffmpeg-codecs.html#toc-libsvtav1)
    QTRLE = 'qtrle'
    """
    TODO: Find information about this video codec.

    More info: ???
    """
    PRORES = 'prores'
    """
    Apple ProRes encoder.

    More info:
    https://www.ffmpeg.org/ffmpeg-codecs.html#toc-ProRes
    """
    COPY = 'copy'
    """
    Indicates that the codec must be copied from 
    the input.
    """

class FfmpegVideoFormat(Enum):
    """
    Enum list to simplify the way we choose a video format for
    the ffmpeg command. This should be used with the FfmpegFlag
    '-f' flag that forces that video format.

    Should be used in the "**-f {format}**" flag.
    """

    CONCAT = 'concat'
    """
    The format will be the concatenation.
    """
    AVI = 'avi'
    """
    Avi format.

    # TODO: Explain more
    """
    PNG = 'png'
    """
    # TODO: Look for mor information about this vcodec
    # TODO: I don't know if this one is actually an FfmpegVideoFormat
    # or if I need to create another Enum class. This option us used
    # in the '-vcodec' option, and the other ones are used in the
    # 'c:v' option.
    """
    # TODO: Keep going

class FfmpegFilter(Enum):
    """
    Enum list to simplify the way we use a filter for the
    ffmpeg command.

    Should be used in the "**-filter {filter}**" flag.
    """

    THUMBNAIL = 'thumbnail'
    """
    Chooses the most representative frame of the video to be used
    as a thumbnail.
    """

class FfmpegPixelFormat(Enum):
    """
    Enum list to simplify the way we use a pixel format for
    the ffmpeg command.

    Should be used in the "**-pix_fmt {format}**" flag.
    """
    
    YUV420p = 'yuv420p'
    """
    This is de default value. TODO: Look for more information about it
    """
    RGB24 = 'rgb24'
    """
    TODO: Look for more information about this pixel format.
    """
    ARGB = 'argb'
    """
    TODO: Look for more information about this pixel format
    """
    YUVA444P10LE = 'yuva444p10le'
    """
    TODO: Look for more information about this pixel format
    """
