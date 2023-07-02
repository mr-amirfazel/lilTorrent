from enum import Enum


class RequestTypes(Enum):
    CONNECTION = 'connection'
    QUOTE = 'quote'
    MEDIA = 'media'

class Request():
    def __init__(self, type, data=None):
        self.type = type
        self.data = data
