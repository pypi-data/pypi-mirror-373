class CreatePagePage:
    def __init__(self, driver):
        self._driver = driver

    def open(self):
        self._driver.go_to('/admin/cms/page/add/')
        return self

    def create_page(self, title, slug=''):
        # Title will automatically set slug which we want to force.
        self._driver.get_elm(tag_name='form').fill_out({
            'title': title,
        })
        self._driver.get_elm(tag_name='form').fill_out_and_submit({
            'slug': slug,
        })
