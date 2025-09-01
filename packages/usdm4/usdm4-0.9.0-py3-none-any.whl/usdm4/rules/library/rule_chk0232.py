from usdm3.rules.library.rule_template import RuleTemplate


class RuleCHK0232(RuleTemplate):
    """
    CHK0232: A planned sex must ether include a single entry of male or female or both female and male as entries.

    Applies to: StudyDesignPopulation, StudyCohort
    Attributes: plannedSex
    """

    def __init__(self):
        super().__init__(
            "CHK0232",
            RuleTemplate.ERROR,
            "A planned sex must ether include a single entry of male or female or both female and male as entries.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
