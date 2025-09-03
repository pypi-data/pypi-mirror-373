from dataclasses import dataclass

from naylence.fame.core.channel.channel import ReadWriteChannel
from naylence.fame.core.address.address import FameAddress


@dataclass
class Binding:
    channel: ReadWriteChannel
    address: FameAddress  # FameAddress as string "<name>@<path>"
