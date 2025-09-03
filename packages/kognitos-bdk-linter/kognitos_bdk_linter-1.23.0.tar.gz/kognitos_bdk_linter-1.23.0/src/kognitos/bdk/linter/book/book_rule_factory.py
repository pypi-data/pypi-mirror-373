from abc import ABC, abstractmethod
from typing import List

from .rules.book_rules import BookRule, DiscoverRule, TagsRule


class BookRuleFactory(ABC):
    @abstractmethod
    def get_rules(self) -> List[BookRule]:
        pass


class DefaultBookRuleFactory(BookRuleFactory):
    def get_rules(self) -> List[BookRule]:
        return [TagsRule(), DiscoverRule()]
