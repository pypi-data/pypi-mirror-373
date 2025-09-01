import copy
import fuzzic.interpretability.fuzzy_logic_manager as fuzzy_logic_manager
from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA

def interpretability(rulebase):
    all_var = rulebase.var
    total = 0
    nb_erreurs = 0   
    war = ""
    for key in all_var.keys():
        var = all_var[key]
        all_extremas = copy.copy(var.bounds)
        total += len(all_extremas)
        Tv = var.all_sef
        for extrema in all_extremas:
            if max([sef.forward(extrema) for sef in Tv]) < 1:
                war ="For variable " + str(var.label) + ", input " + str(extrema) + " does not belong to a fuzzy set with membership degree 1."
                nb_erreurs += 1
    nb_ok = total - nb_erreurs
    score = fuzzy_logic_manager.rounding(nb_ok / total)
    dico = {"warning" : war, "score" : score}
    return dico

CRITERIA.append(criterion(name="extremas", category="linguistic variables", direction="max",
          active=True, func_interpretability=interpretability))
