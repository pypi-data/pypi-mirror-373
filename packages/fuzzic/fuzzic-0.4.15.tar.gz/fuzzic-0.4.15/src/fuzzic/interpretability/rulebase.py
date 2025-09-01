import random
import numpy as np
import copy
from fuzzic.configuration.config import config
import fuzzic.data_management.import_manager as import_manager
import fuzzic.visualization.plot as plot

# DATASET CLASS ===============================================================

class Dataset:
    def __init__(self, dataset_list):
        self.labels = dataset_list[0]
        self.data = dataset_list[1:]



# ALL CLASSES NEEDED TO MANAGE FUZZY SETS AND FUZZY RULE BASES ================

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __repr__(self):
        return "point" + "_" + str(self.x) + str(self.y)


class Droite:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def __repr__(self):
        return "droite" + "_" + repr(self.p1) + "_" + repr(self.p2)

    def forward(self, x):
        x1 = self.p1.x 
        x2 = self.p2.x 
        y1 = self.p1.y
        y2 = self.p2.y
        m = (y2-y1)/(x2-x1)
        p = y1 - m * x1
        return m*x + p

class Gaussian:
    def __init__(self, mean, deviation):
        self.mean = mean
        self.deviation = deviation
        self.hauteur = self.forward(self.mean)
    
    def __repr__(self):
        return "gaussian" + "_" + str(self.deviation) + "_" + str(self.mean)
    
    def forward(self,x):
        return  np.exp(-(x - self.mean)**2 / (2 * self.deviation**2))


# ==================================

