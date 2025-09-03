from abc import abstractmethod


class AbstractStorageService:

    @abstractmethod
    def copy_file(self, source_file_path, target_file_path):
        pass

    def delete_file(self, file_path):
        pass