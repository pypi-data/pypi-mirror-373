from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00101(RuleTemplate):
    """
    DDF00101: Within a study design, if study type is Interventional then at least one intervention is expected to be referenced from a procedure.

    Applies to: Procedure
    Attributes: studyIntervention
    """

    def __init__(self):
        super().__init__(
            "DDF00101",
            RuleTemplate.ERROR,
            "Within a study design, if study type is Interventional then at least one intervention is expected to be referenced from a procedure.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
