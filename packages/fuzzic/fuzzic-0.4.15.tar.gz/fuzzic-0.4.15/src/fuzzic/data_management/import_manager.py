import sys
import xml.etree.ElementTree as ET
import os
import fuzzic.interpretability.rulebase as rbm



# IMPORT DATASET ==============================================================

def import_dataset(filepath):
    """
    Returns a Dataset object from the given filepath

    Parameters
    ----------
    filepath : str
        path of the dataset file.

    Returns
    -------
    dataset
        a dataset object from fuzzic.interpretability.rulebase.py
    """
    
    with open(filepath, "r") as f:
        read_data = []
        ligne = f.readline()
        while ligne != "":
            ligne = ligne[:len(ligne)-1]
            if ligne != "" and ligne != "\n":
                read_data.append(ligne)
            ligne = f.readline()
        datalist = [read_data[i].split(",") for i in range(len(read_data))]
    the_dataset_object = rbm.Dataset(datalist)
    return the_dataset_object



def import_rulebase(filepath, specified_dataset = None):
    """
    Returns a rulebase object from the given filepath

    Parameters
    ----------
    filepath : str
        path of the rulebase file, either fispro or XML type file.
    specified_dataset : str or Dataset object
        a given dataset either already in a Dataset object, or the filepath of it.

    Returns
    -------
    rulebase
        a Rulebase object from fuzzic.interpretability.rulebase.py
    """
    
    typefile = os.path.splitext(filepath)[1]
    
    if typefile == ".fis":
        rb = import_fispro(filepath)
        if type(specified_dataset) is str:
            rb.dataset = import_dataset(specified_dataset)
        else:
            rb.dataset = specified_dataset
        return rb   
    
    elif typefile == ".xml":
        rb = import_xml(filepath)
        if type(specified_dataset) is str:
            rb.dataset = import_dataset(specified_dataset)
        else:
            rb.dataset = specified_dataset
        return rb
    else:
        print("Unknown rule base file format.", file=sys.stderr, flush=True)
        return None

# IMPORT RULEBASE FROM TREE, XML OR FISPRO ==========================================

def import_xml(filepath):
    """
    Returns a rulebase object from the given filepath of a XML file.

    Parameters
    ----------
    filepath : str
        path of the XML file representing a rulebase.

    Returns
    -------
    rulebase
        a Rulebase object from fuzzic.interpretability.rulebase.py
    """
    tree = ET.parse(filepath)
    return import_tree(tree, filepath=filepath)


