from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00112(RuleTemplate):
    """
    DDF00112: A study intervention's role must be specified using the study intervention role (C207417) DDF codelist.

    Applies to: StudyIntervention
    Attributes: role
    """

    def __init__(self):
        super().__init__(
            "DDF00112",
            RuleTemplate.ERROR,
            "A study intervention's role must be specified using the study intervention role (C207417) DDF codelist.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
