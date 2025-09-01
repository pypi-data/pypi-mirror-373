import xml.etree.ElementTree as ET


def generate_xml(rulebase, filepath) : 
    """
    Generates a XML file from a rulebase object from study.py

    Parameters
    ----------
    rulebase : rulebase object (see study.py)
    filepath : str
        path of the wanted resulting XML file.

    Returns
    -------
    Nothing
    """
    
    root = ET.Element("rulebase") 
      
    m1 = ET.Element("label")
    m1.text = rulebase.label
    root.append (m1)
    
    for key in rulebase.var.keys():
        var = rulebase.var[key]
    
        v = ET.Element("variable", ident = var.ident)
        root.append(v)
        l = ET.SubElement(v, "label")
        l.text = var.label
        
        u = ET.SubElement(v, "universe", unit = var.unit)
        mini = ET.SubElement(u, "bound", type = "Inf")
        mini.text = str(var.bounds[0])
        maxi = ET.SubElement(u, "bound", type = "Sup")
        maxi.text = str(var.bounds[1])
        
        for sef in var.all_sef:
            s = ET.SubElement(v, "sef", ident = sef.ident)
            
            l = ET.SubElement(s, "label")
            l.text = sef.label
            
            if sef.shape == "gaussian":
                g = ET.SubElement(s, "gaussian")
                m = ET.SubElement(g, "mean")
                m.text = str(sef.gaussian.mean)
                d = ET.SubElement(g, "deviation")
                d.text = str(sef.gaussian.deviation)
            else:
                for point in sef.points:
                    p = ET.SubElement(s, "point")
                    x = ET.SubElement(p, "x")
                    x.text = str(point.x)
                    y = ET.SubElement(p, "y")
                    y.text = str(point.y)
    
    for key in rulebase.rules.keys():
        rule = rulebase.rules[key]
        
        r = ET.Element("rule", ident = rule.ident)
        root.append(r)
        
        for pre in rule.premisse:
            p = ET.SubElement(r, "premise")
            varid = ET.SubElement(p, "variableID")
            varid.text = pre.var.ident
            fuzzysetid = ET.SubElement(p, "fuzzysetID")
            fuzzysetid.text = pre.sef.ident
            
        for concl in rule.conclusion:
            c = ET.SubElement(r, "conclusion")
            varid = ET.SubElement(c, "variableID")
            varid.text = concl.var.ident
            fuzzysetid = ET.SubElement(c, "fuzzysetID")
            fuzzysetid.text = concl.sef.ident
      
    tree = ET.ElementTree(root) 
    ET.indent(tree, space="\t", level=0)
    
    out = open(filepath, 'wb')
    out.write(b'<?xml version="1.0" encoding="ISO-8859-1" standalone = "yes"?>\n\n')
    #out.write(b'<!DOCTYPE rulebase SYSTEM "rulebase.dtd">?>\n\n')
    tree.write(out, encoding = 'ISO-8859-1', xml_declaration = False)
    out.close()
  