def import_tree(tree, filepath=None):
    """
    Returns a rulebase object from a xml.etree.ElementTree.

    Parameters
    ----------
    tree : ElementTree from xml.etree.ElementTree
        A tree representation of an XML file.
    filepath : str
        path of the origin rulebase XML file if available.

    Returns
    -------
    rulebase
        a Rulebase object from fuzzic.interpretability.rulebase.py
    """
    
    root = tree.getroot()
    
    rule_base = rbm.Rulebase()
    if filepath is not None:
        rule_base.filename = os.path.basename(filepath)
    
    for label in root.iter("label"):
        rule_base.label = label.text
        break
    
    for var in root.iter("variable"):
        var_bounds = [float(var[1][0].text), float(var[1][1].text)]
        
        one_variable = rbm.Variable(label = str(var[0].text),
                                rulebase = rule_base,
                                unit = str(var[1].attrib["unit"]),
                                bounds = var_bounds,
                                all_sef = [],
                                ident = str(var.attrib["ident"]))
        
        for sef in var.iter("sef"):
            
            all_points = []
            is_linear = False
            for point in sef.iter("point"):
                is_linear = True
                P = rbm.Point(float(point[0].text), float(point[1].text))
                all_points.append(P)
            if is_linear:
                if len(all_points) == 1:
                    the_forme = "one_point"
                elif len(all_points) == 3:
                    if all_points[0].y == all_points[2].y:
                        the_forme = "triangle"
                    else:
                        the_forme = "trapeze"
                else:
                    assert len(all_points) == 4, "Forme inconnu du SEF."
                    the_forme = "trapeze"
                one_sef = rbm.Sef(label = str(sef[0].text),
                              shape = the_forme,
                              var = one_variable,
                              points = all_points,
                              ident = str(sef.attrib["ident"]))
            else:
                for gaus in sef.iter("gaussian"):
                    deviation = float(gaus[1].text)
                    if deviation == 0:
                        one_point = rbm.Point(x = float(gaus[0].text), y = 1)
                        one_sef = rbm.Sef(label = str(sef[0].text),
                                      shape = "one_point",
                                      var = one_variable,
                                      points = [one_point],
                                      ident = str(sef.attrib["ident"]))
                    else:
                        G = rbm.Gaussian(mean = float(gaus[0].text), 
                                     deviation = float(gaus[1].text))
                    one_sef = rbm.Sef(label = str(sef[0].text),
                                  shape = "gaussian",
                                  var = one_variable,
                                  gaussian = G,
                                  ident = str(sef.attrib["ident"]))
            
            one_variable.all_sef.append(one_sef)
        
        rule_base.var[one_variable.ident] = one_variable
                
    for rule in root.iter("rule"):
        idd = str(rule.attrib["ident"])
        one_rule = rbm.Rule(ident = idd,
                        premisse = set(),
                        conclusion = set())
        assert len(one_rule.conclusion) == 0
        for premise in rule.iter("premise"):
            the_var = rule_base.var[str(premise[0].text)]
            for sef in the_var.all_sef:
                if sef.ident == str(premise[1].text):
                    the_sef = sef
                    break
            one_term = rbm.Term(var = the_var, 
                            sef = the_sef)
            one_rule.premisse.add(one_term)
        
        for conclusion in rule.iter("conclusion"):
            the_var = rule_base.var[str(conclusion[0].text)]
            for sef in the_var.all_sef:
                if sef.ident == str(conclusion[1].text):
                    the_sef = sef
                    break
            one_term = rbm.Term(var = the_var, 
                            sef = the_sef)
            one_rule.conclusion.add(one_term)
        
        rule_base.rules[str(rule.attrib["ident"])] = one_rule  
    
    rule_base.used_variables = rule_base.get_used_variables()
    
    return rule_base





