from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0171(RuleTemplate):
    """
    CHK0171: An encounter's environmental setting must be specified according to the extensible Environmental Setting (C127262) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: Encounter
    Attributes: environmentalSettings
    """

    def __init__(self):
        super().__init__(
            "CHK0171",
            RuleTemplate.ERROR,
            "An encounter's environmental setting must be specified according to the extensible Environmental Setting (C127262) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
