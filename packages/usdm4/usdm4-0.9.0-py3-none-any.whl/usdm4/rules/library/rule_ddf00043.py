from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00043(RuleTemplate):
    """
    DDF00043: A unit must not be specified for a planned enrollment number or a planned completion number.

    Applies to: StudyDesignPopulation, StudyCohort
    Attributes: plannedEnrollmentNumber, plannedCompletionNumber
    """

    def __init__(self):
        super().__init__(
            "DDF00043",
            RuleTemplate.ERROR,
            "A unit must not be specified for a planned enrollment number or a planned completion number.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
