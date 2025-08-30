from enum import Enum
import jsonlines
import os
from loguru import logger


class AttackFlavor(str, Enum):
    BON = "BON"
    PAIR = "PAIR"
    TAP = "TAP"
    ACTOR = "ACTOR"
    AUTODAN = "AUTODAN"


class BaseAttackManager:
    def __init__(self, res_save_path=None, delete_existing_res=False):
        if res_save_path:
            self.res_save_path = res_save_path
            logger.info(f"Results will be saved to '{res_save_path}'")
            res_dir = os.path.dirname(res_save_path)
            if os.path.exists(res_save_path):
                if os.path.isfile(res_save_path) and delete_existing_res:
                    logger.warning(f"The path '{res_save_path}' already exists. Deleting it.")
                    os.remove(res_save_path)
                else:
                    pass
            os.makedirs(res_dir, exist_ok=True)

    
    @classmethod
    def from_config(cls, config: dict):
        return cls(**config)

    def attack(self):
        pass