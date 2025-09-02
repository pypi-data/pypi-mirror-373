def pytest_addoption(parser):
    parser.addoption('--no-display', action='store_true', help='do not use virtual display')


def pytest_configure(config):
    config.webdriverwrapper_screenshot_path = '/tmp/testresults'
