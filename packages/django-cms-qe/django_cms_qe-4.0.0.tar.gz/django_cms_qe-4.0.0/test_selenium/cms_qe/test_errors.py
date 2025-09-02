from webdriverwrapper.decorators import expected_error_page

from ..pages.cms import CreatePagePage


@expected_error_page(None)
def test_page_not_found(driver):
    driver.go_to('/404')


# No error page should be detected.
def test_page_not_found_custom_by_cms(driver):
    CreatePagePage(driver).open().create_page('Page not found', slug='error404')
    driver.go_to('/404')
