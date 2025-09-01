import fuzzic.interpretability.fuzzy_logic_manager as fuzzy_logic_manager
from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA

def interpretability(rulebase):
    all_var = rulebase.var
    all_results = []
    for key in all_var.keys():
        var = all_var[key]
        Tv = var.all_sef
        for i in range(len(Tv)-1):
            for j in range(i+1, len(Tv)):
                sim = fuzzy_logic_manager.similarity(Tv[i], Tv[j])
                #print("similarity between ", Tv[i].label, "and", Tv[j].label, "is", str(sim))
                all_results.append(sim)
    result = fuzzy_logic_manager.criteria_aggregator(collection = all_results, 
                                direction = "min")
    dico = {"warning" : "", "score" : fuzzy_logic_manager.rounding(result)}
    return dico

CRITERIA.append(criterion(name="distinguishability", category="linguistic variables", direction="min",
          active=True, func_interpretability=interpretability))
