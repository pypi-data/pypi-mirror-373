from uuid import uuid4
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4.api.wrapper import Wrapper
from usdm4.api.code import Code
from usdm4.api.alias_code import AliasCode
from usdm4.api.geographic_scope import GeographicScope
from usdm4.api.governance_date import GovernanceDate
from usdm4.api.organization import Organization
from usdm4.api.study import Study
from usdm4.api.study_definition_document import StudyDefinitionDocument
from usdm4.api.study_definition_document_version import StudyDefinitionDocumentVersion
from usdm4.api.identifier import StudyIdentifier
from usdm4.api.study_title import StudyTitle
from usdm4.api.study_version import StudyVersion
from usdm4.api.biomedical_concept import BiomedicalConcept
from usdm4.api import __all__ as v4_classes
from usdm4.__info__ import __model_version__, __package_version__
from usdm3.base.id_manager import IdManager
from usdm3.base.api_instance import APIInstance
from usdm3.ct.cdisc.library import Library as CdiscCTLibrary
from usdm3.bc.cdisc.library import Library as CdiscBCLibrary
from usdm3.data_store.data_store import DataStore
from usdm4.ct.iso.iso3166.library import Library as Iso3166Library
from usdm4.ct.iso.iso639.library import Library as Iso639Library
from usdm4.builder.cross_reference import CrossReference
from usdm4.api.api_base_model import ApiBaseModelWithId
from usdm4.builder.other_ct_version_manager import OtherCTVersionManager


