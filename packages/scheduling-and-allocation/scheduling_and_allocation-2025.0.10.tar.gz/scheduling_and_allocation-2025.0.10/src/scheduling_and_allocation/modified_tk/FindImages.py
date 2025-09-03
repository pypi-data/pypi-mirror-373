import re, platform
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
#from schedule.Presentation import dirty_flags


def get_image_dir():
    """Gets the image directory"""
    return os.path.join(dir_path, 'Images')


def get_logo(bin_dir):
    return os.path.join(bin_dir, 'schedule_logo.png')


def get_allocation_logo(bin_dir):
    return os.path.join(bin_dir, 'AllocationLogo.gif')
