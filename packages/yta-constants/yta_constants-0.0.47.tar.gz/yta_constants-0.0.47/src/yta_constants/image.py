"""
These settings are used by the ImageEditor. Maybe this file must
be renamed or moved to another path, but I keep this settings 
here because I need them in another file and to avoid cyclic
import issues.

TODO: Are this limits real? I mean, is there any limit to change
the temperature of an image or is this invented (?)
"""
COLOR_TEMPERATURE_CHANGE_LIMIT = (-50, 50)
COLOR_HUE_CHANGE_LIMIT = (-50, 50)
BRIGHTNESS_LIMIT = (-100, 100)
CONTRAST_LIMIT = (-100, 100)
SHARPNESS_LIMIT = (-100, 100)
WHITE_BALANCE_LIMIT = (-100, 100)
SPEED_FACTOR_LIMIT = (0.1, 10)