import fuzzic.interpretability.fuzzy_logic_manager as fuzzy_logic_manager
from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA

def interpretability(rulebase):
    dataset = rulebase.get_dataset()
    
    collection_of_activations = []
    for i in range (len(dataset.data)):
        nb_rules_activated = 0
        for key in rulebase.rules.keys():
            rule = rulebase.rules[key]
            activation = fuzzy_logic_manager.check_activation(rule, dataset.labels, dataset.data[i])
            if activation:
                nb_rules_activated += 1
        collection_of_activations.append(nb_rules_activated / len(rulebase.rules))

    result = fuzzy_logic_manager.criteria_aggregator(collection = collection_of_activations,
                                direction = "min")
    score = fuzzy_logic_manager.rounding(result)
    dico = {"warning" : "", "score" : score}
    return dico

CRITERIA.append(criterion(name="number rules activated", category="fuzzy rule base", direction="min",
          active=True, func_interpretability=interpretability))
