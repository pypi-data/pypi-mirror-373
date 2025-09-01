import sys

class Config:
    descriptions = {
        "criteria": {
            "alpha_coverage" : "Choose between 0 and 1 for coverage threshold",
            "rounding": "Round values of all criteria (number of digits after the decimal point)",
            "similarity": "Choose among: {dice, jaccard, tversky}",
            "similarity_param" : "If tversky is chosen:",
            "space_discretization" : "number of inputs within the universe",
            "sample_size" : "size of sample while creating dataset",
            "activation_rule_threshold" : "Rule is considered activated beyond this threshold",
            "precision" : "admitted error for completeness"
            },
        "aggregators": {
            "criteria_aggregation" : "Choose among: {worst, average}",
            "t_norm": "Choose among: {zadeh, probabiliste, lukasiewicz, drastique}",
            "t_conorm" : "Choose among: {dual, zadeh, probabiliste, lukasiewicz, drastique}",
            "order_relationship" : "Choose among: {min_kernel}"
            },
        "plotting": {
            "size_of_plot_x" : "size of x axis for the plot",
            "size_of_plot_y" : "size of y axis for the plot"
            },
        "user defined": dict()
    }
    def __init__(self, alpha_coverage=0.1,
                 rounding=2, similarity="dice", similarity_param=None,
                 space_discretization=1000, sample_size=1000, activation_rule_threshold=0.05,
                 precision = 0.05, criteria_aggregation="worst", t_norm = "zadeh", t_conorm = "dual",
                 order_relationship = "min_kernel", size_of_plot_x = 10, size_of_plot_y = 4):
        kwargs = locals()
        kwargs.pop('self')
        if similarity_param is None:
            self.similarity_param = {"alpha":0.5, "beta":0.5}
            kwargs.pop('similarity_param')
        for k in kwargs: self.__setattr__(k, kwargs[k])

    def add_param(self, param_name, param_value, param_desc="No description given"):
        """
        Add a new configuration's parameter. Once added, it is accessible as all other already defined ones,
        as an object attribute.
        If the added attribute is already existing, a warning is printed on the standard error stream. If the new value
        is not the same type as the old one, another warning is provided. Anyway, the new value replaces the old one.

        :param param_name : the name of the added attribute
        :param param_value : the value initiating the parameter
        :param param_desc : a short description and domain of values text
        """
        if hasattr(self, param_name):
            print(f"[warning] {param_name} is already a config's attribute.\n"
                  f"Prefer a more traditional write access:\n\t...\n\tconfig.{param_name} = {param_value}\n\t...",
                  file=sys.stderr, flush=True)
            if type(getattr(self, param_name)) != type(param_value) :
                print(f"[warning] New and old values are not the same type: "
                      f"({type(param_value)} Vs {type(getattr(self, param_name))}).", file=sys.stderr, flush=True)
        else:
            Config.descriptions["user defined"][param_name] = param_desc
        self.__setattr__(param_name, param_value)

    def __str__(self):
        return '{'+', '.join(f"{att}={self.__getattribute__(att)}" for att in self.__dict__)+'}'

    def reminder(self):
        """
        Set a string showing the description and the current value of all parameters, grouped per category.
        """
        rmd = []
        for category in Config.descriptions:
            rmd.append("#"+("="*78))
            rmd.append("#"+f'{category.upper()} CONFIGURATION'.center(78, ' '))
            rmd.append("#"+("="*78)+"\n")
            for param in Config.descriptions[category]:
                rmd.append("# " + Config.descriptions[category][param])
                rmd.append(f'{param} = {getattr(self, param)}\n')
        return '\n'.join(rmd)

config = Config()