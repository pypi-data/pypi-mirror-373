from selenium.common.exceptions import (
    ElementClickInterceptedException, StaleElementReferenceException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select as BaseSelect
from waiting import wait

from fild_ui.browser import Browser, Element, Elements


class Container(Element):
    pass


class Button(Element):
    @property
    def text(self):
        return self.located.text

    def click(self):
        self._target = None
        self.scroll_to()
        self.located.click()
        Browser().recreate_session()

        return True  # for sync in waits

    def click_once_loaded(self):
        return wait(
            self.click,
            timeout_seconds=2,
            sleep_seconds=0,
            expected_exceptions=(ElementClickInterceptedException,),
            waiting_for='clicking button once loaded'
        )

    def click_and_switch_to_new_window(self):
        windows = Browser().driver.window_handles
        self.click()
        wait(
            lambda: len(Browser().driver.window_handles) > len(windows),
            timeout_seconds=2,
            waiting_for='new window to open'
        )
        Browser().driver.switch_to.window(
            Browser().driver.window_handles[len(windows)]
        )

    @property
    def is_disabled(self):
        return bool(self.get_attribute('disabled'))

    def verify_text(self, expected):
        actual = self.text
        assert actual == expected, (
            f'Unexpected menu text.\nExpected: {expected}\nActual: {actual}'
        )

    def wait_for_text(self, expected_text, timeout_seconds=2):
        wait(
            lambda: expected_text == self.text,
            sleep_seconds=0,
            timeout_seconds=timeout_seconds,
            waiting_for=f'button text to equal {expected_text}'
        )


class Link(Button):
    @property
    def url(self):
        return self.located.get_attribute('href')


class TextInput(Element):
    def input(self, value):
        self.wait_for_load()

        self.located.click()
        self.located.clear()
        self.located.send_keys(value)

    def safe_input(self, value):
        self.wait_for_load()
        self.located.click()
        action = ActionChains(Browser().driver)
        action.send_keys(value)
        action.perform()

    def clear_and_type(self, value):
        self.wait_for_load()
        self.located.clear()
        self.safe_input(value)

    def get_value(self):
        self.wait_for_load()
        return self.located.get_attribute('value')

    def set_value(self, value):
        self.wait_for_load()
        Browser().driver.execute_script(
            'arguments[0].value = arguments[1]',
            self.located,
            value
        )

    def verify_value(self, expected):
        actual = self.get_value()
        assert actual == str(expected), (
            f'Unexpected input value.\nExpected: {expected}\nGot: {actual}'
        )


class Label(Element):
    @property
    def text(self):
        return self.located.text

    @property
    def is_displayed(self):
        return self.located.is_displayed

    def wait_for_updated(self, timeout=1):
        initial_text = self.located.text

        def _waiter():
            self.wait_for_load()
            return self.located.text != initial_text

        wait(_waiter, timeout_seconds=timeout)

    def wait_for_text(self, value, timeout=1):
        def _waiter():
            try:
                self.wait_for_load()
                return self.located.text == str(value)
            except StaleElementReferenceException:
                self.invalidate()
                return False

        wait(
            _waiter,
            timeout_seconds=timeout,
            waiting_for=f'waiting for text {value}'
        )

    def verify_label_text(self, text):
        self.wait_for_load()
        text = str(text)
        actual = self.located.text
        assert actual == text, (
            f'Unexpected label text.\nExpected: {text}\nGot: {actual}'
        )


class Select(Element):
    @property
    def located(self):
        return BaseSelect(super().located)

    def wait_for_value(self):
        def wait_for_options():
            self._target = None
            return self.located.options

        wait(
            wait_for_options,
            timeout_seconds=5,
            waiting_for='selected option to appear'
        )

    def select(self, value=None, index=None, text=None):
        if value is not None:
            self.located.select_by_value(value)
        elif index is not None:
            self.located.select_by_index(index)
        elif text is not None:
            self.located.select_by_visible_text(text)
        else:
            raise ValueError('provide value for select')

    @property
    def all_options(self):
        return [opt.text for opt in self.located.options]

    @property
    def selected_option(self):
        return self.located.first_selected_option.text

    def verify_selected_option(self, text):
        actual = self.selected_option
        assert actual == str(text), (
            f'Unexpected selected option.\nExpected: {text}\nGot: {actual}'
        )


class Checkbox(Button):
    @property
    def checked(self):
        return self.located.is_selected()

    def verify_checked(self, expected):
        actual = self.checked
        assert actual == expected, f'Expected checkbox to be: {expected}'


class TableRow(Container):
    Columns = Elements(css='td', element_class=Label)


class Table(Container):
    Head = Elements(css='th', element_class=Label)
    Rows = Elements(css='tbody tr', element_class=TableRow)

    def read_data(self):
        Browser().recreate_session()
        headers = [col.text for col in self.Head]
        data = [[col.text for col in row.Columns] for row in self.Rows]

        return headers, data