def import_fispro(filepath):
    """
    Returns a rulebase object from a FisPro file

    Parameters
    ----------
    filepath : str
        path of a FisPro file.

    Returns
    -------
    rulebase
        a Rulebase object from fuzzic.interpretability.rulebase.py
    """
        
    def type_of_line(line):
        i = 0
        while line[i] != "=":
            i += 1
        return str(line[:i])
        
    def recup_value(line):
        i = 0
        while line[i] != "=":
            i += 1
        return eval(line[i+1:])
    
    def traitement_variable(all_lines, indice_line, numero_var):
        assert indice_line > 8, "probablement pas la ligne de variable (paragraphe de description de la base de règle)."
        i = indice_line + 1
        while all_lines[i] != "\n":
            line = all_lines[i]
            t = type_of_line(line)
            if t == "Name":
                the_label = recup_value(line)
            elif t == "Range":
                the_bounds = eval(str(recup_value(line)))              
                one_variable = rbm.Variable(label = the_label,
                                        rulebase = None,
                                        unit = "N/A",
                                        bounds = the_bounds,
                                        all_sef = [],
                                        ident = "Var_" + str(numero_var))
            elif t[:2] == "MF":
                value = recup_value(line)
                the_label = value[0]
                the_points_x = value[2]
                assert value[1] in ["SemiTrapezoidalInf","SemiTrapezoidalSup", "triangular", "trapezoidal", "gaussian"], "The shape is not known :" + str(value[1])
                
                if value[1] == "gaussian":
                    the_forme = "gaussian"
                    G = rbm.Gaussian(mean = the_points_x[0], deviation = the_points_x[1])
                    one_sef = rbm.Sef(label = the_label,
                                  forme = the_forme,
                                  var = one_variable,
                                  gaussian = G,
                                  ident = "var_" + str(numero_var) + "_sef_" + str(t[2]))
                else:
                    if value[1] == "SemiTrapezoidalInf":
                        P1 = rbm.Point(x = the_points_x[0], y = 1)
                        P2 = rbm.Point(x = the_points_x[1], y = 1)
                        P3 = rbm.Point(x = the_points_x[2], y = 0)
                        the_points = [P1, P2, P3]
                        the_forme = "trapeze"
                    elif value[1] == "SemiTrapezoidalSup":
                        P1 = rbm.Point(x = the_points_x[0], y = 0)
                        P2 = rbm.Point(x = the_points_x[1], y = 1)
                        P3 = rbm.Point(x = the_points_x[2], y = 1)
                        the_points = [P1, P2, P3]                        
                        the_forme = "trapeze"
                    elif value[1] == "triangular":
                       P1 = rbm.Point(x = the_points_x[0], y = 0)
                       P2 = rbm.Point(x = the_points_x[1], y = 1)
                       P3 = rbm.Point(x = the_points_x[2], y = 0)
                       the_points = [P1, P2, P3]                        
                       the_forme = "triangle"
                    elif value[1] == "trapezoidal":
                       P1 = rbm.Point(x = the_points_x[0], y = 0)
                       P2 = rbm.Point(x = the_points_x[1], y = 1)
                       P3 = rbm.Point(x = the_points_x[2], y = 1)
                       P4 = rbm.Point(x = the_points_x[3], y = 0)
                       the_points = [P1, P2, P3, P4]                        
                       the_forme = "trapeze"
                
                    one_sef = rbm.Sef(label = the_label,
                                  shape = the_forme,
                                  var = one_variable,
                                  points = the_points,
                                  ident = "var_" + str(numero_var) + "_sef_" + str(t[2]))
                
                one_variable.all_sef.append(one_sef)
            i += 1
                
        return one_variable, i
    
    def recup_variables(all_lines):
        dico_var = dict()
        num_var = 1
        i = 1
        while i < len(all_lines):
            line = all_lines[i]
            if all_lines[i] != "\n":
                t = line
                if t[:6] == "[Input" or t[:6] == "[Outpu":
                    var, i = traitement_variable(all_lines, i, num_var)
                    num_var += 1
                    dico_var[var.ident] = var
            i += 1
        return dico_var
    
    
    def traitement_rule(all_lines, indice_line, numero_rule, dico_var):
        #assert all_lines[indice_line] == "[Rules]\n", "Pas la ligne de rules : " + str(all_lines[indice_line])
        idd = str("rule_" + str(numero_rule))
        one_rule = rbm.Rule(ident = idd,
                        premisse = set(),
                        conclusion = set())
        line = all_lines[indice_line]
        value = eval(line)
        for j in range(len(value)):
            if j < len(value) -1:
                numero_sef = value[j] -1
                numero_var = j + 1
                one_term = rbm.Term(var = dico_var["Var_" + str(numero_var)],
                                sef = dico_var["Var_" + str(numero_var)].all_sef[int(numero_sef)])
                one_rule.premisse.add(one_term)
            else:
                numero_sef = value[j] -1
                numero_var = j + 1
                one_term = rbm.Term(var = dico_var["Var_" + str(numero_var)],
                                sef = dico_var["Var_" + str(numero_var)].all_sef[int(numero_sef)])
                one_rule.conclusion.add(one_term)
        return one_rule
    
    def recup_rules(all_lines, dico_var):
        dico_rules = dict()
        num_rule = 1
        i = 0
        while all_lines[i] != "[Rules]\n":
            i+=1
        ligne = i + 2
        while all_lines[ligne] != "\n":
            rule = traitement_rule(all_lines, ligne, num_rule, dico_var)
            dico_rules[rule.ident] = rule
            ligne += 1
            num_rule += 1
        
        return dico_rules
    
    f = open(filepath, "r")
    all_lines = f.readlines()
    f.close()
    
    dico_var = recup_variables(all_lines)
    dico_rules = recup_rules(all_lines, dico_var)
    
    r = rbm.Rulebase(rules = dico_rules,
                 all_var = dico_var,
                 label = recup_value(all_lines[1]))
    for key in r.var.keys():
        r.var[key].rulebase = r
    
    r.filename = os.path.basename(filepath)
    r.used_variables = r.get_used_variables()
    
    return r
    














