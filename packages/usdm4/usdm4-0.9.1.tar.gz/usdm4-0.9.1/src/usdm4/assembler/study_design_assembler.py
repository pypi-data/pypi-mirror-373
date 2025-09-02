from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4.assembler.base_assembler import BaseAssembler
from usdm4.assembler.population_assembler import PopulationAssembler
from usdm4.assembler.timeline_assembler import TimelineAssembler
from usdm4.assembler.encoder import Encoder
from usdm4.builder.builder import Builder
from usdm4.api.study_design import InterventionalStudyDesign


class StudyDesignAssembler(BaseAssembler):
    """
    Assembler responsible for creating InterventionalStudyDesign objects from study design data.

    This assembler processes study design information including intervention models, study phases,
    arms, epochs, cells, and other structural elements that define how the study is conducted.
    It creates the core study design structure that serves as the framework for the clinical trial.
    """

    MODULE = "usdm4.assembler.study_design_assembler.StudyDesignAssembler"

    def __init__(self, builder: Builder, errors: Errors):
        """
        Initialize the StudyDesignAssembler.

        Args:
            builder (Builder): The builder instance for creating USDM objects
            errors (Errors): Error handling instance for logging issues
        """
        super().__init__(builder, errors)
        self._encoder = Encoder(builder, errors)
        self._study_design = None

    def execute(
        self,
        data: dict,
        population_assembler: PopulationAssembler,
        timeline_assembler: TimelineAssembler,
    ) -> None:
        """
        Creates an InterventionalStudyDesign object from study design data.

        Args:
            data (dict): A dictionary containing study design information.
                        The data parameter must have the following structure:

                        {
                            "label": str,              # Human-readable label for the study design
                            "rationale": str,          # Rationale or justification for this design
                            "trial_phase": str,        # Clinical trial phase (e.g., "Phase I", "Phase II")
                            # Additional optional fields may include:
                            # "description": str,       # Detailed description of the study design
                            # "intervention_model": str, # Type of intervention model (parallel, crossover, etc.)
                            # "arms": list,             # List of study arms/treatment groups
                            # "epochs": list,           # List of study epochs/periods
                            # "cells": list,            # List of study cells (arm-epoch combinations)
                            # "objectives": list,       # List of study objectives
                            # "estimands": list,        # List of estimands for analysis
                            # "interventions": list,    # List of study interventions
                            # "analysis_populations": list,  # List of analysis population definitions
                        }

                        Required fields:
                        - "label": Display name for the study design
                        - "rationale": Explanation for why this design was chosen
                        - "trial_phase": The clinical development phase of the study

            population_assembler (PopulationAssembler): Assembler containing the study population
                definition that will be referenced by this study design
            timeline_assembler (TimelineAssembler): Assembler containing the timelines

        Returns:
            None: The created study design is stored in self._study_design property

        Note:
            The current implementation creates a basic interventional study design with:
            - Default parallel study intervention model (CDISC code C82639)
            - Empty lists for arms, cells, epochs, objectives, estimands, interventions, and analysis populations
            - Reference to the population from the population_assembler
            - Study phase from the input data
        """
        try:
            # Get CDISC code for parallel study intervention model (default)
            intervention_model_code = self._builder.cdisc_code(
                "C82639", "Parallel Study"
            )

            # Create the InterventionalStudyDesign object with basic structure
            self._study_design = self._builder.create(
                InterventionalStudyDesign,
                {
                    "name": self._label_to_name(data["label"]),
                    "label": data["label"],
                    "description": "A study design",
                    "rationale": data["rationale"],
                    "model": intervention_model_code,  # Default to parallel study model
                    "arms": [],  # Empty arms list (future enhancement)
                    "studyCells": [],  # Empty cells list (future enhancement)
                    "epochs": timeline_assembler.epochs,
                    "encounter": timeline_assembler.encounters,
                    "activities": timeline_assembler.activities,
                    "population": population_assembler.population,
                    "objectives": [],  # Empty objectives list (future enhancement)
                    "estimands": [],  # Empty estimands list (future enhancement)
                    "studyInterventions": [],  # Empty interventions list (future enhancement)
                    "analysisPopulations": [],  # Empty analysis populations list (future enhancement)
                    "studyPhase": self._encoder.phase(data["trial_phase"]),
                    "scheduleTimelines": timeline_assembler.timelines,
                },
            )
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "execute")
            self._errors.exception(
                "Failed during creation of study design", e, location
            )

    @property
    def study_design(self) -> InterventionalStudyDesign:
        return self._study_design
