import os
import shutil

from fild_cfg import Cfg
from PIL import Image, ImageDraw
from waiting import wait

from fild_ui import folder


class CompareBase:
    def __init__(self, test_name):
        self.file_name = test_name

        self.failed_screenshot = folder.generate_file_path(
            'screenshots/failed', self.file_name
        )
        self.threshold_screenshot = folder.generate_file_path(
            'screenshots/threshold', self.file_name
        )

    def base_compare(self, expected, actual):
        expected_img = Image.open(expected)
        actual_img = Image.open(actual)

        screen_width, screen_height = actual_img.size
        failed_pixels = []

        for y in range(1, screen_height + 1):
            for x in range(1, screen_width + 1):
                region_actual = self.process_pixel(actual_img, x, y)
                region_expected = self.process_pixel(expected_img, x, y)

                if region_expected != region_actual:
                    failed_pixels.append((x, y))

        mismatch = (len(failed_pixels) / (screen_width * screen_height)) * 100

        if mismatch:
            print(f'Mismatch Percentage is: {mismatch}')
            draw = ImageDraw.Draw(actual_img)

            for pixel in failed_pixels:
                draw.rectangle([pixel, pixel], outline='red')

        if mismatch > Cfg.Screenshot.threshold:
            actual_img.save(self.failed_screenshot)
        if 0 < mismatch <= Cfg.Screenshot.threshold:
            actual_img.save(self.threshold_screenshot)

        return mismatch

    @staticmethod
    def process_pixel(image, x, y):
        """
        This can be used as the sensitivity factor,
        the larger it is the less sensitive the comparison
        """
        factor = 10

        try:
            pixel = image.getpixel((x, y))
            region_total = sum(pixel)/4
        except:  # pylint: disable=bare-except
            return None

        return region_total/factor


class Screenshot(CompareBase):
    def __init__(self, target, test_name):
        super().__init__(test_name=test_name)

        self.target = target

        self.expected_folder = test_name.split('.')[1].rstrip('_extra').rstrip(
            '_reports'
        )
        self.expected_file = '.'.join(test_name.split('.')[2:])

        self.actual_screenshot = folder.generate_file_path(
            'screenshots/actual', self.file_name
        )
        self.expected_screenshot = folder.generate_file_path(
            f'qa/screenshots/{self.expected_folder}', self.expected_file
        )

    def take(self):
        self.target.save_screenshot(self.actual_screenshot)
        self.target.get_screenshot_as_png()

    def generate_expected(self):
        self.target.save_screenshot(self.expected_screenshot)
        self.target.get_screenshot_as_png()

    def compare(self):
        try:
            Image.open(self.expected_screenshot)
        except FileNotFoundError as e:
            self.generate_expected()
            raise FileNotFoundError('Expected screenshot is missing.') from e

        return self.base_compare(
            expected=self.expected_screenshot,
            actual=self.actual_screenshot
        )


class PageScreenshot:
    name = None
    completed = False
    save_mode = False

    @staticmethod
    def set_save_mode(save_mode=False):
        PageScreenshot.save_mode = save_mode

    @staticmethod
    def initialize(name):
        PageScreenshot.name = name
        PageScreenshot.completed = False

    @staticmethod
    def complete():
        PageScreenshot.name = None
        PageScreenshot.completed = True

    @classmethod
    def compare(cls, target):
        screenshot = Screenshot(target, cls.name)

        if cls.save_mode:
            screenshot.generate_expected()
            mismatch = 0
        else:
            screenshot.take()
            mismatch = screenshot.compare()

        cls.complete()

        assert mismatch < Cfg.Screenshot.threshold, 'Screenshots don\'t match'


class DownloadedImg:
    name = None
    save_mode = False

    @staticmethod
    def set_save_mode(save_mode=False):
        DownloadedImg.save_mode = save_mode

    @staticmethod
    def initialize(name):
        downloads_folder = folder.generate_path('downloads').absolute()
        shutil.rmtree(downloads_folder, ignore_errors=True)
        DownloadedImg.name = name

    @staticmethod
    def get_downloaded_file_with_wait():
        downloads_folder = folder.generate_path('downloads').absolute()

        def wait_for_png():
            files = os.listdir(downloads_folder)

            for file_name in files:
                if file_name.endswith('.png'):
                    return True

            return False

        wait(
            wait_for_png,
            timeout_seconds=4,
            waiting_for='file to download'
        )

        for filename in os.listdir(downloads_folder):
            return str(os.path.join(downloads_folder, filename))

        return None  # TODO check if exception needed

    @staticmethod
    def complete():
        DownloadedImg.name = None

    @classmethod
    def compare(cls):
        compare_base = CompareBase(cls.name)

        expected_folder = cls.name.split('.')[1].rstrip(
            '_extra'
        ).rstrip('_reports')
        expected_file = '.'.join(cls.name.split('.')[2:])

        expected_img = folder.generate_file_path(
            f'qa/screenshots/{expected_folder}/files', expected_file
        )
        actual_img = folder.generate_file_path(
            'screenshots/files', expected_file
        )

        if cls.save_mode:
            shutil.copy(
                cls.get_downloaded_file_with_wait(),
                expected_img
            )
            mismatch = 0
        else:
            mismatch = compare_base.base_compare(
                expected=expected_img,
                actual=cls.get_downloaded_file_with_wait()
            )
            # Saving file for publishing actual resul in case of failure
            shutil.copy(
                cls.get_downloaded_file_with_wait(),
                actual_img
            )

        cls.complete()

        assert mismatch < Cfg.Screenshot.threshold, 'Files don\'t match'
