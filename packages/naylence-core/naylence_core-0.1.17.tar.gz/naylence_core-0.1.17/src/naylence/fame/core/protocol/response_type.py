import enum


class FameResponseType(enum.IntFlag):
    NONE = 0
    ACK = 1
    REPLY = 2
    STREAM = 4
