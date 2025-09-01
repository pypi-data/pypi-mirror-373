import os

CRITERIA = [] # The list of interpretability criterion instances

class criterion:
    def __init__(self, name, category="", direction="", active=False, func_interpretability=None):
        # my_path = importlib.import_module(path + name, package=None)
        # my_path = importlib.import_module(".".join(__name__.split('.')[:-1]+['criteria', name]), package=None)
        self.category = category
        self.criterion_name = name
        self.direction = direction
        self.active = active
        self.interpretability = func_interpretability

    def __str__(self):
        return (f'[{self.criterion_name}]: {{' +
                ', '.join((f'{name}: {self.__getattribute__(name)}' for name in self.__dict__ if 'name' not in name)) +
                '}')
                
    def __repr__(self):
        return str(self)

def status():
    criteria = sorted([(_.criterion_name, _.active) for _ in CRITERIA])
    return '\n'.join(f'{c_name}: {"in" if not c_active else ""}active' for c_name, c_active in criteria)

def __onoff__(criterion_name, active):
    for _ in CRITERIA:
        if _.criterion_name.lower() == criterion_name.lower():
            _.active = active
            break
    else:
        print("Unknown criterion")

def activate(criterion_name):
    __onoff__(criterion_name, active=True)

def deactivate(criterion_name):
    __onoff__(criterion_name, active=False)

def evaluate_interpretability(study, particular_rulebase = None):
    '''
    input : the file path to the rulebase you want to analyse
    output : a result file in json format in results folder
    '''
    all_results = dict()
    for rulebase in study.rulebases:
        interpretability_result = dict()
        for C in (c for c in CRITERIA if c.active):
            print(f'Evaluate criteria [{C.criterion_name}]', end=' ')
            result = C.interpretability(rulebase)
            print(result)
            interpretability_result[C.criterion_name] = result
        all_results[rulebase.filename] = interpretability_result
        #if rulebase.filename is not None:
        #    study.save_results(os.path.splitext(rulebase.filename)[0], interpretability_result)
    return all_results

# Do not remove. Necessary to initiate already defined criteria.
import fuzzic.interpretability.criteria





















