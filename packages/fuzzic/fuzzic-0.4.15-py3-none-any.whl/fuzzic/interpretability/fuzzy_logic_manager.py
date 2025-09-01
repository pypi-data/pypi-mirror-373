import numpy as np
from fuzzic.configuration.config import config


# CRITERIA MANAGEMENT =========================================================

def rounding(value):
    """
    Returns the rounded value of an integer

    Parameters
    ----------
    value : float
        a real value

    Returns
    -------
    value : float
        the rounded value with the number of decimals given in configuration object
    """
    
    return round(value, config.rounding)

def criteria_aggregator(collection, direction = None):
    """
    Aggregate the scores in the collection according to the config.criteria_aggregation method.

    Parameters
    ----------
    collection : list
        a real value
    direction : str

    Returns
    -------
    value : float
        The aggregated score for a criterion
    """
    if config.criteria_aggregation == "average":
        return np.average(collection)
    elif config.criteria_aggregation == "worst":
        assert direction in ["min", "max"], "no direction (min or max) to evaluate worst case."
        if direction == "min":
            return max(collection)
        elif direction == "max":
            return min(collection)


# FUZZY LOGIC MANAGEMENT ======================================================

def t_norm(x, y):
    """
    Return the t-norm of two values.

    Parameters
    ----------
    x : float
        a real value
    y : float
        a real value

    Returns
    -------
    value : float
        The t-norm of x and y according to the config.t_norm method
    """
    assert config.t_norm in ["zadeh", "probabiliste", "lukasiewicz", "drastique"], "t norm unknown"
    if config.t_norm == "zadeh":
        return min(x,y)
    elif config.t_norm == "probabiliste":
        return x * y
    elif config.t_norm == "lukasiewicz":
        return max(x, y-1, 0)
    elif config.t_norm == "drastique":
        if y == 1:
            return x
        if x == 1:
            return y
        else:
            return 0

def t_conorm(x, y):
    """
    Return the t-conorm of two values.

    Parameters
    ----------
    x : float
        a real value
    y : float
        a real value

    Returns
    -------
    value : float
        The t-conorm of x and y according to the config.t_conorm method
    """
    assert config.t_norm in ["zadeh", "probabiliste", "lukasiewicz", "drastique"], "t norm unknown"
    if config.t_norm == "zadeh":
        return max(x,y)
    elif config.t_norm == "probabiliste":
        return x + y - (x * y)
    elif config.t_norm == "lukasiewicz":
        return min(x + y, 1)         
    elif config.t_norm == "drastique":
        if y == 0:
            return x
        if x == 0:
            return y
        else:
            return 1

def difference(x, y): #A\B = A inter Bc
    """
    Return the t-norm of x and 1-y.

    Parameters
    ----------
    x : float
        a real value
    y : float
        a real value

    Returns
    -------
    value : float
        The t-norm of x and 1-y according to the config.t_norm method
    """
    
    assert config.t_norm in ["zadeh", "probabiliste", "lukasiewicz", "drastique"], "t-norm unknown"
    return t_norm(x, 1-y)

def check_activation(rule, labels, the_data):
    """
    Verify if a rule is activated by the data.

    Parameters
    ----------
    rule : Rule object
        a real value
    labels : list
        ordered list of the labels of a dataset
    the_data : float
        ordered list of one data of a dataset among all labels

    Returns
    -------
    value : boolean
        True if the t-norm of the activations of all terms or the given rule is greater than the threshold (see config)
    """
    
    final_result = None
    seuil = config.activation_rule_threshold
    for term in rule.premisse:
        indice = labels.index(term.var.label)
        x = float(the_data[indice])
        result = term.sef.forward(x)
        if final_result is None:
            final_result = result
        else:
            final_result = t_norm(final_result, result)
    return final_result > seuil

