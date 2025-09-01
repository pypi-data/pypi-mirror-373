import fuzzic.interpretability.fuzzy_logic_manager as fuzzy_logic_manager
from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA

def interpretability(rulebase):
    dataset = rulebase.get_dataset()
    nb_data_actifs = 0
    war = ""
    
    for i in range(len(dataset.data)):
        input_activated = False
        for key in rulebase.rules.keys():
            rule = rulebase.rules[key]
            activation = fuzzy_logic_manager.check_activation(rule, dataset.labels, dataset.data[i])
            if activation:
                nb_data_actifs += 1
                input_activated = True
                break
        if not input_activated and war == "":
            war += "data : "
            j = 0
            for key in rulebase.var.keys():
                war += rulebase.var[key].label + " : " + str(fuzzy_logic_manager.rounding(float(dataset.data[i][j]))) + ", "
                j +=1
            war += " not activated in the rulebase."
    score = fuzzy_logic_manager.rounding(nb_data_actifs / len(dataset.data))
    dico = {"warning" : war, "score" : score}
    return dico

CRITERIA.append(criterion(name="completeness", category="fuzzy rule base", direction="max",
          active=True, func_interpretability=interpretability))
