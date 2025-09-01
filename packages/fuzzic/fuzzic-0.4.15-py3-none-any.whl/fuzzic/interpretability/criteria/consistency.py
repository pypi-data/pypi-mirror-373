import fuzzic.interpretability.fuzzy_logic_manager as fuzzy_logic_manager
from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA

def interpretability(rulebase):
    def check_two_premisses(pre1, pre2):
        representation1 = hash(repr({t.sef.var.label + t.sef.label for t in pre1}))
        representation2 = hash(repr({t.sef.var.label + t.sef.label for t in pre2}))
        return representation1 == representation2
    
    def check_same_premisse_give_same_conclusion(rules):
        all_results = []
        for i in range(len(rules)-1):
            for j in range(i+1, len(rules)):
                if check_two_premisses(rules[i].premisse, rules[j].premisse):
                    for t1 in rules[i].conclusion:
                        for t2 in rules[j].conclusion:
                            if t1.var.ident == t2.var.ident and t1.sef.ident != t2.sef.ident:
                                U = 0
                                V = 0
                                U_union_V = 0
                                for x in t1.sef.var.espace:
                                    y1 = t1.sef.forward(x)
                                    y2 = t2.sef.forward(x)
                                    U += y1
                                    V += y2
                                    U_union_V += fuzzy_logic_manager.t_norm(y1, y2)
                                all_results.append(U_union_V/(min(U,V)))
        
        if len(all_results) == 0:
            all_results = [1]
        return all_results
            
    rules = [rulebase.rules[key] for key in rulebase.rules.keys()]
    all_results = check_same_premisse_give_same_conclusion(rules)
    score = fuzzy_logic_manager.criteria_aggregator(collection = all_results, 
                                direction = "max")
    dico = {"warning" : "", "score" : fuzzy_logic_manager.rounding(score)}
    return dico

CRITERIA.append(criterion(name="consistency", category="fuzzy rule base", direction="max",
          active=True, func_interpretability=interpretability))
