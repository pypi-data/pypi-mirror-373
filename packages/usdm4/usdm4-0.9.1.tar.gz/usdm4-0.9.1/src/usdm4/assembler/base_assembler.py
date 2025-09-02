from simple_error_log.errors import Errors
from usdm4.builder.builder import Builder


class BaseAssembler:
    MODULE = "usdm4.assembler.base_assembler.BaseAssembler"

    def __init__(self, builder: Builder, errors: Errors):
        self._errors = errors
        self._builder = builder

    def execute(self, data: dict) -> None:
        pass

    def _label_to_name(self, text: str) -> str:
        return text.upper().replace(" ", "-")
