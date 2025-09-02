from yta_constants.enum import YTAEnum as Enum


class TextFinderOption(Enum):
    """
    This is an option that can be applied to modify the
    way we will look for some terms in the given text
    to find any coincidences.
    """

    IGNORE_CASE = 'ignore_case'
    """
    The term found must match teh text, ignoring the 
    cases. This means that if looking for the term
    'Text', any option like 'text', 'TExT', 'texT',
    etc. will be accepted as a match.
    """
    IGNORE_ACCENTS = 'ignore_accents'
    """
    The term found must match the text ignoring the
    accents. This means that if looking for the term
    'pasó', any option like 'pasó', 'paso', pàso', 
    etc. will be accepted as a match.
    """