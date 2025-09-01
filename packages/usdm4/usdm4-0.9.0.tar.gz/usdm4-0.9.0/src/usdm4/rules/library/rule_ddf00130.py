from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00130(RuleTemplate):
    """
    DDF00130: An agent administration's route must be specified according to the extensible Route of Administration Response (C66729) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).

    Applies to: AgentAdministration
    Attributes: route
    """

    def __init__(self):
        super().__init__(
            "DDF00130",
            RuleTemplate.ERROR,
            "An agent administration's route must be specified according to the extensible Route of Administration Response (C66729) SDTM codelist (e.g. an entry with a code or decode used from the codelist should be consistent with the full entry in the codelist).",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
