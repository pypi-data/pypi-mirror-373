class LoginPage:
    def __init__(self, driver):
        self._driver = driver

    def open(self):
        self._driver.go_to('/admin')
        return self

    def login(self, username, password=None):
        """
        Log in to Django CMS application as `username` with `password`.
        If `password` is empty, then is used same as `username`.
        """
        self._driver.get_elm('login-form').fill_out_and_submit({
            'username': username,
            'password': password or username,
        })
