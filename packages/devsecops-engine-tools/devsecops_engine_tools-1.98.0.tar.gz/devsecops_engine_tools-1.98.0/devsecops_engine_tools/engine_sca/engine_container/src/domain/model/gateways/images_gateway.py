from abc import ABCMeta, abstractmethod


class ImagesGateway(metaclass=ABCMeta):
    @abstractmethod
    def list_images(self, image_to_scan) -> str:
        "get image to scan"

    @abstractmethod
    def get_base_image(self, image_to_scan, base_image_labels: list, label_keys: dict = None) -> str:
        "get base image"

    @abstractmethod
    def validate_base_image_date(self, image_to_scan, referenced_date, base_image_labels: list, label_keys: dict = None) -> str:
        "validate base image date"
    
    @abstractmethod
    def validate_black_list_base_image(self, base_image, black_list) -> str:
        "validate base image date"