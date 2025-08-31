class PageDefinition:
    def __init__(self, path, page, page_group, dependency_group):
        self._path = path
        self._page = page
        self._page_group = page_group
        self._dependency_group = dependency_group

    @property
    def path(self):
        return self._path

    @property
    def page(self):
        return self._page

    @property
    def page_group(self):
        return self._page_group

    @property
    def dependency_group(self):
        return self._dependency_group

