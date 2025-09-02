from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4.assembler.base_assembler import BaseAssembler
from usdm4.builder.builder import Builder
from usdm4.api.narrative_content import NarrativeContent, NarrativeContentItem
from usdm4.api.study_definition_document import StudyDefinitionDocument
from usdm4.api.study_definition_document_version import StudyDefinitionDocumentVersion
from usdm4.api.geographic_scope import GeographicScope
from usdm4.api.governance_date import GovernanceDate
from usdm4.assembler.encoder import Encoder


class DocumentAssembler(BaseAssembler):
    """
    Assembler responsible for creating StudyDefinitionDocument and StudyDefinitionDocumentVersion objects
    from document data and structured content sections.

    This assembler processes protocol documents, their versions, and hierarchical content sections,
    creating narrative content structures with proper cross-references and governance dates.
    It handles the conversion of structured document data into USDM-compliant document objects.
    """

    MODULE = "usdm4.assembler.document_assembler.DocumentAssembler"
    DIV_OPEN_NS = '<div xmlns="http://www.w3.org/1999/xhtml">'
    DIV_CLOSE = "</div>"

    def __init__(self, builder: Builder, errors: Errors):
        """
        Initialize the DocumentAssembler.

        Args:
            builder (Builder): The builder instance for creating USDM objects
            errors (Errors): Error handling instance for logging issues
        """
        super().__init__(builder, errors)
        self._encoder = Encoder(builder, errors)
        self._document: StudyDefinitionDocument = None
        self._document_version: StudyDefinitionDocumentVersion = None
        self._contents = []
        self._dates = []

    def execute(self, data: dict) -> None:
        """
        Creates StudyDefinitionDocument and StudyDefinitionDocumentVersion objects from document data.

        Args:
            data (dict): A dictionary containing document and section information.
                        The data parameter must have the following structure:

                        {
                            "document": {               # Document metadata
                                "label": str,           # Human-readable document label
                                "version": str,         # Document version identifier
                                "status": str,          # Document status (e.g., "Draft", "Final")
                                "template": str,        # Template name used for document
                                "version_date": str,    # ISO format date for document version
                            },
                            "sections": [               # List of document sections
                                {
                                    "section_number": str,    # Section number (e.g., "1.1", "2.3.1")
                                    "section_title": str,     # Section title/heading
                                    "text": str,              # Section content (HTML allowed)
                                },
                                # ... additional sections
                            ]
                        }

                        Required fields in "document":
                        - "label": Display name for the document
                        - "version": Version identifier (e.g., "1.0", "2.1")
                        - "status": Current status of the document
                        - "template": Template used for document generation
                        - "version_date": Date when this version was created (ISO format)

                        Required fields in each "sections" item:
                        - "section_number": Hierarchical section number (determines nesting level)
                        - "section_title": Title/heading for the section
                        - "text": Content of the section (can include HTML markup)

                        Note: Section hierarchy is determined by the depth of the section_number
                        (e.g., "1" = level 1, "1.1" = level 2, "1.1.1" = level 3)

        Returns:
            None: Created objects are stored in instance properties

        Note:
            This method creates both document metadata objects and processes hierarchical
            sections into NarrativeContent structures with proper parent-child relationships
            and sequential linking (previousId/nextId).
        """
        try:
            # Extract document metadata and sections from input data
            document: dict = data["document"]
            sections: list[dict] = data["sections"]

            # Create governance date from document version date
            self._create_date(document)

            # Create document version object with version and status
            self._document_version = self._builder.create(
                StudyDefinitionDocumentVersion,
                {
                    "version": document["version"],  # Version identifier from input
                    "status": self._encoder.document_status(
                        document["status"]
                    ),  # Document status from input
                },
            )

            # Get standard codes for document properties
            language = self._builder.iso639_code("en")  # Default to English
            doc_type = self._builder.cdisc_code(
                "C70817", "Protocol"
            )  # CDISC code for Protocol

            # Create the main document object
            self._document = self._builder.create(
                StudyDefinitionDocument,
                {
                    "name": self._label_to_name(
                        document["label"]
                    ),  # Convert label to internal name
                    "label": document["label"],  # Display label from input
                    "description": "Protocol Document",  # Default description
                    "language": language,  # ISO language code
                    "type": doc_type,  # CDISC document type code
                    "templateName": document["template"],  # Template name from input
                    "versions": [self._document_version],  # Include the created version
                },
            )

            # Process sections into hierarchical narrative content structure
            _ = self._section_to_narrative(None, sections, 0, 1)

            # Create sequential links between narrative content items
            self._builder.double_link(
                self._document_version.contents, "previousId", "nextId"
            )

        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "execute")
            self._errors.exception("Failed during creation of document", e, location)

    @property
    def document(self) -> StudyDefinitionDocument:
        return self._document

    @property
    def document_version(self) -> StudyDefinitionDocumentVersion:
        return self._document_version

    @property
    def contents(self) -> list[NarrativeContentItem]:
        # print(f"SECTION COUNT: {len(self._contents)}")
        return self._contents

    @property
    def dates(self) -> list[GovernanceDate]:
        return self._dates

    def _section_to_narrative(
        self, parent: NarrativeContent, sections: list[dict], index: int, level: int
    ) -> int:
        process = True
        previous = None
        local_index = index
        location = KlassMethodLocation(self.MODULE, "_section_to_narrative")
        while process:
            section = sections[local_index]
            section_level = self._section_level(section)
            if section_level == level:
                sn = section["section_number"] if section["section_number"] else ""
                dsn = True if sn else False
                st = section["section_title"] if section["section_title"] else ""
                dst = True if st else False
                nc_text = f"{self.DIV_OPEN_NS}{section['text']}{self.DIV_CLOSE}"
                nci = self._builder.create(
                    NarrativeContentItem,
                    {"name": f"NCI-{local_index}", "text": nc_text},
                )
                nc = self._builder.create(
                    NarrativeContent,
                    {
                        "name": f"NC-{local_index}",
                        "sectionNumber": sn,
                        "displaySectionNumber": dsn,
                        "sectionTitle": st,
                        "displaySectionTitle": dst,
                        "contentItemId": nci.id,
                        "childIds": [],
                        "previousId": None,
                        "nextId": None,
                    },
                )
                self._document_version.contents.append(nc)
                self._contents.append(nci)
                # print(f"SECTION ADD: {len(self._contents)}")
                if parent:
                    parent.childIds.append(nc.id)
                previous = nc
                local_index += 1
            elif section_level > level:
                if previous:
                    local_index = self._section_to_narrative(
                        previous, sections, local_index, level + 1
                    )
                else:
                    self._errors.error(
                        "No previous section set while processing sections", location
                    )
                    local_index += 1
            elif section_level < level:
                return local_index
            if local_index >= len(sections):
                process = False
        return local_index

    def _section_level(self, section: dict) -> int:
        section_number: str = section["section_number"]
        text = section_number[:-1] if section_number.endswith(".") else section_number
        return len(text.split("."))

    def _create_date(self, data: dict) -> None:
        """
        Creates a governance date for the protocol effective date from document data.

        Args:
            data (dict): A dictionary containing document date information.
                        Expected structure for date creation:

                        {
                            "version_date": str,       # ISO format date string (YYYY-MM-DD)
                            # Additional fields from document metadata:
                            # "label": str,            # Document label
                            # "version": str,          # Document version
                            # "status": str,           # Document status
                            # "template": str,         # Template name
                        }

                        Required fields:
                        - "version_date": Date when the protocol version became effective
                          (must be in ISO date format)

        Returns:
            None: Created date is stored in self._dates list

        Note:
            This method creates a GovernanceDate object with CDISC-compliant codes for
            protocol effective date type and global geographic scope. The created date
            is later combined with other dates in the study assembler.
        """
        try:
            if actual_date := self._encoder.to_date(data["version_date"]):
                protocol_date_code = self._builder.cdisc_code(
                    "C207598",
                    "Protocol Effective Date",
                )
                global_code = self._builder.cdisc_code("C68846", "Global")
                global_scope = self._builder.create(
                    GeographicScope, {"type": global_code}
                )
                protocol_date = self._builder.create(
                    GovernanceDate,
                    {
                        "name": "PROTOCOL-DATE",  # Internal name for the date
                        "type": protocol_date_code,  # CDISC code for date type
                        "dateValue": actual_date,
                        "geographicScopes": [global_scope],  # Global scope application
                    },
                )
                if protocol_date:
                    self._dates.append(protocol_date)
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
