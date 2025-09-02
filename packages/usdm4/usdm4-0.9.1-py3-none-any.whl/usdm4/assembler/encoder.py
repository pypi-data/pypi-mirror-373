import datetime
import dateutil.parser as parser
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4.builder.builder import Builder
from usdm4.api.alias_code import AliasCode
from usdm4.api.code import Code


class Encoder:
    MODULE = "usdm4.encoder.encoder.Encoder"
    PHASE_MAP = [
        (
            ["0", "PRE-CLINICAL", "PRE CLINICAL"],
            {"code": "C54721", "decode": "Phase 0 Trial"},
        ),
        (["1", "I"], {"code": "C15600", "decode": "Phase I Trial"}),
        (["1-2"], {"code": "C15693", "decode": "Phase I/II Trial"}),
        (["1/2"], {"code": "C15693", "decode": "Phase I/II Trial"}),
        (["1/2/3"], {"code": "C198366", "decode": "Phase I/II/III Trial"}),
        (["1/3"], {"code": "C198367", "decode": "Phase I/III Trial"}),
        (["1A", "IA"], {"code": "C199990", "decode": "Phase Ia Trial"}),
        (["1B", "IB"], {"code": "C199989", "decode": "Phase Ib Trial"}),
        (["2", "II"], {"code": "C15601", "decode": "Phase II Trial"}),
        (["2-3", "II-III"], {"code": "C15694", "decode": "Phase II/III Trial"}),
        (["2A", "IIA"], {"code": "C49686", "decode": "Phase IIa Trial"}),
        (["2B", "IIB"], {"code": "C49688", "decode": "Phase IIb Trial"}),
        (["3", "III"], {"code": "C15602", "decode": "Phase III Trial"}),
        (["3A", "IIIA"], {"code": "C49687", "decode": "Phase IIIa Trial"}),
        (["3B", "IIIB"], {"code": "C49689", "decode": "Phase IIIb Trial"}),
        (["4", "IV"], {"code": "C15603", "decode": "Phase IV Trial"}),
        (["5", "V"], {"code": "C47865", "decode": "Phase V Trial"}),
    ]
    STATUS_MAP = [
        (["APPROVED"], {"code": "C25425", "decode": "Approved"}),
        (["DRAFT", "DFT"], {"code": "C85255", "decode": "Draft"}),
        (["FINAL"], {"code": "C25508", "decode": "Final"}),
        (["OBSOLETE"], {"code": "C63553", "decode": "Obsolete"}),
        (
            ["PENDING", "PRENDING REVIEW"],
            {"code": "C188862", "decode": "Pending Review"},
        ),
    ]
    REASON_MAP = [
        {"code": "C207612", "decode": "Regulatory Agency Request To Amend"},
        {"code": "C207608", "decode": "New Regulatory Guidance"},
        {"code": "C207605", "decode": "IRB/IEC Feedback"},
        {"code": "C207609", "decode": "New Safety Information Available"},
        {"code": "C207606", "decode": "Manufacturing Change"},
        {"code": "C207602", "decode": "IMP Addition"},
        {"code": "C207601", "decode": "Change In Strategy"},
        {"code": "C207600", "decode": "Change In Standard Of Care"},
        {
            "code": "C207607",
            "decode": "New Data Available (Other Than Safety Data)",
        },
        {"code": "C207604", "decode": "Investigator/Site Feedback"},
        {"code": "C207611", "decode": "Recruitment Difficulty"},
        {
            "code": "C207603",
            "decode": "Inconsistency And/Or Error In The Protocol",
        },
        {"code": "C207610", "decode": "Protocol Design Error"},
        {"code": "C17649", "decode": "Other"},
        {"code": "C48660", "decode": "Not Applicable"},
    ]

    def __init__(self, builder: Builder, errors: Errors):
        self._builder: Builder = builder
        self._errors: Errors = errors

    def phase(self, text: str) -> AliasCode:
        phase = text.upper().replace("PHASE", "").strip() if text else ""
        for tuple in self.PHASE_MAP:
            if phase in tuple[0]:
                entry = tuple[1]
                cdisc_phase_code = self._builder.cdisc_code(
                    entry["code"],
                    entry["decode"],
                )
                self._errors.info(
                    f"Trial phase '{phase}' decoded as '{entry['code']}', '{entry['decode']}'",
                    location=KlassMethodLocation(self.MODULE, "phase"),
                )
                return self._builder.alias_code(cdisc_phase_code)
        cdisc_phase_code = self._builder.cdisc_code(
            "C48660",
            "[Trial Phase] Not Applicable",
        )
        self._errors.warning(
            f"Trial phase '{phase}' not decoded",
            location=KlassMethodLocation(self.MODULE, "phase"),
        )
        return self._builder.alias_code(cdisc_phase_code)

    def document_status(self, text: str) -> Code:
        status = text.upper().strip() if text else ""
        for tuple in self.STATUS_MAP:
            if status in tuple[0]:
                entry = tuple[1]
                cdisc_code = self._builder.cdisc_code(
                    entry["code"],
                    entry["decode"],
                )
                self._errors.info(
                    f"Document status '{status}' decoded as '{entry['code']}', '{entry['decode']}'",
                    location=KlassMethodLocation(self.MODULE, "document_status"),
                )
                return cdisc_code
        cdisc_code = self._builder.cdisc_code("C85255", "Draft")
        self._errors.warning(
            f"Document status '{status}' not decoded",
            location=KlassMethodLocation(self.MODULE, "document_status"),
        )
        return cdisc_code

    def amendment_reason(self, reason_str: str):
        if reason_str:
            parts = reason_str.split(":")
            # print(f"PARTS: {parts}")
            if len(parts) >= 2:
                reason_text = parts[1]
                # print(f"REASON: {reason_text}")
                for reason in self.REASON_MAP:
                    if reason_text in reason["decode"]:
                        self._errors.info(
                            f"Amendment reason '{reason_text}' decoded as '{reason['code']}', '{reason['decode']}'"
                        )
                        code = self._builder.cdisc_code(
                            reason["code"], reason["decode"]
                        )
                        return {"code": code, "other_reason": ""}
            self._errors.warning(
                f"Unable to decode amendment reason '{reason_str}'",
                location=KlassMethodLocation(self.MODULE, "amendment_reason"),
            )
            code = self._builder.cdisc_code("C17649", "Other")
            return {"code": code, "other_reason": parts[-1].strip()}
        self._errors.warning(
            "Amendment reason not decoded, missing text",
            location=KlassMethodLocation(self.MODULE, "amendment_reason"),
        )
        code = self._builder.cdisc_code("C17649", "Other")
        return {"code": code, "other_reason": "No reason text found"}

    def to_date(self, text: str) -> datetime.datetime | None:
        try:
            input_text = text.strip()
            if input_text:
                return parser.parse(input_text)
            else:
                return None
        except Exception as e:
            self._errors.exception(
                f"Failed to decode date text '{text}'",
                e,
                location=KlassMethodLocation(self.MODULE, "to_date"),
            )
            return None
