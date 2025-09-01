import fuzzic.interpretability.fuzzy_logic_manager as fuzzy_logic_manager
from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA
from fuzzic.configuration.config import config

def interpretability(rulebase):
    alpha = config.alpha_coverage
    all_var = rulebase.var
    war = ""
    total_inputs = 0
    total_pas_couverts = 0
    
    for key in all_var.keys():
        var = all_var[key]
        Tv = var.all_sef
        for x in var.espace:
            total_inputs += 1
            cover = False
            for S in Tv:
                if S.forward(x) > alpha:
                    cover = True
            if cover is False:
                total_pas_couverts += 1
                if war == "":
                    war += "Input " + str(fuzzy_logic_manager.rounding(x)) + " for variable " + str(var.label) + " is not covered by a fuzzy set with a membership degree of at least: " + str(alpha)
                
    total_couverts = total_inputs - total_pas_couverts
    dico = {"warning" : war, "score" : fuzzy_logic_manager.rounding(total_couverts / total_inputs)}
    return dico

CRITERIA.append(criterion(name="coverage", category="linguistic variables", direction="max",
          active=True, func_interpretability=interpretability))
