from abc import abstractmethod

from .our_object import OurObject

ENTITY_NAME = "item"


class Item(OurObject):
    def __init__(self, **kwargs):
        super().__init__(ENTITY_NAME, **kwargs)

    @abstractmethod
    def get_id(self):
        raise NotImplementedError("Subclasses must implement the 'get_id' method.")
