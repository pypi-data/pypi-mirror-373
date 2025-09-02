from datetime import date
from typing import List, Literal, Union
from .api_base_model import ApiBaseModelWithId
from .code import Code
from .identifier import StudyIdentifier, ReferenceIdentifier
from .study_design import (
    StudyDesign,
    InterventionalStudyDesign,
    ObservationalStudyDesign,
)
from .governance_date import GovernanceDate
from .study_amendment import StudyAmendment
from .study_title import StudyTitle
from .eligibility_criterion import EligibilityCriterionItem
from .narrative_content import NarrativeContentItem
from .comment_annotation import CommentAnnotation
from .abbreviation import Abbreviation
from .study_role import StudyRole
from .organization import Organization
from .study_intervention import StudyIntervention
from .administrable_product import AdministrableProduct
from .medical_device import MedicalDevice
from .product_organization_role import ProductOrganizationRole
from .biomedical_concept import BiomedicalConcept
from .biomedical_concept_category import BiomedicalConceptCategory
from .biomedical_concept_surrogate import BiomedicalConceptSurrogate
from .syntax_template_dictionary import SyntaxTemplateDictionary
from .condition import Condition


class StudyVersion(ApiBaseModelWithId):
    versionIdentifier: str
    rationale: str
    documentVersionIds: List[str] = []
    dateValues: List[GovernanceDate] = []
    amendments: List[StudyAmendment] = []
    businessTherapeuticAreas: List[Code] = []
    studyIdentifiers: List[StudyIdentifier]
    referenceIdentifiers: List[ReferenceIdentifier] = []
    studyDesigns: List[Union[InterventionalStudyDesign, ObservationalStudyDesign]] = []
    titles: List[StudyTitle]
    eligibilityCriterionItems: List[EligibilityCriterionItem] = []
    narrativeContentItems: List[NarrativeContentItem] = []
    abbreviations: List[Abbreviation] = []
    roles: List[StudyRole] = []
    organizations: List[Organization] = []
    studyInterventions: List[StudyIntervention] = []
    administrableProducts: List[AdministrableProduct] = []
    medicalDevices: List[MedicalDevice] = []
    productOrganizationRoles: List[ProductOrganizationRole] = []
    biomedicalConcepts: List[BiomedicalConcept] = []
    bcCategories: List[BiomedicalConceptCategory] = []
    bcSurrogates: List[BiomedicalConceptSurrogate] = []
    dictionaries: List[SyntaxTemplateDictionary] = []
    conditions: List[Condition] = []
    notes: List[CommentAnnotation] = []
    instanceType: Literal["StudyVersion"]

    def get_title(self, title_type):
        for title in self.titles:
            if title.type.decode == title_type:
                return title
        return None

    def sponsor_identifier(self):
        for identifier in self.studyIdentifiers:
            org = self.organization(identifier.scopeId)
            if org and org.type.code == "C54149":
                return identifier
        return None

    def organization(self, id: str) -> Organization:
        return next((x for x in self.organizations if x.id == id), None)

    def criterion_item(self, id: str) -> EligibilityCriterionItem:
        return next((x for x in self.eligibilityCriterionItems if x.id == id), None)

    def intervention(self, id: str) -> StudyIntervention:
        return next((x for x in self.studyInterventions if x.id == id), None)

    def phases(self) -> str:
        return ", ".join([sd.phase_as_text() for sd in self.studyDesigns])

    def official_title_text(self) -> str:
        for x in self.titles:
            if x.is_official():
                return x.text
        return ""

    def short_title_text(self) -> str:
        for x in self.titles:
            if x.is_short():
                return x.text
        return ""

    def acronym_text(self) -> str:
        for x in self.titles:
            if x.is_acronym():
                return x.text
        return ""

    def official_title(self) -> StudyIdentifier:
        for x in self.titles:
            if x.is_official():
                return x
        return None

    def short_title(self) -> StudyIdentifier:
        for x in self.titles:
            if x.is_short():
                return x
        return None

    def acronym(self) -> StudyIdentifier:
        for x in self.titles:
            if x.is_acronym():
                return x
        return None

    def sponsor(self) -> Organization:
        map = self.organization_map()
        for x in self.studyIdentifiers:
            if x.is_sponsor(map):
                return map[x.scopeId]
        return None

    # Note: Method sponsor_identifier in base USDM class

    def sponsor_identifier_text(self) -> StudyIdentifier:
        for x in self.studyIdentifiers:
            if x.is_sponsor(self.organization_map()):
                return x.text
        return ""

    def sponsor_name(self) -> str:
        map = self.organization_map()
        for x in self.studyIdentifiers:
            if x.is_sponsor(map):
                return map[x.scopeId].name
        return ""

    def sponsor_address(self) -> str:
        map = self.organization_map()
        for x in self.studyIdentifiers:
            if x.is_sponsor(map):
                return map[x.scopeId].legalAddress.text
        return ""

    def nct_identifier(self) -> StudyIdentifier:
        map = self.organization_map()
        for x in self.studyIdentifiers:
            if map[x.scopeId].name == "ClinicalTrials.gov":
                return x.text
        return ""

    def protocol_date(self) -> GovernanceDate:
        for x in self.dateValues:
            if x.type.decode == "Protocol Effective Date":
                return x
        return ""

    def approval_date(self) -> GovernanceDate:
        for x in self.dateValues:
            if x.type.decode == "Protocol Approval by Sponsor Date":
                return x
        return ""

    def protocol_date_value(self) -> date:
        for x in self.dateValues:
            if x.type.decode == "Protocol Effective Date":
                return x.dateValue
        return ""

    def approval_date_value(self) -> date:
        for x in self.dateValues:
            if x.type.decode == "Protocol Approval by Sponsor Date":
                return x.dateValue
        return ""

    def organization_map(self) -> Organization:
        return {x.id: x for x in self.organizations}

    def find_study_design(self, id: str) -> StudyDesign:
        return next((x for x in self.studyDesigns if x.id == id), None)

    def narrative_content_item_map(self) -> NarrativeContentItem:
        return {x.id: x for x in self.narrativeContentItems}
