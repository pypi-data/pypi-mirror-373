import os
import fuzzic.interpretability.fuzzy_logic_manager as fuzzy_logic_manager
from fuzzic.interpretability.interpretability_manager import criterion, CRITERIA

def interpretability(rulebase):
    
    def import_similar_var(rulebase):
        specifics_file = os.path.join(rulebase.study.study_directory, "specifics")
        similar_var_file = os.path.join(specifics_file, "similar_variables.dat")
        
        similar_liste = []
        new_liste = []
        with open(similar_var_file, 'r') as fichier:
            mots = fichier.readlines()
            # Supprimer les caractères de nouvelle ligne
            mots = [mot.strip() for mot in mots]
            for j in range(len(mots)):
                mot = mots[j]
                if mot != "":
                    new_liste.append(mot)
                else:
                    j+=1
                    similar_liste.append(new_liste)
                    new_liste = []
            similar_liste.append(new_liste)
        return similar_liste
    
    all_liste_var_similaires = import_similar_var(rulebase)
    if sum([len(x) for x in all_liste_var_similaires]) == 0:
        dico = {"warning" : "", "score" : 1}
    else:
        all_results = []
        warning = ""
        for liste_var_similaires in all_liste_var_similaires:
            if len(liste_var_similaires) >= 2:
                for i in range(len(liste_var_similaires)-1):
                    for j in range(i+1, len(liste_var_similaires)):
                        var1 = rulebase.get_var(liste_var_similaires[i])
                        var2 = rulebase.get_var(liste_var_similaires[j])
                        result_intermediaire = []
                        for sef1 in var1.all_sef:
                            maxx = -1
                            for sef2 in var2.all_sef:
                                the_similarity = fuzzy_logic_manager.similarity(sef1, sef2)
                                maxx = max(maxx, the_similarity)
                            result_intermediaire.append(maxx)
                        
                        result = fuzzy_logic_manager.criteria_aggregator(collection = result_intermediaire, 
                                                    direction = "max")
                        if result == -1:
                            warning += "variable " + var1.label + " and " + var2.label + " not sharing the same universe.\n"
                        all_results.append(result)
        print(all_results)
        final_result = fuzzy_logic_manager.criteria_aggregator(collection = all_results, 
                                    direction = "max")
        if final_result == -1:
            final_result = 0
        score = fuzzy_logic_manager.rounding(final_result)
        dico = {"warning" : warning, "score" : score}
    return dico

CRITERIA.append(criterion(name="membership function sharing", category="fuzzy rule base", direction="max",
          active=True, func_interpretability=interpretability))
