from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4.assembler.base_assembler import BaseAssembler
from usdm4.assembler.encoder import Encoder
from usdm4.builder.builder import Builder
from usdm4.api.quantity_range import Quantity
from usdm4.api.geographic_scope import GeographicScope
from usdm4.api.subject_enrollment import SubjectEnrollment
from usdm4.api.study_amendment_reason import StudyAmendmentReason
from usdm4.api.study_amendment import StudyAmendment


class AmendmentsAssembler(BaseAssembler):
    MODULE = "usdm4.assembler.amendments_assembler.AmenementsAssembler"

    def __init__(self, builder: Builder, errors: Errors):
        super().__init__(builder, errors)
        self._encoder = Encoder(builder, errors)
        self._amendment = None

    def execute(self, data: dict) -> None:
        try:
            if data:
                self._amendment = self._create_amendment(data)
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "execute")
            self._errors.exception("Failed during creation of amendments", e, location)

    @property
    def amendment(self) -> StudyAmendment:
        return self._amendment

    def _create_amendment(self, data: dict) -> StudyAmendment:
        try:
            # print(f"DATA: {data}")
            reason = {}
            global_code = self._builder.cdisc_code("C68846", "Global")
            global_scope = self._builder.create(GeographicScope, {"type": global_code})
            for k, item in data["reasons"].items():
                # print(f"REASON_CODE: {k} = {item}")
                reason[k] = self._builder.create(
                    StudyAmendmentReason, self._encoder.amendment_reason(item)
                )
            impact = data["impact"]["safety"] or data["impact"]["reliability"]
            # print(f"IMPACT: {impact}")
            params = {
                "name": "AMENDMENT 1",
                "number": "1",
                "summary": data["summary"],
                "substantialImpact": impact,
                "primaryReason": reason["primary"],
                "secondaryReasons": [reason["secondary"]],
                "enrollments": [self._create_enrollment(data)],
                "geographicScopes": [global_scope],
            }
            return self._builder.create(StudyAmendment, params)
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "execute")
            self._errors.exception("Failed during creation of amendments", e, location)
            return None

    def _create_enrollment(self, data: dict):
        try:
            global_code = self._builder.cdisc_code("C68846", "Global")
            params = {
                "type": global_code,
                "code": None,
            }
            geo_scope = self._builder.create(GeographicScope, params)
            if "enrollment" in data:
                unit_alias = None
                if data["enrollment"]["unit"] == "%":
                    unit_code = self._builder.cdisc_code("C25613", "Percentage")
                    unit_alias = (
                        self._builder.alias_code(unit_code) if unit_code else None
                    )
                quantity = self._builder.create(
                    Quantity, {"value": data["enrollment"]["value"], "unit": unit_alias}
                )
                params = {
                    "name": "ENROLLMENT",
                    "forGeographicScope": geo_scope,
                    "quantity": quantity,
                }
            else:
                quantity = self._builder.create(Quantity, {"value": 0, "unit": None})
                params = {
                    "name": "ENROLLMENT",
                    "forGeographicScope": geo_scope,
                    "quantity": quantity,
                }
            return self._builder.create(SubjectEnrollment, params)
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "execute")
            self._errors.exception("Failed during creation of enrollments", e, location)
            return None
