from itertools import groupby
from typing import List, Literal, Union
from .api_base_model import ApiBaseModelWithIdNameLabelAndDesc
from .schedule_timeline_exit import ScheduleTimelineExit
from .scheduled_instance import ScheduledActivityInstance, ScheduledDecisionInstance
from .timing import Timing
from .duration import Duration


class ScheduleTimeline(ApiBaseModelWithIdNameLabelAndDesc):
    mainTimeline: bool
    entryCondition: str
    entryId: str
    exits: List[ScheduleTimelineExit] = []
    timings: List[Timing] = []
    instances: List[Union[ScheduledActivityInstance, ScheduledDecisionInstance]] = []
    plannedDuration: Union[Duration, None] = None
    instanceType: Literal["ScheduleTimeline"]

    def first_timepoint(self) -> ScheduledActivityInstance:
        return self.instances[0] if self.instances else None

    def find_timepoint(self, id: str) -> ScheduledActivityInstance:
        return next((x for x in self.instances if x.id == id), None)

    def timepoint_list(self) -> list:
        return self.instances

    def find_timing_from(self, id: str) -> Timing:
        return next(
            (x for x in self.timings if x.relativeFromScheduledInstanceId == id), None
        )

    # @todo Nice to get StudyDesign type hint included but circular ...
    def soa(self, study_design) -> list:
        # Activities
        activity_order = study_design.activity_list()

        # Epochs and Visits
        ai = []
        timepoints = self.timepoint_list()
        for timepoint in timepoints:
            timing = self.find_timing_from(timepoint.id)
            encounter = study_design.find_encounter(timepoint.encounterId)
            epoch = study_design.find_epoch(timepoint.epochId)
            # print(f"TPT: {timepoint}")
            # print(f"ENCOUNTER: {encounter}")
            # print(f"EPOCH: {epoch}")
            entry = {
                "instance": timepoint,
                "timing": timing,
                "epoch": epoch,
                "encounter": encounter,
            }
            ai.append(entry)

        # Blank row
        visit_row = {}
        for item in ai:
            visit_row[item["instance"].id] = ""

        # Activities
        activities = {}
        for activity in activity_order:
            for timepoint in timepoints:
                if activity.id in timepoint.activityIds:
                    if activity.name not in activities:
                        activities[activity.name] = visit_row.copy()
                    activities[activity.name][timepoint.id] = "X"

        # Form results
        labels = []
        for item in ai:
            label = (
                item["encounter"].label if item["encounter"] else item["instance"].label
            )
            labels.append(label)
        results = []
        results.append(
            [""] + [item["epoch"].label if item["epoch"] else "&nbsp;" for item in ai]
        )
        results.append([""] + labels)
        results.append(
            [""]
            + [item["instance"].label if item["instance"] else "&nbsp;" for item in ai]
        )
        results.append(
            [""]
            + [
                item["timing"].windowLabel if item["timing"] else "&nbsp;"
                for item in ai
            ]
        )
        for activity in activity_order:
            if activity.name in activities:
                data = activities[activity.name]
                label = activity.label if activity.label else activity.name
                results.append(
                    [{"name": label, "id": activity.id}] + list(data.values())
                )

        # Format as HTML
        lines = []
        lines.append('<table class="soa-table table">')
        lines.append("<thead>")
        lines.append('<tr class="table-active">')
        epochs = [[i, len([*group])] for i, group in groupby(results[0])]
        text = '<td><p class="m-0 p-0"><small>&nbsp;</small></p></td>'
        for epoch in epochs[1:]:
            text += f'<td class="text-center" colspan="{epoch[1]}"><p class="m-0 p-0"><small>{epoch[0]}</small></p></td>'
        lines.append(text)
        lines.append("</tr>")
        for result in results[1:4]:
            lines.append('<tr class="table-active">')
            lines.append('<td><p class="m-0 p-0"><small>&nbsp;</small></p></td>')
            for cell in result[1:]:
                lines.append(
                    f'<td class="text-center"><p class="m-0 p-0"><small>{cell}</small></p></td>'
                )
            lines.append("</tr>")
        lines.append("</thead>")
        lines.append("<tbody>")
        for result in results[4:]:
            lines.append("<tr>")
            x = result[0]["name"]
            lines.append(
                f'<td class="m-0 p-0"><p class="m-0 p-0"><small>{x}</small></p></td>'
            )
            for cell in result[1:]:
                lines.append(
                    f'<td class="m-0 p-0 text-center"><p class="m-0 p-0"><small>{cell}</small></p></td>'
                )
            lines.append("</tr>")
        lines.append("</tbody>")
        lines.append("</table>")
        return ("\n").join(lines)
