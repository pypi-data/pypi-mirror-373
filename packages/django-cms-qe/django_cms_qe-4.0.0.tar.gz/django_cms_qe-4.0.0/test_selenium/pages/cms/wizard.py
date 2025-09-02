class WizardPage:
    def __init__(self, driver):
        self._driver = driver

    def open(self):
        self._driver.go_to('/cms_wizard/create/?language=en')
        return self

    def create_home_page(self):
        """
        Creates empty homepage for Django CMS. Usuful to create some
        at the beggining of tests so any test can start somewhere.
        """
        self._driver.get_elm(tag_name='form').submit()
        self._driver.get_elm(tag_name='form').fill_out_and_submit({
            '1-title': 'homepage',
        })
