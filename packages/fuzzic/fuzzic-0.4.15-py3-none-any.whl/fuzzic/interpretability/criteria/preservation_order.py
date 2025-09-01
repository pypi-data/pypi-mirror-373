import os
import json
import fuzzic.interpretability.fuzzy_logic_manager as fuzzy_logic_manager
from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA

#TO CHECK

def interpretability(rulebase):
    all_var = rulebase.used_variables
    total_var = len(all_var)
    compteur_var_ok = len(all_var)
    war = ""
    
    specific_path = os.path.join(rulebase.study.study_directory, "specifics")
    label_orders_file = os.path.join(specific_path, "label_orders.json")
    
    with open(label_orders_file, "r") as g:
        all_ordre_des_labels = json.load(g)
        
    for key in all_var.keys():
        var = all_var[key]
        dico_ordre_des_labels = all_ordre_des_labels[key]
        
        if sum(dico_ordre_des_labels[k] for k in dico_ordre_des_labels.keys()) == 0:
            total_var -=1    
            compteur_var_ok -= 1
                    
        else:
            liste_ordre_des_labels = sorted(dico_ordre_des_labels, key=dico_ordre_des_labels.get)
            for i in range(len(liste_ordre_des_labels) -1):
                S1 = var.find_sef(liste_ordre_des_labels[i])
                S2 = var.find_sef(liste_ordre_des_labels[i+1])
                if not fuzzy_logic_manager.is_greater_than(S2, S1):
                    if war == "":
                        war +="SEF " + str(S1.label) + " est strictement plus grand que " + str(S2.label)
                    compteur_var_ok = compteur_var_ok - 1
                    break
    if total_var != 0:
        print("compteur_var_ok", compteur_var_ok)
        print("total_var", total_var)
        score = fuzzy_logic_manager.rounding(compteur_var_ok / total_var)
    else:
        score = 1
    dico = {"warning" : war, "score" : score}
    return dico

CRITERIA.append(criterion(name="preservation order", category="linguistic variables", direction="max",
          active=True, func_interpretability=interpretability))
