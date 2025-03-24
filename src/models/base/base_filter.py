class BaseFilter:
    _max_page_size: int = 50
    _page_number: int = 1
    _page_size: int = 10

    def __init__(self):
        self._max_page_size = 50

    @property
    def page_size(self):
        return self._page_size

    @page_size.setter
    def page_size(self, page_size: int):
        self._page_size = page_size if page_size <= self._max_page_size else self._max_page_size

    @property
    def page_number(self):
        return self._page_number

    @page_number.setter
    def page_number(self, page_number: int):
        self._page_number = page_number

    @property
    def skip(self):
        return self._page_size * (self._page_number - 1)
