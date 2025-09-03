from abc import ABC, abstractmethod

from pipelex.tools.exceptions import ToolException


class TemplateNotFoundError(ToolException):
    pass


class TemplateProviderAbstract(ABC):
    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def teardown(self) -> None:
        pass

    @abstractmethod
    def get_template(self, template_name: str) -> str:
        pass
