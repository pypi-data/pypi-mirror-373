from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4.assembler.base_assembler import BaseAssembler
from usdm4.builder.builder import Builder
from usdm4.api.population_definition import StudyDesignPopulation
from usdm4.api.eligibility_criterion import (
    EligibilityCriterion,
    EligibilityCriterionItem,
)


class PopulationAssembler(BaseAssembler):
    """
    Assembler responsible for processing population-related data and creating StudyDesignPopulation objects.

    This assembler handles the creation of study population definitions, including population criteria,
    cohort definitions, and subject enrollment information. It processes population data from the
    input structure and creates the appropriate USDM population objects.
    """

    MODULE = "usdm4.assembler.population_assembler.PopulationAssembler"

    def __init__(self, builder: Builder, errors: Errors):
        """
        Initialize the PopulationAssembler.

        Args:
            builder (Builder): The builder instance for creating USDM objects
            errors (Errors): Error handling instance for logging issues
        """
        super().__init__(builder, errors)
        self._population = None
        self._cohorts = []
        self._ec_items = []
        self._eci_items = []

    def execute(self, data: dict) -> None:
        """
        Processes population data and creates a StudyDesignPopulation object.

        Args:
            data (dict): A dictionary containing population definition data.
                        The data parameter must have the following structure:

                        {
                            "label": str,              # Human-readable label for the population
                            "inclusion_exclusion: {
                                "inclusion": list[str],
                                "exclusion": list[str],
                            }
                            # Additional optional fields may be includes in the future:
                            # "criteria": list,         # List of eligibility criteria
                            # "cohorts": list,          # List of population cohorts/subgroups
                            # "enrollment": dict,       # Subject enrollment information
                            # "analysis_populations": list  # Analysis population definitions
                        }

                        Required fields:
                        - "label": A string that provides a human-readable name for the population.
                          This will be used to generate both the display label and the internal name
                          (converted to uppercase with spaces replaced by hyphens).

                        The current implementation creates a basic population definition with:
                        - name: Generated from label (uppercase, spaces -> hyphens)
                        - label: Direct copy of the input label
                        - description: Default placeholder text
                        - includesHealthySubjects: Default to True
                        - criteria: Empty list (to be populated by future enhancements)

        Returns:
            None: The created population is stored in self._population property

        Raises:
            Exception: If population creation fails, logged via error handler
        """
        try:
            self._ie(data["inclusion_exclusion"])

            # Extract required label field and create population parameters
            # The label is used for both display purposes and name generation
            params = {
                "name": data["label"]
                .upper()
                .replace(" ", "-"),  # Convert label to internal name format
                "label": data["label"],  # Keep original label for display
                "description": "The study population, currently blank",  # Default description
                "includesHealthySubjects": True,  # Default assumption
                "criteria": self._ec_items,
            }

            # Create the StudyDesignPopulation object using the builder
            self._population = self._builder.create(StudyDesignPopulation, params)

        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "execute")
            self._errors.exception("Failed during creation of population", e, location)

    @property
    def population(self) -> StudyDesignPopulation:
        return self._population

    @property
    def criteria_items(self) -> list[EligibilityCriterionItem]:
        return self._eci_items

    def _ie(self, criteria: dict) -> None:
        self._collection(
            criteria["inclusion"], "C25532", "INCLUSION", "INC", "Inclusion"
        )
        self._collection(
            criteria["exclusion"], "C25370", "EXCLUSION", "EXC", "Exclusion"
        )

    def _collection(
        self, criteria: list[str], code: str, decode: str, prefix: str, label: str
    ) -> None:
        for index, text in enumerate(criteria):
            try:
                category = self._builder.cdisc_code(code, decode)
                params = {
                    "name": f"{prefix}-I{index + 1}",
                    "label": f"{label} item {index + 1} ",
                    "description": "",
                    "text": text,
                }
                eci_item = self._builder.create(EligibilityCriterionItem, params)
                self._eci_items.append(eci_item)
                params = {
                    "name": f"{prefix}{index + 1}",
                    "label": f"{label} criterion {index + 1} ",
                    "description": "",
                    "criterionItemId": eci_item.id,
                    "category": category,
                    "identifier": f"{index + 1}",
                }
                self._ec_items.append(
                    self._builder.create(EligibilityCriterion, params)
                )
            except Exception as e:
                location = KlassMethodLocation(self.MODULE, "_collection")
                self._errors.exception(
                    f"Failed during creation of criterion '{text}", e, location
                )
