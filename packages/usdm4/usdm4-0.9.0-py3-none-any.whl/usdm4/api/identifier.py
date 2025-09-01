from typing import Literal
from .api_base_model import ApiBaseModelWithId
from .organization import Organization
from .code import Code


class Identifier(ApiBaseModelWithId):
    text: str
    scopeId: str
    instanceType: Literal["Identifier"]


class ReferenceIdentifier(Identifier):
    type: Code
    instanceType: Literal["ReferenceIdentifier"]


class StudyIdentifier(Identifier):
    instanceType: Literal["StudyIdentifier"]

    def is_sponsor(self, organization_map: dict) -> bool:
        org = organization_map[self.scopeId]
        return True if org.type.code == "C54149" else False

    def scoped_by(self, organization_map: dict) -> Organization:
        return organization_map[self.scopeId]


class AdministrableProductIdentifier(Identifier):
    instanceType: Literal["AdministrableProductIdentifier"]


class MedicalDeviceIdentifier(Identifier):
    type: Code
    instanceType: Literal["MedicalDeviceIdentifier"]
