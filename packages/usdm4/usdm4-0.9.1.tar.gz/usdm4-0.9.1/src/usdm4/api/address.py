from typing import Literal, Union, List
from .api_base_model import ApiBaseModelWithId
from .code import Code


class Address(ApiBaseModelWithId):
    text: Union[str, None] = None
    lines: List[str] = []
    city: Union[str, None] = None
    district: Union[str, None] = None
    state: Union[str, None] = None
    postalCode: Union[str, None] = None
    country: Union[Code, None] = None
    instanceType: Literal["Address"]

    def set_text(self) -> None:
        text = ""
        for line in self.lines:
            text = Address._concat(text, line)
        for attr in ["city", "district", "state", "postalCode"]:
            text = Address._concat(text, self.__getattribute__(attr))
        self.text = Address._concat(text, self.country.decode) if self.country else text

    @staticmethod
    def _concat(text, value):
        if text:
            return text + ", " + value if value else text
        else:
            return value if value else ""
