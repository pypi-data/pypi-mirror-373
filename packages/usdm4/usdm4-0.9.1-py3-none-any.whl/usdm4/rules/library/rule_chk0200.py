from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0200(RuleTemplate):
    """
    CHK0200: An administration's route must be specfied according to the extensible Route of Administration Response (C66729) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: Administration
    Attributes: route
    """

    def __init__(self):
        super().__init__(
            "CHK0200",
            RuleTemplate.ERROR,
            "An administration's route must be specfied according to the extensible Route of Administration Response (C66729) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
