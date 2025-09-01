import fuzzic.interpretability.fuzzy_logic_manager as fuzzy_logic_manager
from fuzzic.configuration.config import config
from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA

def interpretability(rulebase):
    all_var = rulebase.used_variables
    war = ""
    all_results = []
    for key in all_var.keys():
        non_respect_complementarity = False
        var = all_var[key]
        Tv = var.all_sef
        for x in var.espace:
            somme = 0
            for S in Tv:
                somme += S.forward(x)
            somme = fuzzy_logic_manager.rounding(somme)
            if abs(somme - 1) > config.precision:
                non_respect_complementarity = True
                if war == "":
                    war += "complementarity not filled for variable " + str(var.label) + " and input : " + str(x) + ", somme des degré d'appartenance : " + str(somme)
        if non_respect_complementarity:
            all_results.append(0)
        else:
            all_results.append(1)
    result = fuzzy_logic_manager.criteria_aggregator(collection = all_results, 
                                direction = "max")
    score = fuzzy_logic_manager.rounding(result)
    dico = {"warning" : war, "score" : score}
    return dico

CRITERIA.append(criterion(name="complementarity", category="linguistic variables", direction="min",
          active=True, func_interpretability=interpretability))
