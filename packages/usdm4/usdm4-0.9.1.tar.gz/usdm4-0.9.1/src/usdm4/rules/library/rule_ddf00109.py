from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00109(RuleTemplate):
    """
    DDF00109: A study element must only reference study interventions that are defined within the same study design as the study element.

    Applies to: StudyElement
    Attributes: studyInterventions
    """

    def __init__(self):
        super().__init__(
            "DDF00109",
            RuleTemplate.ERROR,
            "A study element must only reference study interventions that are defined within the same study design as the study element.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
