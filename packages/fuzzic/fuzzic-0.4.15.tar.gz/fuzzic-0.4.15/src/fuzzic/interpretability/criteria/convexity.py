import fuzzic.interpretability.fuzzy_logic_manager as fuzzy_logic_manager
from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA

def interpretability(rulebase):
    all_sef = rulebase.get_all_sef()
    total = len(all_sef)
    compteur = len(all_sef)
    war = ""
    for sef in all_sef:
        if sef.shape == "gaussian":
            war = "Gaussian are not convex."
            compteur = compteur - 1
    dico = {"warning" : war, "score" : fuzzy_logic_manager.rounding(compteur / total)}
    return dico

CRITERIA.append(criterion(name="convexity", category="fuzzy set", direction="max",
          active=True, func_interpretability=interpretability))
