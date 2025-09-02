import base64
import logging

from osbot_utils.utils.Dev import Dev

from osbot_utils.utils.Files import temp_file
from osbot_utils.utils.Misc import bytes_to_base64

logger_png = logging.getLogger()

def save_png_bytes_to_file(bytes, png_file=None):
    png_data = bytes_to_base64(bytes)
    return save_png_base64_to_file(png_data, png_file)

def save_png_base64_to_file(png_data, png_file=None):
    if png_data is not None:
        if type(png_data) is not str:
            logger_png.error(f'Png data was not a string: {png_data}')
        else:
            if png_file is None:
                png_file = temp_file('.png')
            try:
                with open(png_file, "wb") as fh:
                    fh.write(base64.decodebytes(png_data.encode()))
                logger_png.error(f'Png data with size {len(png_data)} saved to {png_file}')  # note: this is currently set to error because nothing else seems to be picked up by logging.getLogger().addHandler(logging.StreamHandler())
                return png_file
            except Exception as error:
                logger_png.error(f'png save error: {error}')
                logger_png.error(png_data)
