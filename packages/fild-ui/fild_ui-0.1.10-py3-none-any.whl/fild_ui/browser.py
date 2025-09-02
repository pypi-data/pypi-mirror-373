import time
import waiting

from fild_compare import compare
from fild_cfg import Cfg
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common import action_chains
from selenium.common.exceptions import (
    ElementClickInterceptedException, StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver import Chrome, Remote
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from waiting import wait, TimeoutExpired

from fild_ui import folder
from fild_ui.screenshots import PageScreenshot
from fild_ui.singleton import Singleton


def retry_on_js_reload(function, refresh, timeout_seconds=2):
    result = None

    def action():
        try:
            nonlocal result
            result = function()
            return True
        except StaleElementReferenceException:
            refresh()
            return None
        except ElementClickInterceptedException:
            refresh()
            return None

    waiting.wait(
        action,
        timeout_seconds=timeout_seconds,
        waiting_for='the elements to load'
    )
    return result


class Browser(metaclass=Singleton):
    _driver = None
    _session_id = 0

    @property
    def driver(self):
        if self._driver is None:
            options = Options()

            options.add_argument('--allow-insecure-localhost')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--disable-web-security')
            options.add_argument('--hide-scrollbars')
            options.add_argument('--disable-site-isolation-trials')

            if Cfg.Browser.headless:
                options.add_argument('--headless=new')
                # fixing chrome issues
                options.add_experimental_option(
                    'excludeSwitches', ['enable-automation']
                )
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument('--remote-debugging-pipe')

            if Cfg.Browser.get('devtools'):
                options.add_argument('--auto-open-devtools-for-tabs')

            if Cfg.Browser.get('no_sandbox'):
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-setuid-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-infobars')
                options.add_argument('--disable-browser-side-navigation')

            options.add_experimental_option('prefs', {
                'download.default_directory':
                    str(folder.generate_path('downloads').absolute()),
                'pageLoadStrategy': 'none',
            })

            if Cfg.Browser.get('remote_url'):
                self._driver = Remote(
                    options=options, command_executor=Cfg.Browser.remote_url
                )
            else:
                self._driver = Chrome(options=options)

            self._driver.set_page_load_timeout(15)
            self._driver.set_window_size(1680, 1050)

        return self._driver

    def close(self):
        if self._driver is None:
            return

        self._driver.quit()
        self._driver = None

    @classmethod
    def recreate_session(cls):
        cls._session_id += 1

    @property
    def is_open(self):
        return self._driver is not None

    @property
    def session(self):
        return self._session_id

    @property
    def console_log(self):
        logs = self.driver.get_log('browser')
        severe_logs = [log for log in logs if log['level'] == 'SEVERE']

        return severe_logs


class Page:
    base_url = None
    url = None

    @classmethod
    def open(cls, *args, url_postfix=None):
        cls.open_page(*args, url_postfix=url_postfix)

    @classmethod
    def open_page(cls, *args, url_postfix=None):
        if cls.base_url is None and cls.url is None:
            raise NotImplementedError('Page url is not specified')

        url = f'{cls.base_url}/{(cls.url or "").format(*args)}{url_postfix or ""}'
        Browser().recreate_session()
        Browser().driver.get(url)

    @classmethod
    def scroll_to_bottom(cls):
        Browser().driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight);"
        )
        Browser().driver.execute_script(
             "document.querySelector('#root').scrollTo(0,document.body.scrollHeight);"
        )
        # TODO make it work w/o sleep
        time.sleep(0.5)

    @classmethod
    def get_current_url(cls):
        return Browser().driver.current_url

    @classmethod
    def wait_for_redirect(cls):
        waiting.wait(
            lambda: '?_=' in cls.get_current_url(),
            timeout_seconds=1,
            waiting_for='url to update'
        )

    @classmethod
    def wait_for_current_url(cls, url):
        waiting.wait(
            lambda: cls.get_current_url() == url,
            timeout_seconds=1,
            waiting_for='url to update'
        )

    @classmethod
    def is_open(cls, *args, url_postfix=None, skip_params=True):
        actual = cls.get_current_url()

        if skip_params:
            actual = actual.split('?')[0]

        page_url = (
            f'{cls.base_url}/{(cls.url or "").format(*args)}'
            f'{url_postfix or ""}'
        )

        return page_url == actual

    @classmethod
    def verify_current_url(cls, *args, url_postfix=None, skip_params=True):
        actual = cls.get_current_url()

        if skip_params:
            actual = actual.split('?')[0]

        expected = (
            f'{cls.base_url}/{(cls.url or "").format(*args)}'
            f'{url_postfix or ""}'
        )

        assert actual == expected, (
            f'Unexpected url.\nExpected: {expected}\nGot: {actual}'
        )

    @classmethod
    def go_back(cls):
        return Browser().driver.back()

    @staticmethod
    def press_key(key):
        action_chains.ActionChains(Browser().driver).send_keys(key).perform()

    @staticmethod
    def wait_for_window_closed(timeout=5):
        wait(
            lambda: len(Browser().driver.window_handles) == 1,
            timeout_seconds=timeout,
            waiting_for='extra windows to close'
        )

    @staticmethod
    def switch_to_default_window():
        Browser().driver.switch_to.window(
            Browser().driver.window_handles[0]
        )


