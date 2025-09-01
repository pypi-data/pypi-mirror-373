from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA

def interpretability(rulebase):
    score = len(rulebase.var)
    dico = {"warning" : "", "score" : score}
    return dico

CRITERIA.append(criterion(name="number of variables", category="fuzzy rule base", direction="min",
          active=True, func_interpretability=interpretability))
