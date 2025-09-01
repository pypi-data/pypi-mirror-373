import fuzzic.interpretability.fuzzy_logic_manager as fuzzy_logic_manager
from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA

def interpretability(rulebase):
    rules = rulebase.rules
    result = fuzzy_logic_manager.criteria_aggregator(collection = [len(rules[key].premisse) + len(rules[key].conclusion) for key in rules.keys()],
                                direction = "min")
    dico = {"warning" : "", "score" : fuzzy_logic_manager.rounding(result)}
    return dico

CRITERIA.append(criterion(name="rule size", category="fuzzy rule", direction="min",
          active=True, func_interpretability=interpretability))
