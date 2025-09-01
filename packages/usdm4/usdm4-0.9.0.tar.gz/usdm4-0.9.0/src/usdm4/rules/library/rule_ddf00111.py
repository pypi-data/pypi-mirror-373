from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00111(RuleTemplate):
    """
    DDF00111: The unit of a planned age is expected to be specified using terms from the Age Unit (C66781) SDTM codelist.

    Applies to: StudyDesignPopulation, StudyCohort
    Attributes: plannedAge
    """

    def __init__(self):
        super().__init__(
            "DDF00111",
            RuleTemplate.ERROR,
            "The unit of a planned age is expected to be specified using terms from the Age Unit (C66781) SDTM codelist.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
