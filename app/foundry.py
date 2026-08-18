from foundry_local_sdk import FoundryLocalManager
from app.config import config

_manager = None


def get_manager():
    """
    Singleton FoundryLocalManager döndürür.
    Program boyunca yalnızca bir kez oluşturulur.
    """

    global _manager

    if _manager is None:


        _manager = FoundryLocalManager(config)

    return _manager