import re
from uuid import uuid4
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4.assembler.base_assembler import BaseAssembler
from usdm4.assembler.encoder import Encoder
from usdm4.assembler.identification_assembler import IdentificationAssembler
from usdm4.assembler.study_design_assembler import StudyDesignAssembler
from usdm4.assembler.document_assembler import DocumentAssembler
from usdm4.assembler.population_assembler import PopulationAssembler
from usdm4.assembler.amendments_assembler import AmendmentsAssembler
from usdm4.builder.builder import Builder
from usdm4.api.study import Study
from usdm4.api.study_version import StudyVersion
from usdm4.api.geographic_scope import GeographicScope
from usdm4.api.governance_date import GovernanceDate


class StudyAssembler(BaseAssembler):
    """
    Assembler responsible for creating the top-level Study object and its associated StudyVersion.

    This assembler coordinates data from multiple other assemblers to create the complete study
    structure, including study metadata, versions, governance dates, and cross-references to
    study designs, documents, and identification information.
    """

    MODULE = "usdm4.assembler.study_assembler.StudyAssembler"

    def __init__(self, builder: Builder, errors: Errors):
        """
        Initialize the StudyAssembler.

        Args:
            builder (Builder): The builder instance for creating USDM objects
            errors (Errors): Error handling instance for logging issues
        """
        super().__init__(builder, errors)
        self._study = None
        self._encoder = Encoder(builder, errors)
        self._dates = []

    def execute(
        self,
        data: dict,
        identification_assembler: IdentificationAssembler,
        study_design_assembler: StudyDesignAssembler,
        document_assembler: DocumentAssembler,
        population_assembler: PopulationAssembler,
        amendments_assembler: AmendmentsAssembler,
    ) -> None:
        """
        Creates the top-level Study object and its associated StudyVersion from study data.

        Args:
            data (dict): A dictionary containing core study information.
                        The data parameter must have the following structure:

                        {
                            "name": str,               # Internal name/identifier for the study
                            "label": str,              # Human-readable display label for the study
                            "version": str,            # Version identifier for this study version
                            "rationale": str,          # Rationale or reason for this study version
                            # Additional optional fields may include:
                            # "description": str,       # Detailed study description
                            # "objectives": list,       # List of study objectives
                            # "indications": list,      # List of study indications
                            # "interventions": list,    # List of study interventions
                            # "sponsor_approval_date": str,  # Date of sponsor approval (ISO format)
                        }

                        Required fields:
                        - "name": Internal identifier/name for the study
                        - "label": Display label for the study
                        - "version": Version identifier (e.g., "1.0", "2.1", etc.)
                        - "rationale": Explanation for this version of the study

            identification_assembler (IdentificationAssembler): Assembler containing study
                identifiers, titles, and organization information
            study_design_assembler (StudyDesignAssembler): Assembler containing the complete
                study design structure (arms, epochs, activities, etc.)
            document_assembler (DocumentAssembler): Assembler containing protocol documents
                and governance dates

        Returns:
            None: The created study is stored in self._study property

        Note:
            This method creates both a StudyVersion object (containing version-specific data)
            and a top-level Study object (containing the study container and metadata).
            The StudyVersion aggregates data from all other assemblers, while the Study
            object serves as the root container.
        """
        try:
            # Create the dates
            self._create_date(data)

            # Create StudyVersion parameters by combining data from all assemblers
            params = {
                "versionIdentifier": data["version"],  # Version ID from input data
                "rationale": data["rationale"],  # Version rationale from input data
                "titles": identification_assembler.titles,  # Study titles from identification
                "dateValues": self._dates
                + document_assembler.dates,  # Combined governance dates
                "studyDesigns": [
                    study_design_assembler.study_design
                ],  # Study design structure
                "documentVersionIds": [
                    document_assembler.document_version.id
                ],  # Document references
                "studyIdentifiers": identification_assembler.identifiers,  # Study identifiers
                "organizations": identification_assembler.organizations,  # Sponsor/organization info
                "eligibilityCriterionItems": population_assembler.criteria_items,
                "narrativeContentItems": document_assembler.contents,
                "amendments": [amendments_assembler.amendment]
                if amendments_assembler.amendment
                else [],
            }
            study_version = self._builder.create(StudyVersion, params)

            # print(f"STUDY VERSION: {study_version is not None}")

            # Create the top-level Study container object
            study_name, study_label = self._get_study_name_label(data["name"])
            self._study = self._builder.create(
                Study,
                {
                    "id": uuid4(),  # Generate unique study ID
                    "name": study_name,  # Internal study name
                    "label": study_label,  # Display study label
                    "description": "The top-level study container",  # Default description
                    "versions": [study_version],  # Include the created version
                    "documentedBy": [
                        document_assembler.document
                    ],  # Reference to protocol document
                },
            )

            # print(f"STUDY: {self._study is not None}")

        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "execute")
            self._errors.exception("Failed during creation of study", e, location)

    @property
    def study(self) -> Study:
        return self._study

    def _create_date(self, data: dict) -> None:
        try:
            if actual_date := self._encoder.to_date(data["sponsor_approval_date"]):
                sponsor_approval_date_code = self._builder.cdisc_code(
                    "C132352", "Protocol Approval by Sponsor Date"
                )
                global_code = self._builder.cdisc_code("C68846", "Global")
                global_scope = self._builder.create(
                    GeographicScope, {"type": global_code}
                )
                approval_date = self._builder.create(
                    GovernanceDate,
                    {
                        "name": "SPONSOR-APPORVAL-DATE",  # Human-readable name
                        "type": sponsor_approval_date_code,  # CDISC code for date type
                        "dateValue": actual_date,
                        "geographicScopes": [global_scope],  # Global scope application
                    },
                )
                if approval_date:
                    self._dates.append(approval_date)
            else:
                self._errors.warning(
                    "No sponsor approval date detected",
                    KlassMethodLocation(self.MODULE, "_create_date"),
                )
        except Exception as e:
            self._errors.exception(
                "Failed during creation of governance date",
                e,
                KlassMethodLocation(self.MODULE, "_create_date"),
            )

    def _get_study_name_label(self, options: dict) -> tuple[str, str]:
        items = ["acronym", "identifier", "compound"]
        for item in items:
            if item in options and options[item]:
                name = re.sub(r"[\W_]+", "", options[item].upper())
                self._errors.info(
                    f"Study name set to '{name}'",
                    location=KlassMethodLocation(self.MODULE, "_get_study_name_label"),
                )
                return name, options[item]
        return "", ""
