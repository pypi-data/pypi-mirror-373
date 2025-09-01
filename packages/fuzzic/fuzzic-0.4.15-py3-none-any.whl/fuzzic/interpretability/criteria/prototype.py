import os
import json
import fuzzic.interpretability.fuzzy_logic_manager as fuzzy_logic_manager
from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA

#TO CHECK

def interpretability(rulebase):
    all_var = rulebase.var
    war = ""
    total = 0
    nb_erreurs = 0
    
    specific_path = os.path.join(rulebase.study.study_directory, "specifics")
    prototype_file = os.path.join(specific_path, "prototypes.json")
    with open(prototype_file, "r") as f:
        prototypes = json.load(f)
    for key in all_var.keys():
        var = all_var[key]
        list_of_prototypes = prototypes[key]
        total += len(list_of_prototypes)

        Tv = var.all_sef
        for prototype in list_of_prototypes:
            if max([sef.forward(prototype) for sef in Tv]) < 1:
                if war =="":
                    war = "For variable " + str(var.label) + ", input " + str(prototype) + " does not belong to a fuzzy set with membership degree 1."
                nb_erreurs += 1
    nb_ok = total - nb_erreurs
    if total != 0:
        score = fuzzy_logic_manager.rounding(nb_ok / total)
    else:
        score = 1
    dico = {"warning" : war, "score" : score}
    return dico

CRITERIA.append(criterion(name="prototype", category="linguistic variables", direction="max",
          active=True, func_interpretability=interpretability))
