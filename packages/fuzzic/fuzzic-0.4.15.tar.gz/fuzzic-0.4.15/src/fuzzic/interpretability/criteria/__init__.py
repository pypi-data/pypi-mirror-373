import os
for module in os.listdir(os.path.dirname(__file__)):
    if module.endswith(".py") and module != "__init__.py":
        module = 'fuzzic.interpretability.criteria.'+module[:-3]
        __import__(module, locals(), globals())

