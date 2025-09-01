from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00129(RuleTemplate):
    """
    DDF00129: A study intervention's product designation must be specified using the product designation (C207418) DDF codelist.

    Applies to: StudyIntervention
    Attributes: productDesignation
    """

    def __init__(self):
        super().__init__(
            "DDF00129",
            RuleTemplate.ERROR,
            "A study intervention's product designation must be specified using the product designation (C207418) DDF codelist.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
