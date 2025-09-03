from pylint.lint import PyLinter

from .book import BookChecker
from .concept_checker import ConceptChecker
from .config_checker import ConfigChecker
from .connect_checker import ConnectChecker
from .oauth_checker import OAuthChecker
from .procedure.procedure_checker import ProcedureChecker
from .pyproject_checker import PyProjectChecker


def register(linter: PyLinter) -> None:
    """This required method auto registers the checker during initialization.
    :param linter: The linter to register the checker to.
    """
    linter.register_checker(PyProjectChecker(linter))
    linter.register_checker(BookChecker(linter))
    linter.register_checker(ProcedureChecker(linter))
    linter.register_checker(ConnectChecker(linter))
    linter.register_checker(ConfigChecker(linter))
    linter.register_checker(OAuthChecker(linter))
    linter.register_checker(ConceptChecker(linter))
