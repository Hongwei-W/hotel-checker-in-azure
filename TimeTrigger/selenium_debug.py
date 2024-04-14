class SeleniumDebug:
    def __init__(self, driver):
        self.driver = driver

    def save_screenshot(self, filename):
        self.driver.save_screenshot(filename)

    def save_page_source(self, filename):
        with open(filename, 'w') as f:
            f.write(self.driver.page_source)

    def save_cookies(self, filename):
        with open(filename, 'w') as f:
            f.write(json.dumps(self.driver.get_cookies()))

    def save_html(self, filename):
        with open(filename, 'w') as f:
            f.write(self.driver.execute_script("return document.documentElement.outerHTML"))

class SeleniumWithAzureBlob(SeleniumDebug):
    def __init__(self, driver, blob_service_client, container_name):
        super().__init__(driver)
        self.blob_service_client = blob_service_client
        self.container_name = container_name

    def save_screenshot(self, filename):
        super().save_screenshot(filename)
        self.__upload_to_blob(filename)

    def save_page_source(self, filename):
        super().save_page_source(filename)
        self.__upload_to_blob(filename)

    def save_cookies(self, filename):
        super().save_cookies(filename)
        self.__upload_to_blob(filename)

    def save_html(self, filename):
        super().save_html(filename)
        self.__upload_to_blob(filename)

    def __upload_to_blob(self, filename):
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=filename)
        with open(filename, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)