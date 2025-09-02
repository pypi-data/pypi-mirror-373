from typing import Optional

from .Resource import Resource

class OnlineAccount:
    identifier = 'http://gedcomx.org/v1/OnlineAccount'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, serviceHomepage: Resource, accountName: str) -> None:
        pass