import traceback
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4.assembler.base_assembler import BaseAssembler
from usdm4.builder.builder import Builder
from usdm4.api.schedule_timeline import ScheduleTimeline
from usdm4.api.schedule_timeline_exit import ScheduleTimelineExit
from usdm4.api.scheduled_instance import ScheduledInstance, ScheduledActivityInstance
from usdm4.api.activity import Activity
from usdm4.api.study_epoch import StudyEpoch
from usdm4.api.encounter import Encounter
from usdm4.api.timing import Timing


class TimelineAssembler(BaseAssembler):
    MODULE = "usdm4.assembler.timeline_assembler.TimelineAssembler"

    def __init__(self, builder: Builder, errors: Errors):
        super().__init__(builder, errors)
        self._timelines: list[ScheduleTimeline] = []
        self._epochs: list[StudyEpoch] = []
        self._encounters: list[Encounter] = []
        self._activities: list[Activity] = []

    def execute(self, data: dict) -> None:
        try:
            self._epochs = self._add_epochs(data)
            self._encounters = self._add_encounters(data)
            self._activities = self._add_activities(data)
            instances = self._add_instances(data)
            timings = self._add_timing(data)
            self._link_timepoints_and_activities(data)
            tl = self._add_timeline(data, instances, timings)
            self._timelines.append(tl)
        except Exception as e:
            self._errors.exception(
                "Failed during creation of study design",
                e,
                KlassMethodLocation(self.MODULE, "execute"),
            )

    @property
    def timelines(self) -> list[ScheduleTimeline]:
        return self._timelines

    @property
    def encounters(self) -> list[Encounter]:
        return self._encounters

    @property
    def epochs(self) -> list[StudyEpoch]:
        return self._epochs

    @property
    def activities(self) -> list[Activity]:
        return self._activities

    def _add_epochs(self, data) -> list[ScheduledInstance]:
        try:
            results = []
            map = {}
            self._errors.debug(
                f"EPOCHS:\n{data['raw']}\n",
                KlassMethodLocation(self.MODULE, "_add_epochs"),
            )
            items = data["raw"]["epochs"]["period_columns"]
            table = data["final"]["table-001"]
            instances: dict = table["schedule_columns_data"]
            self._errors.debug(
                f"INSTANCES:\n{instances}\n",
                KlassMethodLocation(self.MODULE, "_add_epochs"),
            )
            instance_keys = list(instances.keys())
            for index, item in enumerate(items):
                label = item["text"]
                name = f"EPOCH-{label.upper()}"
                if name not in map:
                    epoch: StudyEpoch = self._builder.create(
                        StudyEpoch,
                        {
                            "name": name,
                            "description": f"EPOCH-{name}",
                            "label": label,
                            "type": self._builder.klass_and_attribute_value(
                                StudyEpoch, "type", "Treatment Epoch"
                            ),
                        },
                    )
                    results.append(epoch)
                    map[name] = epoch
                epoch = map[name]
                if index < len(instance_keys):
                    key = instance_keys[index]
                    instances[key]["epoch_instance"] = epoch
                else:
                    self._errors.warning(
                        f"Cannot align Epoch with timepoint {index + 1}",
                        KlassMethodLocation(self.MODULE, "_add_epochs"),
                    )
            self._errors.info(
                f"Epochs: {len(results)}",
                KlassMethodLocation(self.MODULE, "_add_epochs"),
            )
            return results
        except Exception as e:
            self._errors.exception(
                "Error creating Epochs",
                e,
                KlassMethodLocation(self.MODULE, "_add_epochs"),
            )

    def _add_encounters(self, data) -> list[Encounter]:
        try:
            results = []
            table = data["final"]["table-001"]
            instances: dict = table["schedule_columns_data"]
            # instance_keys = list(instances.keys())
            items: dict = table["grid_columns"]
            print(f"ENCOUNTER ITEMS: {items}")
            item: dict[str]
            for key, item in items.items():
                name = (
                    item["header_text"]
                    if item["header_text"].strip()
                    else instances[key]["timepoint_reference"]
                )
                print(f"ENCOUNTER NAME: {name}")
                encounter: Encounter = self._builder.create(
                    Encounter,
                    {
                        "name": f"ENCOUNTER-{name.upper()}",
                        "description": f"Encounter {name}",
                        "label": name,
                        "type": self._builder.klass_and_attribute_value(
                            Encounter, "type", "visit"
                        ),
                        "environmentalSettings": [
                            self._builder.klass_and_attribute_value(
                                Encounter, "environmentalSettings", "clinic"
                            )
                        ],
                        "contactModes": [
                            self._builder.klass_and_attribute_value(
                                Encounter, "contactModes", "In Person"
                            )
                        ],
                        "transitionStartRule": None,
                        "transitionEndRule": None,
                        "scheduledAtId": None,  # @todo
                    },
                )
                results.append(encounter)
                instances[key]["encounter_instance"] = encounter
            self._errors.info(
                f"Encounters: {len(results)}",
                KlassMethodLocation(self.MODULE, "_add_encounters"),
            )
            return results
        except Exception as e:
            self._errors.exception(
                "Error creating Encounters",
                e,
                KlassMethodLocation(self.MODULE, "_add_encounters"),
            )

    def _add_activities(self, data) -> list[Activity]:
        try:
            results = []
            table = data["final"]["table-001"]
            items: dict = table["activity_rows"]
            print(f"ACTIVITY ITEMS: {items}")
            item: dict[str]
            for key, item in items.items():
                params = {
                    "name": f"ACTIVITY-{item['activity_name'].upper()}",
                    "description": f"Activity {item['activity_name']}",
                    "label": item["activity_name"],
                    "definedProcedures": [],
                    "biomedicalConceptIds": [],
                    "bcCategoryIds": [],
                    "bcSurrogateIds": [],
                    "timelineId": None,
                }
                activity = self._builder.create(Activity, params)
                results.append(activity)
                item["activity_instance"] = activity
            self._errors.info(
                f"Activities: {len(results)}",
                KlassMethodLocation(self.MODULE, "_add_activities"),
            )
            self._builder.double_link(results, "nextId", "previousId")
            return results
        except Exception as e:
            print(f"ACTIVITIES EXCEPTION: {e}, {traceback.format_exc()}")
            self._errors.exception(
                "Error creating Activities",
                e,
                KlassMethodLocation(self.MODULE, "_add_activities"),
            )

    def _add_instances(self, data) -> list[ScheduledInstance]:
        try:
            results = []
            table = data["final"]["table-001"]
            items: dict = table["schedule_columns_data"]
            item: dict[str]
            for key, item in items.items():
                sai = self._builder.create(
                    ScheduledActivityInstance,
                    {
                        "name": f"SAI-{item['timepoint_reference'].upper()}",
                        "description": f"Scheduled activity instance {item['temporal_value']}",
                        "label": item["temporal_value"],
                        "timelineExitId": None,
                        "encounterId": item["encounter_instance"].id,
                        "scheduledInstanceTimelineId": None,
                        "defaultConditionId": None,
                        "epochId": item["epoch_instance"].id,
                        "activityIds": [],
                    },
                )
                item["sai_instance"] = sai
                results.append(sai)
            self._errors.info(
                f"SAI: {len(results)}",
                KlassMethodLocation(self.MODULE, "_add_instances"),
            )
            return results
        except Exception as e:
            print(f"INSTANCES EXCEPTION: {e}, {traceback.format_exc()}")
            self._errors.exception(
                "Error creating Scheduled Activity Instances",
                e,
                KlassMethodLocation(self.MODULE, "_add_instances"),
            )
            return []

    def _add_timing(self, data) -> list[ScheduledInstance]:
        try:
            results = []
            table = data["final"]["table-001"]
            items: dict = table["schedule_columns_data"]
            anchor_index, anchor_key = self._find_anchor(data)
            anchor: ScheduledInstance = items[anchor_key]["sai_instance"]
            item: dict[str]
            for key, item in items.items():
                index = int(item["timepoint_reference"])
                this_sai: ScheduledInstance = item["sai_instance"]
                if index < anchor_index:
                    self._timing(self, index, item, "Before", this_sai.id, anchor.id)
                elif index == anchor_index:
                    self._timing(
                        self, index, item, "Fixed Reference", this_sai.id, this_sai.id
                    )
                else:
                    self._timing(self, index, item, "After", anchor.id, this_sai.id)
            self._errors.info(
                f"Timing: {len(results)}",
                KlassMethodLocation(self.MODULE, "_add_timing"),
            )
            return results
        except Exception as e:
            self._errors.exception(
                "Error creating timings",
                e,
                KlassMethodLocation(self.MODULE, "_add_timing"),
            )
            return []

    def _timing(
        self, data: dict, index, int, type: str, from_id: str, to_id: str
    ) -> Timing:
        try:
            item: Timing = self._builder.create(
                Timing,
                {
                    "type": self._builder.klass_and_attribute_value(
                        Timing, "type", type
                    ),
                    "value": "ENCODE ???",  # @todo
                    "valueLabel": "???",  # @todo
                    "name": f"TIMING-{index}",
                    "description": f"Timing {index + 1}",
                    "label": "",
                    "relativeToFrom": self._builder.klass_and_attribute_value(
                        Timing, "relativeToFrom", "start to start"
                    ),
                    "windowLabel": "",  # @todo
                    "windowLower": "",  # @todo
                    "windowUpper": "",  # @todo
                    "relativeFromScheduledInstanceId": from_id,
                    "relativeToScheduledInstanceId": to_id,
                },
            )
            return item
        except Exception as e:
            self._errors.exception(
                "Error creating individual timing",
                e,
                KlassMethodLocation(self.MODULE, "_timing"),
            )
            return None

    def _find_anchor(self, data) -> int:
        table = data["final"]["table-001"]
        items = table["schedule_columns_data"]
        item: dict[str]
        for key, item in items.items():
            if item["temporal_dict"]["value"] == "1":
                return int(item["timepoint_reference"]), key
        return 0, list[items.keys()][0]

    def _link_timepoints_and_activities(self, data: dict) -> None:
        try:
            table = data["final"]["table-001"]
            items = table["scheduled_activities"]
            item: dict[str]
            activity_rows = table["activity_rows"]
            sai_instances = table["schedule_columns_data"]
            for key, item in items.items():
                activity: Activity = activity_rows[item["activity_id"]][
                    "activity_instance"
                ]
                sai_instance: ScheduledActivityInstance = sai_instances[item["col_id"]][
                    "sai_instance"
                ]
                sai_instance.activityIds.append(activity.id)
        except Exception as e:
            self._errors.exception(
                "Error linking timepoints and activities",
                e,
                KlassMethodLocation(self.MODULE, "_link_timepoints_and_activities"),
            )
            return None

    def _add_timeline(
        self, data, instances: list[ScheduledInstance], timings: list[Timing]
    ):
        try:
            self._errors.debug(
                f"Istances: {len(instances)}, Timings: {len(timings)}",
                KlassMethodLocation(self.MODULE, "_add_timeline"),
            )
            exit = self._builder.create(ScheduleTimelineExit, {})
            # duration = (
            #     self._builder.create(
            #         Duration,
            #         {
            #             "text": self.duration_text,
            #             "quantity": self.duration,
            #             "durationWillVary": False,
            #             "reasonDurationWillVary": "",
            #         },
            #     )
            #     if self.duration
            #     else None
            # )
            duration = None
            return self._builder.create(
                ScheduleTimeline,
                {
                    "mainTimeline": True,
                    "name": "MAIN-TIMELINE",
                    "description": "The main timeline",
                    "label": "Main timeline",
                    "entryCondition": "Paricipant identified",
                    "entryId": instances[0].id,
                    "exits": [exit],
                    "plannedDuration": duration,
                    "instances": instances,
                    "timings": timings,
                },
            )
        except Exception as e:
            print(f"TIMELINE EXCEPTION: {e}, {traceback.format_exc()}")
            self._errors.exception(
                "Error creating timeline",
                e,
                KlassMethodLocation(self.MODULE, "_add_timeline"),
            )
            return None