class Builder:
    MODULE = "usdm4.builder.builder.Builder"

    def __init__(self, root_path: str, errors: Errors):
        self._id_manager: IdManager = IdManager(v4_classes)
        self.errors = errors
        self.api_instance: APIInstance = APIInstance(self._id_manager)
        self.cdisc_ct_library = CdiscCTLibrary(root_path)
        self.cdisc_bc_library = CdiscBCLibrary(root_path, self.cdisc_ct_library)
        self.iso3166_library = Iso3166Library(root_path)
        self.iso639_library = Iso639Library(root_path)
        self.cross_reference = CrossReference()
        self.other_ct_version_manager = OtherCTVersionManager()
        self.cdisc_ct_library.load()
        self.cdisc_bc_library.load()
        self.iso3166_library.load()
        self.iso639_library.load()
        self._data_store = None
        self._cdisc_code_system = self.cdisc_ct_library.system
        self._cdisc_code_system_version = self.cdisc_ct_library.version

    def clear(self):
        self._id_manager.clear()
        self.errors.clear()
        self.cross_reference.clear()
        self._data_store = None

    def seed(self, file_path: str):
        self._data_store = DataStore(file_path)
        self._data_store.decompose()
        for klass in v4_classes:
            for instance in self._data_store.instances_by_klass(klass):
                if "id" in instance:
                    self._id_manager.add_id(klass, instance["id"])

    def create(
        self, klass: str, params: dict, cross_reference: bool = True
    ) -> ApiBaseModelWithId | None:
        try:
            object: ApiBaseModelWithId = self.api_instance.create(klass, params)
            if self._check_object(object) and cross_reference:
                name = self._set_name(object, params)
                self.cross_reference.add(object, name)
            return object
        except Exception as e:
            print(f"EXCEPTION ON CREATE: {e}")
            location = KlassMethodLocation(self.MODULE, "create")
            self.errors.exception(
                f"Failed to create instance of klass '{klass}' with params {params}, reason: {e}",
                e,
                location,
            )
            print(f"ERRORS: {self.errors}")
            return None

    def _check_object(self, object) -> bool:
        return True if object and hasattr(object, "id") else False

    def _set_name(self, object, params: dict) -> str | None:
        if hasattr(object, "name"):
            return object.name
        elif "name" in params:
            return params["name"]
        return None

    def minimum(self, title: str, identifier: str, version: str) -> "Wrapper":
        """
        Create a minimum study with the given title, identifier, and version.
        """
        # Define the codes to be used in the study
        english_code = self.iso639_code("en")
        title_type = self.cdisc_code("C207616", "Official Study Title")
        organization_type_code = self.cdisc_code("C54149", "Pharmaceutical Company")
        doc_status_code = self.cdisc_code("C25425", "Approved")
        protocol_code = self.cdisc_code("C70817", "Protocol")
        global_code = self.cdisc_code("C68846", "Global")
        global_scope = self.create(GeographicScope, {"type": global_code})
        approval_date_code = self.cdisc_code(
            "C132352", "Protocol Approval by Sponsor Date"
        )

        # Study Title
        study_title = self.create(StudyTitle, {"text": title, "type": title_type})

        # Governance dates
        approval_date = self.create(
            GovernanceDate,
            {
                "name": "D_APPROVE",
                "label": "Design Approval",
                "description": "Design approval date",
                "type": approval_date_code,
                "dateValue": "2006-06-01",
                "geographicScopes": [global_scope],
            },
        )
        # Define the organization and the study identifier
        organization = self.create(
            Organization,
            {
                "name": "Sponsor",
                "type": organization_type_code,
                "identifier": "To be provided",
                "identifierScheme": "To be provided",
                "legalAddress": None,
            },
        )
        study_identifier = self.create(
            StudyIdentifier,
            {"text": identifier, "scopeId": organization.id},
        )

        # Documenta
        study_definition_document_version = self.create(
            StudyDefinitionDocumentVersion,
            {"version": "1", "status": doc_status_code, "dateValues": [approval_date]},
        )
        study_definition_document = self.create(
            StudyDefinitionDocument,
            {
                "name": "PROTOCOL DOCUMENT",
                "label": "Protocol Document",
                "description": "The entire protocol document",
                "language": english_code,
                "type": protocol_code,
                "templateName": "Sponsor",
                "versions": [study_definition_document_version],
            },
        )

        study_version = self.create(
            StudyVersion,
            {
                "versionIdentifier": "1",
                "rationale": "To be provided",
                "titles": [study_title],
                "studyDesigns": [],
                "documentVersionIds": [study_definition_document_version.id],
                "studyIdentifiers": [study_identifier],
                "studyPhase": None,
                "dateValues": [approval_date],
                "amendments": [],
                "organizations": [organization],
            },
        )
        study = self.create(
            Study,
            {
                "id": str(uuid4()),
                "name": "Study",
                "label": title,
                "description": title,
                "versions": [study_version],
                "documentedBy": [study_definition_document],
            },
        )

        # Return the wrapper for the study
        result = self.api_instance.create(
            Wrapper,
            {
                "study": study,
                "usdmVersion": __model_version__,
                "systemName": "Python USDM4 Package",
                "systemVersion": __package_version__,
            },
        )
        return result

    def klass_and_attribute(self, klass: str, attribute: str) -> dict:
        return self.cdisc_ct_library.klass_and_attribute(klass, attribute)

    def klass_and_attribute_value(self, klass: str, attribute: str, value: str) -> Code:
        code_item, version = self.cdisc_ct_library.klass_and_attribute_value(
            klass, attribute, value
        )
        return (
            self.create(
                Code,
                {
                    "code": code_item["conceptId"],
                    "codeSystem": self._cdisc_code_system,
                    "codeSystemVersion": version,
                    "decode": code_item["preferredTerm"],
                },
            )
            if code_item
            else None
        )

    def cdisc_code(self, code: str, decode: str) -> Code:
        cl = self.cdisc_ct_library.cl_by_term(code)
        return (
            self.create(
                Code,
                {
                    "code": code,
                    "codeSystem": self._cdisc_code_system,
                    "codeSystemVersion": cl["source"]["effective_date"],
                    "decode": decode,
                },
            )
            if cl
            else None
        )

    def cdisc_unit_code(self, unit: str) -> Code:
        unit = self.cdisc_ct_library.unit(unit)
        unit_cl = self.cdisc_ct_library.unit_code_list()
        return (
            self.create(
                Code,
                {
                    "code": unit["conceptId"],
                    "codeSystem": self._cdisc_code_system,
                    "codeSystemVersion": unit_cl["source"]["effective_date"],
                    "decode": unit["preferredTerm"],
                },
            )
            if unit
            else None
        )

    def alias_code(self, standard_code: Code) -> AliasCode:
        return self.create(AliasCode, {"standardCode": standard_code})

    def bc(self, name) -> BiomedicalConcept | None:
        if self.cdisc_bc_library.exists(name):
            bc_params = self.cdisc_bc_library.usdm(name)
            self._set_ids(bc_params)
            return self.create(
                BiomedicalConcept, bc_params, False
            )  # No cross reference for BCs
        else:
            return None

    def iso3166_code_or_decode(self, text: str) -> Code:
        code, decode = self.iso3166_library.code_or_decode(text)
        if code:
            return self.create(
                Code,
                {
                    "code": code,
                    "codeSystem": self.iso3166_library.system,
                    "codeSystemVersion": self.iso3166_library.version,
                    "decode": decode,
                },
            )
        else:
            return None

    def iso3166_code(self, code: str) -> Code:
        code, decode = self.iso3166_library.decode(code)
        if code:
            return self.create(
                Code,
                {
                    "code": code,
                    "codeSystem": self.iso3166_library.system,
                    "codeSystemVersion": self.iso3166_library.version,
                    "decode": decode,
                },
            )
        else:
            return None

    def iso639_code_or_decode(self, text: str) -> Code:
        code, decode = self.iso639_library.code_or_decode(text)
        print(f"ISO639: {text} = [{code} {decode}]")
        if code:
            return self.create(
                Code,
                {
                    "code": code,
                    "codeSystem": self.iso639_library.system,
                    "codeSystemVersion": self.iso639_library.version,
                    "decode": decode,
                },
            )
        else:
            return None

    def iso639_code(self, code: str) -> Code:
        new_code, decode = self.iso639_library.decode(code)
        if new_code:
            return self.create(
                Code,
                {
                    "code": code,
                    "codeSystem": self.iso639_library.system,
                    "codeSystemVersion": self.iso639_library.version,
                    "decode": decode,
                },
            )
        else:
            return None

    def iso3166_region_code(self, code: str) -> Code:
        code, decode = self.iso3166_library.region_code(code)
        return self.create(
            Code,
            {
                "code": code,
                "codeSystem": self.iso3166_library.system,
                "codeSystemVersion": self.iso3166_library.version,
                "decode": decode,
            },
        )

    def other_code(self, code: str, system: str, version: str, decode: str) -> Code:
        return self.create(
            Code,
            {
                "code": code,
                "codeSystem": system,
                "codeSystemVersion": version,
                "decode": decode,
            },
        )

    def sponsor(self, sponsor_name: str) -> Organization:
        sponsor_code = self.cdisc_code("C54149", "Pharmaceutical Company")
        return self.create(
            Organization,
            {
                "name": sponsor_name,
                "label": sponsor_name,
                "type": sponsor_code,
                "identifier": "---------",
                "identifierScheme": "DUNS",
                # "legalAddress": address
            },
        )

    def double_link(self, items, prev_attribute, next_attribute):
        for idx, item in enumerate(items):
            if idx == 0:
                setattr(item, prev_attribute, None)
            else:
                the_id = getattr(items[idx - 1], "id")
                setattr(item, prev_attribute, the_id)
            if idx == len(items) - 1:
                setattr(item, next_attribute, None)
            else:
                the_id = getattr(items[idx + 1], "id")
                setattr(item, next_attribute, the_id)

    def load(self, data: dict):
        self._decompose(data)

    def _decompose(self, data) -> None:
        if isinstance(data, dict):
            self._add_id(data)
            for _, value in data.items():
                if isinstance(value, dict):
                    self._decompose(value)
                elif isinstance(value, list):
                    for item in value:
                        self._decompose(item)

    def _add_id(self, data: dict):
        self._id_manager.add_id(data["instanceType"], data["id"])

    def _set_ids(self, parent):
        if isinstance(parent, str) or isinstance(parent, bool) or (parent is None):
            return
        parent["id"] = self._id_manager.build_id(parent["instanceType"])
        for _, value in parent.items():
            if isinstance(value, list):
                for child in value:
                    self._set_ids(child)
            else:
                self._set_ids(value)
