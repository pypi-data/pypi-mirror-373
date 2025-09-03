from dataclasses import dataclass

from naylence.fame.core.channel.channel import Channel
from naylence.fame.core.address.address import FameAddress


@dataclass
class Subscription:
    channel: Channel
    address: FameAddress
