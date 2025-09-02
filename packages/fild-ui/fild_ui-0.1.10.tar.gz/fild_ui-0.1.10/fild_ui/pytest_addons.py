from pprint import pprint

from io import StringIO

from functools import wraps

import pytest

from fild_cfg import Cfg
from selenium.common.exceptions import WebDriverException

from fild_ui import folder
from fild_ui.browser import Browser
from fild_ui.screenshots import DownloadedImg, PageScreenshot


def is_screenshot_marked(item):
    for marker in item.own_markers:
        if marker.name == 'screenshot':
            return True

    return False


def save_screenshot_on_failure(outcome, item):

    report = outcome.get_result()

    if report.failed and Browser().is_open and not is_screenshot_marked(item):
        test_name = item.name

        if report.when == 'setup':
            test_name = f'setup_for_{test_name}'
        elif report.when != 'call':
            return

        file_name = folder.generate_file_name(test_name)
        file_path = folder.generate_file_path('screenshots', file_name)
        try:
            Browser().driver.save_screenshot(file_path)
        except WebDriverException:
            pass


def compare_screenshot(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if Cfg.Screenshot.compare:
            PageScreenshot.initialize(f'{func.__module__}.{func.__name__}.png')

        func(*args, **kwargs)

        if Cfg.Screenshot.compare and not PageScreenshot.completed:
            PageScreenshot.compare(Browser().driver)

    return pytest.mark.screenshot(wrapped)


def compare_downloaded_img(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if Cfg.Screenshot.compare:
            DownloadedImg.initialize(f'{func.__module__}.{func.__name__}.png')

        func(*args, **kwargs)

        if Cfg.Screenshot.compare:
            DownloadedImg.compare()

    return pytest.mark.screenshot(wrapped)


def get_console_errors():
    exclude = Cfg.Browser.get('exclude_logs_from') or []

    def is_excluded(log_item):
        for exclude_item in exclude:
            if exclude_item in log_item['message']:
                return True

        return False

    error_log = Browser().console_log

    return [log_item for log_item in error_log if not is_excluded(log_item)]


def check_console_errors(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        func(*args, **kwargs)
        error_log = get_console_errors()
        printed_log = StringIO()
        pprint(error_log, printed_log)
        assert not error_log, f'Console log errors.\n{printed_log.getvalue()}'

    return pytest.mark.extended(wrapped)
