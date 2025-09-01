import fuzzic.interpretability.fuzzy_logic_manager as fuzzy_logic_manager
from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA

def interpretability(rulebase):
    all_var = rulebase.var
    all_results = []
    for key in all_var.keys():
        var = all_var[key]
        Tv = var.all_sef
        all_cardinals = [s.cardinal for s in Tv]
        result = min(all_cardinals) / max(all_cardinals)
        #result = np.std(all_cardinals)
        all_results.append(result)

    final_result = fuzzy_logic_manager.criteria_aggregator(collection = all_results, 
                                        direction = "max")
    score = fuzzy_logic_manager.rounding(final_result)
    dico = {"warning" : "", "score" : score}
    return dico

CRITERIA.append(criterion(name="uniformity", category="linguistic variables", direction="max",
          active=True, func_interpretability=interpretability))
