from typing import Literal
from .api_base_model import ApiBaseModelWithId
from .code import Code


class StudyTitle(ApiBaseModelWithId):
    text: str
    type: Code
    instanceType: Literal["StudyTitle"]

    def is_official(self) -> bool:
        return True if self.type.decode == "Official Study Title" else False

    def is_acronym(self) -> bool:
        return True if self.type.decode == "Study Acronym" else False

    def is_short(self) -> bool:
        return True if self.type.decode == "Brief Study Title" else False