class Variable:
    def __init__(self, label, rulebase, unit, bounds, all_sef = None, ident = None, prototypes = None):
        self.ident = ident
        self.label = label
        self.rulebase = rulebase
        self.unit = unit
        self.bounds = bounds
        self.all_sef = [] if all_sef is None else all_sef
        self.space_discretization = config.space_discretization
        self.espace = self.define_linear_space(xmin = self.bounds[0], 
                                               xmax = self.bounds[1])
    
    def __repr__(self):
        return "variable_" + str(self.ident) + "_" + str(self.label) + "_" + str(self.unit) + "_" + repr(self.bounds)
    
    def define_linear_space(self, xmin, xmax):
        total_div = self.space_discretization
        return np.linspace(xmin, xmax, total_div).tolist()
    
    def find_sef(self, label_sef):
        for i in range(len(self.all_sef)):
            s = self.all_sef[i]
            if s.label == label_sef:
                return s
        return None
    
    def plot(self):        
        captions = [sef.label for sef in self.all_sef]
        plot.plot_membership_functions(self.all_sef, captions, self.label, pas = (self.bounds[1]-self.bounds[0])//10, unite=self.unit)
        
        #elif self.all_sef[0].shape == "gaussian":
        #    plot.plot_gaussian_membership_functions(self.all_sef, self.label, pas = (self.bounds[1]-self.bounds[0])//10, unite=self.unit)
        #else:
        #    captions = [sef.label for sef in self.all_sef]
        #    plot.plot_trapezoidal_membership_functions(self.all_sef, captions, self.label, pas = (self.bounds[1]-self.bounds[0])//10, add_annotation = False, gaussian = None, unite=self.unit)




# =============================================================================

class Sef:
    # fuzzy set class
    def __init__(self, label, shape, var = None, points = None, gaussian = None, ident = None):
        self.ident = ident
        self.label = label
        self.shape = shape
        self.points = points
        self.gaussian = gaussian
        self.var = var
        self.cardinal = self.cardinal()
        if self.gaussian is not None:
            self.hauteur_x = self.gaussian.mean
            self.hauteur_y = self.gaussian.hauteur
        else:
            self.hauteur_y = max([self.points[i].y for i in range(len(self.points))])
            self.hauteur_x = min([self.points[i].x for i in range(len(self.points)) if self.points[i].y == self.hauteur_y])

        assert self.gaussian is not None or self.points is not None, "Le SEF n'a pas de forme."

    def __repr__(self):
        if self.shape == "gaussian":
            return "sef_" + str(self.ident) + "_" + str(self.label) + "_" + str(self.shape) + "_" + repr(self.gaussian) + "_" + repr(self.var)
        else:
            return "sef_" + str(self.ident) + "_" + str(self.label) + "_" + str(self.shape) + "_" + repr(self.points) + "_" + repr(self.var)
    
    def cardinal(self):
        U = 0
        for x in self.var.espace:
            y1 = self.forward(x)
            U += y1
        return U
    
    def forward(self, x):
        assert x >= self.var.bounds[0] and x <= self.var.bounds[1], "x = " + str(x) + " outside universe " + repr(self.var.bounds)
        if self.shape == "gaussian":
            return self.gaussian.forward(x)
        else:
            for po in self.points:
                if po.x == x:
                    return po.y
                
            if self.shape == "one_point":
                if x != self.points[0].x:
                    return 0
                else:
                    return self.points[0].y
            else:
                all_points = copy.deepcopy(self.points)
                slots = [all_points[j].x for j in range (len(all_points))]
                
                if all_points[0].x > self.var.bounds[0]:
                    slots = [self.var.bounds[0]] + slots
                    P = Point(x = self.var.bounds[0], y = all_points[0].y)
                    all_points = [P] + all_points
                
                if all_points[len(all_points)-1].x < self.var.bounds[1]:
                    slots = slots +[self.var.bounds[1]]
                    P = Point(x = self.var.bounds[1], y = all_points[len(all_points)-1].y)
                    all_points =  all_points + [P]
                
                i = 0
                while x > slots[i+1]:
                    i = i+1
                #print(str(x) +  " est bien entre " + str(slots[i]) + " et " + str(slots[i+1]))
    
                p1 = all_points[i]
                p2 = all_points[i+1]
                d = Droite(p1, p2)
                #print("d est la droite des points (" + str(p1.x) + " " + str(p1.y) + ") et (" + str(p2.x) + " " + str(p2.y) + ").")
                return d.forward(x)
    
    def starting_point(self):
        assert self.shape != "gaussian", "not possible to generate linear functions since functions are gaussian."
        if self.points[0].y > 0:
            return self.points[0]
        else:
            return self.points[1]
    
    def linear_functions(self):
        assert self.shape != "gaussian", "not possible to generate linear functions since functions are gaussian."
        i = 0
        L = []
        while i< len(self.points)-1 and self.points[i][1] != self.points[i+1][1]:
            #on ne choisit que les droites qui ne sont pas horizontales
            d = Droite(self.points[i], self.points[i+1])
            L.append(d)
        return L


# =============================================================================

class Term:
    def __init__(self, var, sef):
        self.var = var
        self.sef = sef
    
    def __repr__(self):
        return "term_" + repr(self.var) + repr(self.sef)
    
    def forward(self,x):
        return self.sef.forward(x)
    
    
# =============================================================================

class Rule:
    def __init__(self, ident = None, premisse = None, conclusion = None):
        self.ident = ident
        self.premisse = set() if premisse is None else premisse
        self.conclusion = set() if conclusion is None else conclusion
        
    def __repr__(self):
        return "rule_" + repr(self.ident) + repr(self.premisse) + "_" + repr(self.conclusion)


# =============================================================================
    
class Rulebase:
    def __init__(self, rules = None, all_var = None, label = None):
        self.filename = None
        self.label = label
        self.rules = dict() if rules is None else rules
        self.var = dict() if all_var is None else all_var
        self.dataset = None
        self.used_variables = None
        self.study = None
    
    def __repr__(self):
        return "rulebase_" + repr(self.label) + repr({k: self.rules[k] for k in sorted(self.rules)})
    
    def get_var(self, ident):
        for key in self.var.keys():
            if self.var[key].ident == ident:
                return self.var[key]
        return None
    
    def get_all_sef(self):
        the_sef = []
        for key in self.var.keys():
            var = self.var[key]
            for s in var.all_sef:
                the_sef.append(s)
        return the_sef
    
    def create_dataset(self):
        print("Creating dataset...")
        all_var = []
        for key in self.var.keys():
            the_var = self.var[key]
            one_var = [the_var.label]
            for i in range(config.sample_size):
                x = random.uniform(the_var.bounds[0],the_var.bounds[1])
                one_var.append(x)
            all_var.append(one_var)
        all_var = np.transpose(all_var).tolist()
        self.dataset = Dataset(all_var)

    def set_dataset(self, file):
        assert type(file) in [list, str], "le dataset ne peut être importé dans la base de règle" + str(self.label)
        
        if type(file) is list:
            self.dataset = Dataset(file)
        
        else:
            ds = import_manager.import_dataset(file)
            self.dataset = Dataset(ds)
            
    def get_dataset(self):
        if self.dataset is None:
            self.create_dataset()
        return self.dataset
    
    def plot_variables(self):
        for key in self.var.keys():
            self.var[key].plot()
    
    def get_used_variables(self):
        var_utilisees = dict()
        rules = self.rules
        for key in rules.keys():
            rule = rules[key]
            for term in rule.premisse:
                var_utilisees[term.var.ident] = self.get_var(term.var.ident)
            for term in rule.conclusion:
                var_utilisees[term.var.ident] = self.get_var(term.var.ident)
        
        return var_utilisees
        #all_keys = self.var.keys()
        #var_non_utilisees = set()
        #for key in all_keys:
        #    if key not in var_utilisees:
        #        var_non_utilisees.add(key)
        #for key in var_non_utilisees:
        #    del(self.var[key])
    
    def display(self):
        print("====================")
        print("\tRULE BASE : " + self.label)
        print()
        for key in self.var.keys():
            print("\t====================")
            print("\tVARIABLE : " + str(key))
            print("\tLabel :", self.var[key].label)
            print("\tUnités :", self.var[key].unit)
            print("\tBornes : entre " + str(self.var[key].bounds[0]) + " et " + str(self.var[key].bounds[1]) + " " + str(self.var[key].unit))
            print()
            for sef in self.var[key].all_sef:
                print("\t\tSEF : " + sef.ident)
                print("\t\tLabel : " + str(sef.label))
                if sef.shape == "gaussian":
                    print("\t\t" + str(sef.shape) + " --> mean : " + str(sef.gaussian.mean) + " and deviation : " + str(sef.gaussian.deviation))
                else:
                    print("\t\t" + str(sef.shape) + " --> " + repr([[p.x, p.y] for p in sef.points]))
                print()
        for key in self.rules.keys():
            rule = self.rules[key]
            print("====================")
            print("Rule : " + str(rule.ident))
            p = rule.premisse
            stri = "Si "
            for pre in p:
                stri += str(pre.var.label) + " est " + str(pre.sef.label) + " et "
            stri = stri[:len(stri)-4]
            stri+= ", alors "
            c = rule.conclusion
            for concl in c:
                stri += str(concl.var.label) + " est " + str(concl.sef.label) + " et "
            stri = stri[:len(stri)-4]
            stri += "."
            print(stri)
        print("\n")








