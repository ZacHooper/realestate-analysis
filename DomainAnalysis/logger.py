import logging

from requests.api import get

def get_logger(filepath = "scraper.log", filepath_level = logging.INFO, console_level = logging.DEBUG):
    mylogs = logging.getLogger(__name__)
    mylogs.setLevel(logging.DEBUG)

    file = logging.FileHandler(filepath)
    fileformat = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
    file.setLevel(filepath_level)
    file.setFormatter(fileformat)

    stream = logging.StreamHandler()
    streamformat = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
    stream.setLevel(console_level)
    stream.setFormatter(streamformat)

    mylogs.addHandler(file)
    mylogs.addHandler(stream)
    return mylogs

logger = get_logger()