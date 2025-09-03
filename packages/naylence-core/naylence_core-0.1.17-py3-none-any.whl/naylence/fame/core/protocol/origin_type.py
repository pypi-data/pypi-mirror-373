from enum import Enum


class DeliveryOriginType(str, Enum):
    DOWNSTREAM = "downstream"
    UPSTREAM = "upstream"
    PEER = "peer"
    LOCAL = "local"
