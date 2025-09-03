import logging
import os

from ..utils import config
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound

from ..models import ItemImage
from .abstract_images_service import AbstractImagesService

class ImagesService(AbstractImagesService):

    def __init__(self, s3_service):
        self.s3_service = s3_service

    def get_image_file_name(self, parent, payload) -> str:
        source_image_file_path = payload['file_path']
        return f'{parent.id}_{os.path.basename(source_image_file_path)}'

    def prepare(self, parent, payload):
        logging.getLogger('api').debug(f'ImagesService::prepare - adding image to item with id {parent.id}')
        source_image_file_path = payload['file_path']
        image_file_name = self.get_image_file_name(parent, payload)

        target_image_file_path = f'{config("STORAGE.TARGET.IMAGES_FOLDER_NAME")}/{image_file_name}'

        self.s3_service.copy_file(source_image_file_path, target_image_file_path)

    def update(self, parent, image_id, payload) -> ItemImage:
        logging.getLogger('api').debug(f'ImagesService::update - updating image {image_id} in item with id {parent.id}')

        try:
            item_image = parent.images.get(pk=image_id)
        except ObjectDoesNotExist:
            raise NotFound(f'ItemImage {image_id} does not exist for item {parent.id}.')

        src_image_file_path = payload['file_path']
        former_image_file_name = item_image.file_name

        for key, value in payload.items():
            setattr(item_image, key, value)

        if not src_image_file_path is None:
            image_file_name = self.get_image_file_name(parent, payload)
            target_folder_name = config("STORAGE.TARGET.IMAGES_FOLDER_NAME")
            if not former_image_file_name is None:
                former_image_file_path = f'{target_folder_name}/{former_image_file_name}'
                self.s3_service.delete_file(former_image_file_path)
            target_image_file_path = f'{target_folder_name}/{image_file_name}'
            self.s3_service.copy_file(src_image_file_path, target_image_file_path)
            item_image.file_name = image_file_name

        item_image.save()
        return item_image

    def remove(self, parent, image_id):
        logging.getLogger('api').debug(f'ImagesService::remove - removing image {image_id} from item with id {parent.id}')

        try:
            item_image = parent.images.get(pk=image_id)
            if not item_image.file_name is None:
                image_file_path = f'{config("STORAGE.TARGET.IMAGES_FOLDER_NAME")}/{item_image.file_name}'
                self.s3_service.delete_file(image_file_path)
            item_image.delete()
        except ObjectDoesNotExist:
            raise NotFound(f'ItemImage {image_id} does not exist for item {parent.id}.')