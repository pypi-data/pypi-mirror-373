import fuzzic.interpretability.fuzzy_logic_manager as fuzzy_logic_manager
from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA

def interpretability(rulebase):
    all_results = []
    for key in rulebase.var.keys():
        var = rulebase.var[key]
        Tv = var.all_sef
        taille = len(Tv)
        all_results.append(taille)
    result = fuzzy_logic_manager.criteria_aggregator(collection = all_results, 
                                direction = "min")
    dico = {"warning" : "", "score" : fuzzy_logic_manager.rounding(result)}
    return dico
CRITERIA.append(criterion(name="justifiable number of elements", category="linguistic variables", direction="min",
          active=True, func_interpretability=interpretability))
