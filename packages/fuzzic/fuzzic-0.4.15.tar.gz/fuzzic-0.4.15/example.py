from fuzzic.study.study import Study, create_project
from fuzzic.interpretability.interpretability_manager import CRITERIA, criterion, status, deactivate
from fuzzic.configuration.config import config

def interpretability(rulebase):
    return {"warning" : 'Nothing to say', "score" : 1.}
CRITERIA.append(criterion(name="example", category="linguistic variables", direction="max",
          active=False, func_interpretability=interpretability))

config.add_param('additional_param', [1, 2, 3, 4], 'A example of user criteria')
config.additional_param = [3, 2]
print(config)
print(config.reminder())

study_name = "climatiseur" # the folder name in working_dir/study where the rule-base and all the results are/will be stored

# create_project(study_name)
deactivate("coverage")
print(status())

S = Study(study_name)

# S.display()
S.evaluate()
