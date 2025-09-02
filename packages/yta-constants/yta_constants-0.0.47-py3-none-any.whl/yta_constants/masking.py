from yta_constants.enum import YTAEnum as Enum


GREENSCREEN_RGB_COLOR = (0, 249, 12)
"""
The RGB color we use to generate greenscreens.
"""

class GreenscreenType(Enum):
    """
    The type of greenscreen we are handling.
    """
    
    VIDEO = 'video'
    """
    Video that includes at least one greenscreen
    in at least one of its frames.
    """
    IMAGE = 'image'

class AlphascreenType(Enum):
    """
    The type of alphascreen we are handling. An
    alphascreen is an image or a video with at
    least one area in which we have transparency,
    so we can place something behind that will be
    visible through that alpha channel.
    """
    
    VIDEO = 'video'
    """
    Video that includes at least one alphascreen
    in at least one of its frames.
    """
    IMAGE = 'image'
