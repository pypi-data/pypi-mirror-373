from usdm4.assembler.base_assembler import BaseAssembler
from usdm4.builder.builder import Builder
from usdm4.api.address import Address
from usdm4.api.organization import Organization
from usdm4.api.identifier import StudyIdentifier
from usdm4.api.study_title import StudyTitle


from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation


class IdentificationAssembler(BaseAssembler):
    """
    Assembler for processing study identification information including titles, identifiers, and organizations.

    This assembler handles the creation of study titles, study identifiers, and associated organizations
    based on input data. It supports both standard predefined organizations (like CT.GOV, EMA, FDA)
    and custom non-standard organizations.

    Attributes:
        MODULE (str): Module path for error reporting
        TITLE_TYPES (list): Supported study title types
        TITLE_CODES (dict): Mapping of title types to CDISC codes
        ORG_CODES (dict): Mapping of organization types to CDISC codes
        STANDARD_ORGS (dict): Predefined standard organizations with their details
    """

    MODULE = "usdm4.assembler.identification_assembler.IdentificationAssembler"

    TITLE_TYPES = [
        "brief",
        "official",
        "public",
        "scientific",
        "acronym",
    ]

    TITLE_CODES = {
        "brief": {"code": "C207615", "decode": "Brief Study Title"},
        "official": {"code": "C207616", "decode": "Official Study Title"},
        "public": {"code": "C207617", "decode": "Public Study Title"},
        "scientific": {"code": "C207618", "decode": "Scientific Study Title"},
        "acronym": {"code": "C207646", "decode": "Study Acronym"},
    }

    ORG_CODES = {
        "registry": {"code": "C93453", "decode": "Clinical Study Registry"},
        "regulator": {"code": "C188863", "decode": "Regulatory Agency"},
        "healthcare": {"code": "C21541", "decode": "Healthcare Facility"},
        "pharma": {"code": "C54149", "decode": "Pharmaceutical Company"},
        "lab": {"code": "C37984", "decode": "Laboratory"},
        "cro": {"code": "C54148", "decode": "Contract Research Organization"},
        "gov": {"code": "C199144", "decode": "Government Institute"},
        "academic": {"code": "C18240", "decode": "Academic Institution"},
        "medical_device": {"code": "C215661", "decode": "Medical Device Company"},
    }
    STANDARD_ORGS = {
        "ct.gov": {
            "type": "registry",
            "name": "CT.GOV",
            "label": "ClinicalTrials.gov",
            "description": "The US clinical trials registry",
            "identifier": "ClinicalTrials.gov",
            "identifierScheme": "National Institute of Health, US Government",
            "legalAddress": {
                "lines": ["National Library of Medicine", "8600 Rockville Pike"],
                "city": "Bethesda",
                "district": "",
                "state": "MD",
                "postalCode": "20894",
                "country": "USA",
            },
        },
        "ema": {
            "type": "regulator",
            "name": "EMA",
            "label": "European Medicines Agency",
            "description": "The European medicines regulator",
            "identifier": "EMA",
            "identifierScheme": "European Union",
            "legalAddress": {
                "lines": ["Domenico Scarlattilaan 6"],
                "city": "Amsterdam",
                "district": "",
                "state": "",
                "postalCode": "1083 HS",
                "country": "NL",
            },
        },
        "fda": {
            "type": "regulator",
            "name": "FDA",
            "label": "Food and Drug Admionistration",
            "identifier": "FDA",
            "description": "The US medicines regulator",
            "identifierScheme": "Health and Human Services, US Government",
            "legalAddress": {
                "lines": ["10903 New Hampshire Ave"],
                "city": "Silver Spring",
                "district": "",
                "state": "MD",
                "postalCode": "20903",
                "country": "USA",
            },
        },
    }

    def __init__(self, builder: Builder, errors: Errors):
        """
        Initialize the IdentificationAssembler.

        Args:
            builder (Builder): The builder instance for creating USDM objects
            errors (Errors): Error handling instance for logging issues
        """
        super().__init__(builder, errors)
        self._titles = []
        self._organizations = []
        self._identifiers = []
        self._study_name = ""

    def execute(self, data: dict) -> None:
        """
        Process study identification data to create titles, identifiers, and organizations.

        This method processes the input data dictionary to create study titles, study identifiers,
        and associated organizations. It handles both standard predefined organizations and
        custom non-standard organizations.

        Args:
            data (dict): A complex dictionary containing study identification information with the following structure:
                {
                    "titles": {
                        "brief": str,           # Brief study title
                        "official": str,        # Official study title
                        "public": str,          # Public study title
                        "scientific": str,      # Scientific study title
                        "acronym": str,         # Study acronym
                    },
                    "identifiers": [            # List of study identifiers
                        {
                            "identifier": str,  # The actual identifier value
                            "scope": {          # Organization scope for the identifier
                                # Either use a standard predefined organization:
                                "standard": str,    # Key from STANDARD_ORGS (e.g., "ct.gov", "ema", "fda")

                                # OR define a custom non-standard organization:
                                "non_standard": {
                                    "type": str,            # Organization type (must match ORG_CODES keys)
                                    "name": str,            # Organization name
                                    "description": str,     # Organization description
                                    "label": str,           # Organization label/display name
                                    "identifier": str,      # Organization identifier
                                    "identifierScheme": str, # Scheme used for organization identifier
                                    "legalAddress": {       # Organization's legal address
                                        "lines": [str],     # Address lines (array of strings)
                                        "city": str,        # City name
                                        "district": str,    # District/region
                                        "state": str,       # State/province
                                        "postalCode": str,  # Postal/ZIP code
                                        "country": str      # ISO 3166 country code
                                    }
                                }
                            }
                        }
                    ]
                }

        Note:
            - Title types must be one of: "brief", "official", "public", "scientific", "acronym"
            - Organization types for non_standard must match keys in ORG_CODES
            - Standard organization keys must match keys in STANDARD_ORGS
            - Country codes must be valid ISO 3166 codes
            - Each identifier must have either "standard" OR "non_standard" in scope, not both

        Raises:
            Various exceptions may be raised during object creation if data is invalid
        """
        # print(f"\n\nDATA; {data}\n\n")

        # Make sure data ok.
        titles = data["titles"] if "titles" in data else {}
        identifiers = data["identifiers"] if "identifiers" in data else []

        # Titles
        for type, text in titles.items():
            try:
                if type in self.TITLE_TYPES:
                    title = self._create_title(type, text)
                    if title:
                        self._titles.append(title)
                else:
                    self._errors.warning(
                        f"Title '{text}' of type '{type}' is not valid, ignored."
                    )
            except Exception as e:
                location = KlassMethodLocation(self.MODULE, "execute")
                self._errors.exception(
                    f"Failed during creation of title '{text}' of type '{type}'",
                    e,
                    location,
                )

        # Identifiers
        id_details: dict
        for id_details in identifiers:
            try:
                scope = id_details["scope"]
                organization: dict = (
                    self.STANDARD_ORGS[scope["standard"]]
                    if "standard" in scope
                    else scope["non_standard"]
                )

                # Address
                if organization["legalAddress"]:
                    organization["legalAddress"] = self._create_address(
                        organization["legalAddress"]
                    )

                # Identifier and scoping Organization
                org = self._create_organization(organization)
                if org:
                    identifier = self._create_identifier(id_details["identifier"], org)
                    if identifier:
                        self._organizations.append(org)
                        self._identifiers.append(identifier)
                    else:
                        location = KlassMethodLocation(self.MODULE, "execute")
                        self._errors.exception(
                            f"Failed to create identifier {id_details['identifier']}",
                            location,
                        )
                else:
                    location = KlassMethodLocation(self.MODULE, "execute")
                    self._errors.exception(
                        f"Failed to create organization {organization}", location
                    )
            except Exception as e:
                location = KlassMethodLocation(self.MODULE, "execute")
                self._errors.exception(
                    f"Failed during creation of identifier {id_details}", e, location
                )

    @property
    def titles(self):
        return self._titles

    @property
    def organizations(self):
        return self._organizations

    @property
    def identifiers(self):
        return self._identifiers

    def _create_address(self, address: dict) -> Address | None:
        try:
            if ("country" in address) and address["country"]:
                address["country"] = self._builder.iso3166_code_or_decode(
                    address["country"]
                )
            else:
                address["country"] = None
            addr: Address = self._builder.create(Address, address)
            addr.set_text()
            self._errors.info(
                f"Address set to {addr.text}",
                KlassMethodLocation(self.MODULE, "_create_address"),
            )
            return addr
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_create_address")
            self._errors.exception("Failed to create address object", e, location)
            return None

    def _create_organization(self, organization: dict) -> Organization | None:
        try:
            org_type = organization["type"]
            organization["type"] = self._builder.cdisc_code(
                self.ORG_CODES[org_type]["code"], self.ORG_CODES[org_type]["decode"]
            )
            organization["name"] = self._label_to_name(organization["label"])
            return self._builder.create(Organization, organization)
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_create_organization")
            self._errors.exception(
                "Failed during creation of organization", e, location
            )
            return None

    def _create_identifier(
        self, identifier: str, org: Organization
    ) -> StudyIdentifier | None:
        try:
            identifier = self._builder.create(
                StudyIdentifier, {"text": identifier, "scopeId": org.id}
            )
            return identifier
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_create_identifier")
            self._errors.exception(
                f"Failed during creation of identifier '{identifier}'", e, location
            )
            return None

    def _create_title(self, type: str, text: str) -> StudyTitle | None:
        try:
            title_type = self._builder.cdisc_code(
                self.TITLE_CODES[type]["code"], self.TITLE_CODES[type]["decode"]
            )
            return self._builder.create(StudyTitle, {"text": text, "type": title_type})
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_create_title")
            self._errors.exception(
                f"Failed during creation of title '{text}'of type '{type}'", e, location
            )
            return None
