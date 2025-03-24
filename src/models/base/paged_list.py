import math
from typing import TypeVar, Generic

T = TypeVar('T')


class PagedList(Generic[T]):
    items: list[T]
    total_count: int
    current_page: int
    total_pages: int
    page_size: int

    def __init__(self, items: list[T], count: int, page_number: int, page_size: int):
        self.total_count = count
        self.page_size = page_size
        self.current_page = page_number
        self.total_pages = int(math.ceil(float(count) / page_size))
        self.items: list[T] = items

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()

    def empty(self) -> bool:
        return not self.items

    def has_previous(self) -> bool:
        return self.current_page > 1

    def has_next(self) -> bool:
        return self.current_page < self.total_pages