class Element:
    _fixed_target = None
    _browser_session = None
    _parent = None
    _target = None

    _height = None
    _width = None

    def __init__(self, by_value=None, by=None, # pylint: disable=invalid-name
                 css=None, xpath=None, name=None):
        if css:
            by = By.CSS_SELECTOR
            by_value = css
        elif xpath:
            by = By.XPATH
            by_value = xpath
        elif name:
            by = By.NAME
            by_value = name

        self._fixed_target = None
        self.by = by or By.ID  # pylint: disable=invalid-name
        self.by_value = by_value

    def is_list_item_container(self):
        return self._fixed_target is not None

    @classmethod
    def set_located(cls, target):
        element = cls(by_value=None)
        element._fixed_target = target

        return element

    @property
    def parent(self):
        if self._parent is None:
            return Browser().driver

        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    def invalidate(self):
        self._target = None

        if self._parent:
            self._parent.invalidate()

    def check_browser_session(self):
        actual_session = Browser().session

        if self._browser_session != actual_session:
            self.invalidate()
            self._browser_session = actual_session

    def find_element(self, by, value):
        return self.located.find_element(by=by, value=value)

    def find_elements(self, by, value):
        return self.located.find_elements(by=by, value=value)

    @property
    def located(self):
        if self._fixed_target is not None:
            return self._fixed_target

        self.check_browser_session()

        if self._target is None:
            self._target = self.parent.find_element(
                by=self.by, value=self.by_value
            )

        return self._target

    def get_attribute(self, name):
        return self.located.get_attribute(name=name)

    def __get__(self, instance, owner):
        if instance and issubclass(owner, Element):
            if instance.is_list_item_container:
                Browser().recreate_session()

            self.parent = instance

        return self

    def __getattr__(self, item):
        if hasattr(self.__class__, item):
            return object.__getattribute__(self, item)

        return self.located.__getattribute__(item)

    @property
    def text(self):
        return self.located.text

    def wait_for_load(self, timeout_seconds=2):
        wait(lambda: self.is_present(timeout=1),
             timeout_seconds=timeout_seconds,
             waiting_for='item to be displayed')

    def wait_for_not_present(self, timeout_seconds=1):
        wait(lambda: self.is_present(timeout=0) is False,
             timeout_seconds=timeout_seconds,
             sleep_seconds=0,
             waiting_for='item to be not present')

    def is_not_present(self, timeout_seconds=1):
        try:
            wait(lambda: self.is_present(timeout=0) is False,
                 timeout_seconds=timeout_seconds,
                 waiting_for='item to be not displayed')
            return True
        except TimeoutExpired:
            return False

    def is_present(self, timeout=0):
        def wait_for_is_displayed():
            Browser().recreate_session()
            return self.located.is_displayed()

        Browser().driver.implicitly_wait(timeout)

        try:
            wait(wait_for_is_displayed, timeout_seconds=timeout)
            return True
        except WebDriverException:
            return False
        except TimeoutExpired:
            return False
        finally:
            Browser().driver.implicitly_wait(1)

    def scroll_to(self, timeout=1):
        self.wait_for_load()
        viewport_height = Browser().driver.get_window_size()['height']
        height = self.located.size['height']

        if self.located.location['y'] + height <= viewport_height:
            return

        wait(
            lambda: self.located.location_once_scrolled_into_view['y'] + height <= viewport_height,
            timeout_seconds=timeout,
            waiting_for='element to be scrolled into view'
        )

    def delete(self):
        self.wait_for_load()

        Browser().driver.execute_script(
            'arguments[0].parentNode.removeChild(arguments[0])',
            self.located
        )

    def save_screenshot(self, file_name):
        self.located.screenshot(filename=file_name)

    def get_screenshot_as_png(self):
        return self.located.screenshot_as_png

    def wait_for_size(self, height=None, width=None):
        def is_of_size():
            Browser().recreate_session()

            if height is not None:
                if self.located.size['height'] != height:
                    return False

            if width is not None:
                if self.located.size['width'] != width:
                    return False

            return True

        wait(
            is_of_size,
            sleep_seconds=0,
            timeout_seconds=2,
            waiting_for=(
                f'element to load to size {height}x{width}. '
                f'Latest was: {self.located.size}'
            )
        )

    def verify_by_screenshot(self):
        PageScreenshot.compare(self)

    def verify_displayed(self, height=None, width=None):
        self.scroll_to()
        self.wait_for_size(
            height=height or self._height,
            width=width or self._width
        )

        if Cfg.Screenshot.compare:
            self.verify_by_screenshot()
        else:
            assert self.located.is_displayed()

    def hover(self):
        self.wait_for_load()
        ActionChains(Browser().driver).move_to_element(self.located).perform()

        return True  # for syncronization in waits


