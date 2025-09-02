"""
The constants we need when interacting with
the Google Drive service to download files
from shareable public links and handle the
errors.
"""

DRIVE_RESOURCE_URL = 'https://drive.google.com/file/d/'
"""
The start of the sharable url to be able to detect
it and obtain the id.
"""
DOWNLOAD_URL = 'https://docs.google.com/uc?export=download&confirm=1'
"""
The start of the sharable download url.
"""
CONFIRMATION_STRING = 'confirm=t'
"""
The confirmation string that allows Google Drive to
download a file surpassing a new virus scan check.
Check these links:
- https://github.com/ndrplz/google-drive-downloader/pull/30
- https://github.com/tensorflow/datasets/issues/3935#issuecomment-2067094366
"""
FILE_NOT_FOUND_ERROR_STRING = '<p class="errorMessage" style="padding-top: 50px">'
"""
A paragraph we can find when the id in the given
Google Drive shareable url is not valid but the
url is well-formatted.
"""