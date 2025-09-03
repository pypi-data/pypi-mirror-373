from abc import abstractmethod

from ..models import ItemImage


class AbstractImagesService:

    @abstractmethod
    def prepare(self, parent, payload):
        pass

    @abstractmethod
    def update(self, parent, image_id, payload) -> ItemImage:
        pass

    @abstractmethod
    def remove(self, parent, image_id):
        pass