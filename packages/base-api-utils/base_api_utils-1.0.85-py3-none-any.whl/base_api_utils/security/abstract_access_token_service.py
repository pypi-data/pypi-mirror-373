from abc import abstractmethod


class AbstractAccessTokenService:

    def __init__(self):
        pass

    @abstractmethod
    def validate(self, access_token:str):
        pass
