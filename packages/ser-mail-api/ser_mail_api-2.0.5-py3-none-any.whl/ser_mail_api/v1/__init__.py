"""
Author: Ludvik Jerabek
Package: ser-mail-api
License: MIT
"""
from .client import Client
from .data import *
from .common import *

__all__ = ['Client', 'Region', 'Attachment', 'Disposition', 'Content', 'ContentType', 'MailUser', 'Message', 'MessageHeaders']