"""
Author: Ludvik Jerabek
Package: ser-mail-api
License: MIT
"""
from enum import Enum


class Region(Enum):
    US = 'mail-us.ser.proofpoint.com'
    EU = 'mail-eu.ser.proofpoint.com'
    AU = 'mail-aus.ser.proofpoint.com'
