from yta_constants.enum import YTAEnum as Enum


class TimelineTrackType(Enum):
    """
    The type of a timeline track, which will determine
    which kind of elements are accepted by the track
    with this type.
    """
    
    VIDEO = 'video'
    """
    The type of track that only accept video elements.
    """
    AUDIO = 'audio'
    """
    The type of track that only accept audio elements.
    """
    # TODO: Probably add 'GreenscreenTrack',
    # 'AlphascreenTrack', 'TextTrack', 'SubtitleTrack',
    # and all needed in a future when this concept 
    # evolves properly