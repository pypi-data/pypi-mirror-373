from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0199(RuleTemplate):
    """
    CHK0199: An administration's frequency must be specfied according to the extensible Frequency (C71113) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: Administration
    Attributes: frequency
    """

    def __init__(self):
        super().__init__(
            "CHK0199",
            RuleTemplate.ERROR,
            "An administration's frequency must be specfied according to the extensible Frequency (C71113) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
