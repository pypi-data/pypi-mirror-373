from selenium.common.exceptions import NoSuchElementException
from webdriverwrapper import Chrome as _Chrome


class ChromeBrowser(_Chrome):
    def get_error_page(self):
        # Django error page.
        try:
            error_page = self.get_elm('summary')
        except NoSuchElementException:
            pass
        else:
            header = error_page.get_elm(tag_name='h1')
            return header.text

        # Generic error page.
        try:
            error_page = self.get_elm('error-page')
        except NoSuchElementException:
            pass
        else:
            header = error_page.get_elm(tag_name='h1')
            return header.text

    def get_error_traceback(self):
        try:
            traceback = self.get_elm('traceback_area')
        except NoSuchElementException:
            pass
        else:
            return traceback.text

    def get_error_messages(self):
        try:
            error_elms = self.get_elms(xpath='//*[contains(@class, "alert-danger")]')
        except NoSuchElementException:
            return []
        else:
            return [error_elm.text for error_elm in error_elms]

    def get_info_messages(self):
        try:
            info_elms = self.get_elms(xpath='//*[contains(@class, "alert-success")]')
        except NoSuchElementException:
            return []
        else:
            return [info_elm.get_attribute('info') for info_elm in info_elms]
