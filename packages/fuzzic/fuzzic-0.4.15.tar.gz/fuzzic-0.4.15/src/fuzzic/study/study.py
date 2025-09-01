import os
import json
import datetime
import fuzzic.interpretability.interpretability_manager as interpretability_manager
import fuzzic.data_management.import_manager as import_manager

study_path = os.path.realpath(os.getcwd())

def create_project(study_name = "Study", study_root="study"):
    """
   Create the project folder in the study directory.

   Parameters
   ----------
   study_name : str
       name of the study
   study_root : str
       folder in which the study and the results will remain

   Returns
   -------
   Nothing
   """
   
    study_directory = os.path.join(study_path, study_root, study_name)
    if os.path.isdir(study_directory):
        time = datetime.datetime.today().strftime('%Y-%m-%d--%H:%M:%S')
        ref_study = study_name + "_" + time
        print("Study name already exist, it now refers to :" + ref_study) 
        study_directory = os.path.join(study_path, study_root, ref_study)
    else:
        ref_study = study_name

    os.mkdir(study_directory)
    
    dataset_directory = os.path.join(study_directory, "datasets")
    os.mkdir(dataset_directory)
    
    rulebase_directory = os.path.join(study_directory, "rulebases")
    os.mkdir(rulebase_directory)
    
    results_directory = os.path.join(study_directory, "results")
    os.mkdir(results_directory)
    
    specifics_directory = os.path.join(study_directory, "specifics")
    os.mkdir(specifics_directory)
    
    print("Study is ready to set! Reference: " + ref_study)
    print("\nPlease drop at least one rulebase in the rulebases folder before creating object Study.")


def load_study(ref_study):
    """
   load the study object from the reference

   Parameters
   ----------
   ref_study : str
       reference of the study
   
   Returns
   -------
   Nothing
   """
   
    return Study(ref_study, True)

class Study:
    def __init__(self, ref_study = "Study", ref_study_root="study", already_set = False):
        self.ref_study = ref_study
        self.study_directory = os.path.join(study_path, ref_study_root, ref_study)
        self.rulebases_directory = os.path.join(self.study_directory, "rulebases")

        self.dataset = None
        self.rulebases = None
        self.first_rulebase = None

        self.import_rulebases()
        self.import_dataset()
        
        if not already_set:
            self.dump_dataset()
            self.initiate_specifics()
    
    def __repr__(self):
        return "study_" + str(self.ref_study)
        
    def initiate_specifics(self):
        """
       Initialize the study with specific files that are needed for some criteria
       """        
        specifics_directory = os.path.join(self.study_directory, "specifics")
        
        dico_prototype = dict()
        dico_label_order = dict()
        
        variables = self.rulebases[0].var
        
        for key in variables.keys():
            dico_label_order[key] = dict()
            for s in variables[key].all_sef:
                dico_label_order[key][s.label] = 0
        label_orders = os.path.join(specifics_directory, "label_orders.json")
        with open(label_orders, 'w') as f:
            json.dump(dico_label_order, f, sort_keys=True, indent=4, separators=(',', ': '))
        
        for key in variables.keys():
            dico_prototype[key] = []
            
        prototypes_file = os.path.join(specifics_directory, "prototypes.json")
        with open(prototypes_file, 'w') as f:
            json.dump(dico_prototype, f, sort_keys=True, indent=4, separators=(',', ': '))
        
        similar_var_file = os.path.join(specifics_directory, "similar_variables.dat")
        with open(similar_var_file, 'w') as f:
            pass

    
    def import_dataset(self, particular_dataset_name = None):
        """
       Import a dataset for all rulebases of the study.
       If a particular dataset is provided, ignores the other datasets of the dataset folder.
       """
       
        dataset_directory = os.path.join(self.study_directory, "datasets")
        if particular_dataset_name is None:
            the_all_datasets = os.listdir(dataset_directory)
            all_datasets = [data for data in the_all_datasets if not data.endswith('.gitkeep')]
            if len(all_datasets) ==0:
                all_datasets = [None]
        else:
            all_datasets = [particular_dataset_name]
        if not all_datasets[0] is None:
            the_dataset = os.path.join(dataset_directory, all_datasets[0])
            self.dataset = import_manager.import_dataset(the_dataset)
        else:
            dataset = self.rulebases[0].get_dataset()
            self.dataset = dataset
        for rb in self.rulebases:
            rb.dataset = self.dataset
    
    
    def dump_dataset(self):
        """
       Write a dataset from the first rulebase of the folder in the dataset folder
       """
        data = self.rulebases[0].get_dataset()
        dataset_path = os.path.join(self.study_directory, "datasets")
        dataset_file = os.path.join(dataset_path, "one_dataset.data")
        with open(dataset_file, "w") as g:
            for j in range(len(data.labels)):
                lab = data.labels[j]
                g.write(str(lab))
                if j < len(data.labels) - 1:
                    g.write(",")
            g.write("\n")
            for one_data in data.data:
                for i in range(len(one_data)):
                    one_value = one_data[i]
                    g.write(str(one_value))
                    if i < len(one_data)-1:
                        g.write(",")
                g.write("\n")
    
    
    def import_rulebases(self, particular_rulebase_name = None):
        #getting all rulebases in the rulebase folder of the study
        if particular_rulebase_name is None:
            all_rulebases_names = os.listdir(self.rulebases_directory)
            all_rulebases = [os.path.join(self.rulebases_directory, rb) for rb in all_rulebases_names if not rb.endswith('.gitkeep')]
            self.rulebases = [import_manager.import_rulebase(rb) for rb in all_rulebases]
        else:
            rb = os.path.join(self.rulebases_directory, particular_rulebase_name)
            self.rulebases = [import_manager.import_rulebase(rb)]
        for rb in self.rulebases:
            rb.study = self
        self.first_rulebase = self.rulebases[0]
    
    
    def save_results(self, rulebase_name, results):
        result_path = os.path.join(self.study_directory, "results")
        file_path = os.path.join(result_path, rulebase_name + ".json")
        with open(file_path, "w") as f:
            json.dump(results, f, sort_keys=True, indent=4, separators=(',', ': '))

    
    def get_results(self, particular_rulebase_name = None):
        return interpretability_manager.evaluate_interpretability(self, particular_rulebase_name)
    
    def evaluate(self, particular_rulebase_name = None):
        interpretability_result = self.get_results(particular_rulebase_name)
        for rulebase in self.rulebases:
            if rulebase.filename is not None:
                self.save_results(os.path.splitext(rulebase.filename)[0], interpretability_result)
        print("Evaluation of interpretability of rule bases of : " + self.ref_study + " successful !\n")
        result_path = os.path.join(self.study_directory, "results")
        print("Results of evaluation available in " + result_path)
        
    
    def display(self, rulebase_name = None):
        if rulebase_name is None:
            print("Display of the first rulebase:")
            self.rulebases[0].plot_variables()
            self.rulebases[0].display()
        else:
            all_rulebases_names = os.listdir(self.rulebases_directory)
            idx = all_rulebases_names.index(rulebase_name)
            print("Display of rulebase:" + str(rulebase_name))
            self.rulebases[idx].plot_variables()
            self.rulebases[idx].display()




