class Elements(Element):
    def __init__(self, by_value=None, by=None, css=None, xpath=None,
                 element_class=None):
        super().__init__(by_value=by_value, by=by, css=css, xpath=xpath)
        self.element_class = element_class

    @property
    def located(self):
        self.check_browser_session()

        if self._target is None:
            self._target = self.parent.find_elements(
                by=self.by, value=self.by_value
            )

        if self.element_class:
            self._target = [self.element_class.set_located(element)
                            for element in self._target]

        return self._target

    def reload(self, parent):
        if self._parent:
            self._parent.invalidate()
            self._target = self.parent.find_elements(by=self.by, value=self.by_value)
        else:
            self._target = parent.find_elements(by=self.by, value=self.by_value)

        if self.element_class:
            self._target = [self.element_class.set_located(element)
                            for element in self._target]

    def is_present(self, timeout=0):
        Browser().driver.implicitly_wait(0)
        try:
            wait(self.located[0].is_displayed, timeout_seconds=timeout)
            return True
        except WebDriverException:
            return False
        except TimeoutExpired:
            return False
        except IndexError:
            return False
        finally:
            Browser().driver.implicitly_wait(1)

    def __len__(self):
        return len(self.located)

    def __getitem__(self, item):
        Browser().recreate_session()
        return self.located[item]  # Return Field to provide attribute access

    def __iter__(self):
        return iter(self.located)

    def get_by_attribute(self, **kwargs):
        name = next(iter(kwargs))
        value = kwargs[name]

        for element in self.located:
            if element.get_attribute(name) == value:
                return element

        return None

    def _get_by_text(self, text, strip=False):
        for element in self.located:
            current = element.text

            if strip:
                current = current.strip()

            if current == text:
                return element

        return None

    def get_by_text(self, text, strip=False):
        return retry_on_js_reload(
            function=lambda: self._get_by_text(text=text, strip=strip),
            refresh=Browser.recreate_session
        )

    def click_by_text(self, text, strip=False):
        retry_on_js_reload(
            function=lambda: self._get_by_text(text=text, strip=strip).click(),
            refresh=Browser.recreate_session
        )

    def wait_for_items_load(self, items_count, timeout_seconds=2):
        def check_count():
            if not items_count:
                Browser().driver.implicitly_wait(0)

            Browser().recreate_session()
            return len(self.located) == items_count

        try:
            wait(check_count,
                 timeout_seconds=timeout_seconds,
                 waiting_for=f'{items_count} items. Got: {len(self.located)}')
        finally:
            Browser().driver.implicitly_wait(1)

    def wait_for_some_items(self, timeout_seconds=2):
        def check_count():
            Browser().recreate_session()
            return len(self.located) != 0

        wait(check_count,
             timeout_seconds=timeout_seconds,
             waiting_for='some items to load')

    def get_labels(self):
        return retry_on_js_reload(
            function=lambda: [item.text for item in self.located],
            refresh=Browser.recreate_session
        )

    def get_not_empty_labels(self):
        return retry_on_js_reload(
            function=lambda: [item.text for item in self.located if item.text],
            refresh=Browser.recreate_session
        )

    def wait_for_labels(self, count, timeout_seconds=2):
        def check_count():
            Browser().recreate_session()
            labels = self.get_not_empty_labels()

            return labels and len(labels) == count

        wait(check_count,
             timeout_seconds=timeout_seconds,
             waiting_for='some items to load')

    def verify_labels(self, expected):
        compare(
            expected=expected,
            actual=self.get_labels(),
            target_name='elements labels'
        )
