from typing import List, Literal, Union
from .activity import Activity
from .api_base_model import ApiBaseModelWithIdNameLabelAndDesc
from .alias_code import AliasCode
from .biospecimen_retention import BiospecimenRetention
from .code import Code
from .encounter import Encounter
from .study_cell import StudyCell
from .indication import Indication
from .study_arm import StudyArm
from .study_epoch import StudyEpoch
from .study_element import StudyElement
from .population_definition import StudyDesignPopulation
from .eligibility_criterion import EligibilityCriterion
from .analysis_population import AnalysisPopulation
from .objective import Objective
from .schedule_timeline import ScheduleTimeline
from .estimand import Estimand
from .comment_annotation import CommentAnnotation


class StudyDesign(ApiBaseModelWithIdNameLabelAndDesc):
    studyType: Union[Code, None] = None
    studyPhase: Union[AliasCode, None] = None
    therapeuticAreas: List[Code] = []
    characteristics: List[Code] = []
    encounters: List[Encounter] = []
    activities: List[Activity] = []
    arms: List[StudyArm]
    studyCells: List[StudyCell]
    rationale: str
    epochs: List[StudyEpoch]
    elements: List[StudyElement] = []
    estimands: List[Estimand] = []
    indications: List[Indication] = []
    studyInterventionIds: List[str] = []
    objectives: List[Objective] = []
    population: StudyDesignPopulation
    scheduleTimelines: List[ScheduleTimeline] = []
    biospecimenRetentions: List[BiospecimenRetention] = []
    documentVersionIds: List[str] = []
    eligibilityCriteria: List[EligibilityCriterion] = []
    analysisPopulations: List[AnalysisPopulation] = []
    notes: List[CommentAnnotation] = []
    instanceType: Literal["StudyDesign"]

    def main_timeline(self):
        return next(
            (item for item in self.scheduleTimelines if item.mainTimeline), None
        )

    def phase(self) -> Code:
        try:
            return self.studyPhase.standardCode
        except Exception:
            return None

    def phase_as_text(self) -> str:
        code = self.phase()
        return code.decode if code else ""

    def soa(self, timeline_name: str) -> list:
        timeline = next(
            (x for x in self.scheduleTimelines if x.name == timeline_name), None
        )
        return timeline.soa() if timeline else None

    def main_soa(self) -> list:
        timeline = next((x for x in self.scheduleTimelines if x.mainTimeline), None)
        return timeline.soa() if timeline else None

    def first_activity(self) -> Activity:
        return next((x for x in self.activities if not x.previousId and x.nextId), None)

    def find_activity(self, id: str) -> Activity:
        return next((x for x in self.activities if x.id == id), None)

    def activity_list(self) -> list:
        items = []
        item = self.first_activity()
        while item:
            items.append(item)
            item = self.find_activity(item.nextId)
        return items

    def find_epoch(self, id: str) -> StudyEpoch:
        return next((x for x in self.epochs if x.id == id), None)

    def find_encounter(self, id: str) -> Encounter:
        return next((x for x in self.encounters if x.id == id), None)

    def find_timeline(self, id: str) -> ScheduleTimeline:
        return next((x for x in self.scheduleTimelines if x.id == id), None)

    def find_analysis_population(self, id: str) -> AnalysisPopulation:
        return next((x for x in self.analysisPopulations if x.id == id), None)

    def criterion_map(self) -> dict[EligibilityCriterion]:
        return {x.id: x for x in self.eligibilityCriteria}


class InterventionalStudyDesign(StudyDesign):
    subTypes: List[Code] = []
    model: Code
    intentTypes: List[Code] = []
    blindingSchema: Union[AliasCode, None] = None
    instanceType: Literal["InterventionalStudyDesign"]


class ObservationalStudyDesign(StudyDesign):
    subTypes: List[Code] = []
    model: Code
    timePerspective: Code
    samplingMethod: Union[Code, None] = None
    instanceType: Literal["ObservationalStudyDesign"]
