import fuzzic.interpretability.fuzzy_logic_manager as fuzzy_logic_manager
from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA

def interpretability(rulebase):
    total = 0
    compteur = 0
    war = ""
    all_var = rulebase.used_variables
    for key in all_var.keys():
        all_sef = rulebase.var[key].all_sef
        for sef in all_sef:
            total += 1
            if sef.hauteur_y < 1:
                war ="Le SEF : " + str(sef.label) + " de la variable " + str(sef.var.label) + " n'a pas une hauteur de 1 mais une hauteur de : " + str(sef.hauteur_y)
                compteur += 1
    
    dico = dict()
    dico["warning"] = war
    dico["score"] = fuzzy_logic_manager.rounding( (total - compteur) / total)
    return dico

CRITERIA.append(criterion(name="normality", category="fuzzy sets", direction="max",
          active=True, func_interpretability=interpretability))
