from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00078(RuleTemplate):
    """
    DDF00078: If a transition start rule is defined then an end rule is expected and vice versa.

    Applies to: StudyElement, Encounter
    Attributes: transitionStartRule, transitionEndRule
    """

    def __init__(self):
        super().__init__(
            "DDF00078",
            RuleTemplate.ERROR,
            "If a transition start rule is defined then an end rule is expected and vice versa.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
