# FuzzIC

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**FuzzIC** is a Python library for evaluating the **interpretability of fuzzy rule bases**.  
It computes up to **19 different interpretability criteria**, and provides configurable, flexible, and customizable evaluation tools.

---

## 📑 Table of Contents
- [Features](#-features)
- [Installation](#-installation)
- [Quickstart](#-quickstart)
- [Input / Output](#📥-input--📤-output)
- [Configuration](#-configuration)
- [Add a New Criterion](#-add-a-new-criterion)
- [Acknowledgement](#-acknowledgement)
- [License](#-license)

---

## ✨ Features
- Evaluation of **up to 19 interpretability criteria**.
- Configurable via a **central config object**.
- Works with **XML** or **FisPro** rule base formats.
- Outputs results in **JSON**, easy to reuse for visualization or comparison.
- Allows adding **custom interpretability criteria**.

---

## 🛠 Installation

Clone and install locally:

```bash
git clone https://gitlab.lip6.fr/pontoizeau/fuzzic.git
cd fuzzic
pip install -e .
```

> ✅ Requirements: Python ≥ 3.8, `numpy`, `matplotlib`, etc.  
(Dependencies are installed automatically via `pip`.)

---

## 🚀 Quickstart

Quick example on a A/C controller rule base :

```python
from fuzzic.study.study import Study

S = Study("climatiseur") # the folder can be found in <working_dir>/study

S.display()
S.evaluate()
```

Setting your own rule bases.

```python
from fuzzic.study.study import Study, create_project

# 1. Create a new project
study_name = "MyStudy"
create_project(study_name)

# 2. Initialize the study
S = Study(study_name)

# 3. Display and evaluate rule bases
S.display()
S.evaluate()
```

- A new folder `study/MyStudy` is created.
- Put your **rule bases** in `rulebases/`.
- Optionally, put a **dataset** in `dataset/` (CSV format).
- Results will be generated in the `results/` folder.

---

## 📥 Input / 📤 Output

### Input
- Rule bases in **XML** or **FisPro** format (templates provided).
- Fuzzy sets must be **trapezoidal** or **Gaussian**.
- Dataset (optional) in CSV:
  - First line = labels
  - Following lines = instances (comma-separated)

### Output
- A **JSON file** containing all computed criteria values for the rule bases.

---

## 🔧 Configuration

All configuration parameters are managed in:

```python
from fuzzic.configuration.config import config
print(config.reminder())
```

Example:
```python
config.sample_size = 800
print(config.reminder())
```

### Main parameters
- **Criteria configuration**  
  `alpha_coverage`, `rounding`, `similarity`, `sample_size`, etc.
- **Aggregators**  
  `criteria_aggregation`, `t_norm`, `t_conorm`, etc.
- **Plotting**  
  `size_of_plot_x`, `size_of_plot_y`
- **User-defined**  
  Add your own parameters with:
  ```python
  config.add_param('my_param', [1, 2, 3], 'Example custom parameter')
  ```

---

## ➕ Add a New Criterion

Define a function taking a **rulebase** and returning a `dict`:

```python
def interpretability(rulebase):
    return {"warning": "Nothing to say", "score": 1.0}
```

Register it in the global `CRITERIA` list:

```python
from fuzzic.interpretability.criteria import CRITERIA, criterion

CRITERIA.append(criterion(
    name="example",
    category="linguistic variables",
    direction="max",
    active=True,
    func_interpretability=interpretability
))
```

Set the criterion parameter:
- criterion_name: The name of your criterion
- category: The object which the criterion applies on. Current are ['linguistic variables', 'fuzzy rule', 'fuzzy set', 'fuzzy rule base', 'fuzzy sets'].
- direction : if the criterion must be maximized, minimized
- active: if you wish to evaluate this criterion or not during evaluation
- func_interpretability: the reference to the interpretability evaluation function of this criterion

Manage active criteria:
```python
import fuzzic.interpretability.criteria as ic

ic.activate("normality")
ic.deactivate("coverage")
print(ic.status())
```

Here is a full example:
```python
from fuzzic.study.study import Study, create_project
from fuzzic.interpretability.interpretability_manager import  status, deactivate
from fuzzic.configuration.config import config

#### IF A NEW INTERPRETABILITY CRITERION HAS TO BE DEFINED IN ADDITION
from fuzzic.interpretability.interpretability_manager import CRITERIA, criterion

def interpretability(rulebase):
    ...
    return {"warning" : 'Nothing to say', "score" : 1.}

CRITERIA.append(criterion(name="example", category="linguistic variables", direction="max",
          active=True, func_interpretability=interpretability))
#########

config.add_param('additional_param', [1, 2, 3, 4], 'A example of user criteria')
print(config.reminder())
config.additional_param = [3, 2]

study_name = "climatiseur" # the folder name in working_dir/study where the rule-base and all the results are/will be stored

create_project(study_name)

deactivate("coverage")
print(status())

S = Study(study_name)

S.display()
S.evaluate()
```

---

## 🙏 Acknowledgement

This work has been funded by the project **IFP-in-RL, ANR-22-ASTR-0032**.

---

## 📜 License

Distributed under the [MIT License](https://choosealicense.com/licenses/mit/).