def is_greater_than(sef1, sef2):
    """
    Verify if the fuzzy set sef1 is greater than sef2 with the order relationship of the configuration object.

    Parameters
    ----------
    sef1 : Sef object
        a fuzzy set object
    sef2 : Sef object
        a fuzzy set object

    Returns
    -------
    value : boolean
        True if sef1 is greater than sef2
    """
    
    order_relationship = config.order_relationship
    assert order_relationship in ["min_kernel"], "unknown order relationship."
    if order_relationship == "min_kernel":
        a = sef1.hauteur_x
        b = sef2.hauteur_x
        return a >= b


# SIMILARITY MANAGEMENT =========================================================

def similarity(sef1, sef2):
    """
    Computes the similarity between two fuzzy sets.

    Parameters
    ----------
    sef1 : Sef object
        a fuzzy set object
    sef2 : Sef object
        a fuzzy set object

    Returns
    -------
    float
        Similarity result (from config object) of the two given fuzzy sets.
    """
    
    if config.similarity == "dice":
        return dice(sef1, sef2)
    
    elif config.similarity == "jaccard":
        return jaccard(sef1, sef2)
    
    elif config.similarity == "tversky":
        return tversky(sef1, sef2, config.similarity_param["alpha"], config.similarity_param["beta"])
    

def dice(sef1, sef2):
    """
    Computes the Dice similarity between two fuzzy sets.

    Parameters
    ----------
    sef1 : Sef object
        a fuzzy set object
    sef2 : Sef object
        a fuzzy set object

    Returns
    -------
    float
        Dice similarity result of the two given fuzzy sets.
    """
    
    if sef1.var.bounds[0] == sef2.var.bounds[0] and sef1.var.bounds[1] == sef2.var.bounds[1]:
        #mini = max(sef1.var.bounds[0], sef2.var.bounds[0])
        #maxi = min(sef1.var.bounds[1], sef2.var.bounds[1])
        #total_div = config.space_discretization
        #espace = np.linspace(mini, maxi, total_div).tolist()
        U = 0
        V = 0
        inter_UV = 0
        for x in sef1.var.espace:
            y1 = sef1.forward(x)
            y2 = sef2.forward(x)
            U += y1
            V += y2
            inter_UV += t_norm(y1, y2)
        dice_result = (2 * inter_UV) / (U + V)
        return dice_result
    else:
        return -1


def jaccard(sef1, sef2):
    """
    Computes the Jaccard similarity between two fuzzy sets.

    Parameters
    ----------
    sef1 : Sef object
        a fuzzy set object
    sef2 : Sef object
        a fuzzy set object

    Returns
    -------
    float
        Jaccard similarity result of the two given fuzzy sets.
    """
    
    if sef1.bounds[0] == sef2.bounds[0] and sef1.bounds[1] == sef2.bounds[1]:
    
        inter_UV = 0
        union_UV = 0
        for x in sef1.var.espace:
            y1 = sef1.forward(x)
            y2 = sef2.forward(x)
            inter_UV += t_norm(y1, y2)
            union_UV += t_conorm(y1, y2)
        result = inter_UV / union_UV
        return result
    else:
        return -1


def tversky (sef1, sef2, alpha, beta):
    """
    Computes the Tversky similarity between two fuzzy sets.

    Parameters
    ----------
    sef1 : Sef object
        a fuzzy set object
    sef2 : Sef object
        a fuzzy set object

    Returns
    -------
    float
        Tversky similarity result of the two given fuzzy sets.
    """
    
    if sef1.bounds[0] == sef2.bounds[0] and sef1.bounds[1] == sef2.bounds[1]:
        inter_UV = 0
        U_sans_V = 0
        V_sans_U = 0
        for x in sef1.var.espace:
            y1 = sef1.forward(x)
            y2 = sef2.forward(x)
            U_sans_V += difference(y1, y2)
            V_sans_U += difference(y2, y1)
            inter_UV += t_norm(y1, y2)
        result = inter_UV / (inter_UV + alpha * U_sans_V + beta * V_sans_U)
        return result
    else:
        return -1






