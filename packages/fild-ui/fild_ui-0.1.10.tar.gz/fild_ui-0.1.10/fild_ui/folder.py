import os

from pathlib import Path
from datetime import datetime

from waiting import wait


def generate_path(folder_name):
    path = Path(folder_name)

    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except FileExistsError:
        # it's race condition
        pass

    return path


def generate_file_name(postfix='', extension='png'):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    return f'{timestamp}_{postfix}.{extension}'


def generate_file_path(folder_name, filename):
    path = generate_path(folder_name)

    return str(path / filename)


def get_downloaded_file_with_wait(extension=None):
    downloads_folder = generate_path('downloads').absolute()

    def wait_for_file():
        files = os.listdir(downloads_folder)

        for file_name in files:
            if extension is None or file_name.endswith(extension):
                return True

        return False

    wait(
        wait_for_file,
        timeout_seconds=2,
        waiting_for='file to download'
    )

    for filename in os.listdir(downloads_folder):
        return str(os.path.join(downloads_folder, filename))
