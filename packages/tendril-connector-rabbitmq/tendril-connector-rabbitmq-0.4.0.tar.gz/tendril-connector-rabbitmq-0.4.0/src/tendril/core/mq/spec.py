

from dataclasses import dataclass

@dataclass
class MQConnectionSpec(object):
    routing: str = None
    exchange_name: str = None
    service_name: str = None
