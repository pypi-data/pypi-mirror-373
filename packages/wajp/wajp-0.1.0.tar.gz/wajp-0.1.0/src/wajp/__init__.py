import os
import pathlib
import shutil
from typing import Union


def wipe_directory(directory_path: Union[str, pathlib.Path]):
    dir_path = str(directory_path)
    if not os.path.isdir(dir_path):
        return

    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)

        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)
