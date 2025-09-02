from usdm3.rules.library.rule_template import RuleTemplate


class RuleDDF00088(RuleTemplate):
    """
    DDF00088: Epoch ordering using previous and next attributes is expected to be consistent with the order of corresponding scheduled activity instances according to their specified default conditions.

    Applies to: StudyEpoch
    Attributes: previous, next
    """

    def __init__(self):
        super().__init__(
            "DDF00088",
            RuleTemplate.ERROR,
            "Epoch ordering using previous and next attributes is expected to be consistent with the order of corresponding scheduled activity instances according to their specified default conditions.",
        )

    def validate(self, config: dict) -> bool:
        raise NotImplementedError("rule is not implemented")
