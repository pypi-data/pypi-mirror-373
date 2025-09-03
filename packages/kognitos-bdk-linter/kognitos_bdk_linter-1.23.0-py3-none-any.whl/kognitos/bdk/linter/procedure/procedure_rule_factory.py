from abc import ABC, abstractmethod
from typing import List

from .rules.procedure_rules import (ProcedureConnectionRequiredRule,
                                    ProcedureExamplesRule, ProcedureRule)


class ProcedureRuleFactory(ABC):
    @abstractmethod
    def get_rules(self) -> List[ProcedureRule]:
        pass


class DefaultProcedureRuleFactory(ProcedureRuleFactory):
    def get_rules(self) -> List[ProcedureRule]:
        return [ProcedureExamplesRule(), ProcedureConnectionRequiredRule()]
