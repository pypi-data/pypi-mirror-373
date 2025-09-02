from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00094(RuleTemplate):
    """
    DDF00094: Within a study version, if a date of a specific type exists with a global geographic scope then no other dates are expected with the same type.

    Applies to: StudyVersion
    Attributes: dateValues
    """

    def __init__(self):
        super().__init__(
            "DDF00094",
            RuleTemplate.ERROR,
            "Within a study version, if a date of a specific type exists with a global geographic scope then no other dates are expected with the same type.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
