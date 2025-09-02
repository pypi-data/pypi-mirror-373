from yta_constants.enum import YTAEnum as Enum


class ManimAnimationType(Enum):
    """
    Internal manim animation classifier to be able
    to handle the different video building processes
    in a better way and dynamically thanks to this
    enum.
    """

    GENERAL = 'general'
    """
    Manim animation which doesn't have an specific
    type by now, so it is classified as a general
    animation.
    """
    TEXT_ALPHA = 'text_alpha'
    """
    Manim animation which is text with a transparent 
    background, intented to be used as a main video
    overlay.
    """

class ManimRenderer(Enum):
    """
    The different rendeders manim has available.

    These are some tests I made with these renderers:
    - ImageMobject + Cairo works, but positioning gets crazy.
    - ImageMobject + Opengl fails
    - OpenGLImageMobject + Opengl works perfectly.
    - VideoMobject (ImageMobject) + Cairo works, but positioning gets crazy.
    - VideoMobject (ImageMobject) + Opengl fails
    - VideoMobject (OpenGLImageMobject) + Opengl only shows the first frame, but positioning is perfect.
    - Didn't test anything else
    """
    
    CAIRO = 'cairo'
    OPENGL = 'opengl'