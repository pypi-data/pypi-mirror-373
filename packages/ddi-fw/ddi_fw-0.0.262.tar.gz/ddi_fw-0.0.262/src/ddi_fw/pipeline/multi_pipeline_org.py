import json
from typing import Optional
from ddi_fw.pipeline.pipeline import Pipeline
from ddi_fw.pipeline.ner_pipeline import NerParameterSearch
import importlib


def load_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config


def get_import(full_path_of_import):
    """Dynamically imports an object from a module given its full path.

    Args:
        full_path_of_import (str): The full path of the import (e.g., 'module.submodule.ClassName').

    Returns:
        object: The imported object.

    Raises:
        ImportError: If the module cannot be imported.
        AttributeError: If the attribute does not exist in the module.
    """
    if not full_path_of_import:
        raise ValueError("The import path cannot be empty.")

    parts = full_path_of_import.split('.')
    import_name = parts[-1]
    module_name = ".".join(parts[:-1]) if len(parts) > 1 else ""

    try:
        module = importlib.import_module(module_name)
        return getattr(module, import_name)
    except ModuleNotFoundError as e:
        raise ImportError(f"Module '{module_name}' could not be found.") from e
    except AttributeError as e:
        raise AttributeError(
            f"'{module_name}' has no attribute '{import_name}'") from e


class MultiPipeline():
    # def __init__(self, experiments_config_file, experiments_config):
    #     if experiments_config_file is None and experiments_config is None:
    #         raise ValueError("Either experiments_config_file or experiments_config must be provided.")
    #     if experiments_config_file is not None and experiments_config is not None:  
    #         raise ValueError("Only one of experiments_config_file or experiments_config should be provided.")
    #     if experiments_config_file is not None:
    #         self.experiments_config = load_config(experiments_config_file)
    #     else:
    #         self.experiments_config = experiments_config
    #     self.items = []
    #     self.pipeline_resuts = dict()
    
    def __init__(self, experiments_config_file: Optional[str] = None, experiments_config: Optional[dict] = None):
        """
        Initialize the MultiPipeline.

        Args:
            experiments_config_file (str, optional): Path to the experiments configuration file.
            experiments_config (dict, optional): Dictionary containing the experiments configuration.

        Raises:
            ValueError: If neither or both of the parameters are provided.
        """
        self.experiments_config = self._validate_and_load_config(experiments_config_file, experiments_config)
        self.items = []
        # self.pipeline_results = {}
        self.pipeline_resuts = dict()

    def _validate_and_load_config(self, experiments_config_file: Optional[str], experiments_config: Optional[dict]) -> dict:
        """
        Validate and load the experiments configuration.

        Args:
            experiments_config_file (str, optional): Path to the experiments configuration file.
            experiments_config (dict, optional): Dictionary containing the experiments configuration.

        Returns:
            dict: The loaded experiments configuration.

        Raises:
            ValueError: If neither or both of the parameters are provided.
        """
        if experiments_config_file is None and experiments_config is None:
            raise ValueError("Either 'experiments_config_file' or 'experiments_config' must be provided.")
        if experiments_config_file is not None and experiments_config is not None:
            raise ValueError("Only one of 'experiments_config_file' or 'experiments_config' should be provided.")

        if experiments_config_file is not None:
            try:
               config = load_config(experiments_config_file)
            except FileNotFoundError:
                raise FileNotFoundError(f"Configuration file '{experiments_config_file}' not found.")
        else:
            config = experiments_config
        if config is None:
            raise ValueError("Configuration cannot be None.")
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary.")
        # if "experiments" not in config: 
        #     raise ValueError("Configuration must contain 'experiments' key.")
        return config

    def __create_pipeline(self, config):
        type = config.get("type")
        library = config.get("library")

        use_mlflow = config.get("use_mlflow")
        experiment_name = config.get("experiment_name")
        experiment_description = config.get("experiment_description")
        experiment_tags = config.get("experiment_tags")
        tracking_uri = config.get("tracking_uri")
        artifact_location = config.get("artifact_location")
        #new
        default_model = config.get("default_model")
        multi_modal = config.get("multi_modal")
        columns = config.get("columns")
        ner_data_file = config.get("ner_data_file")
        ner_threshold = config.get("ner_threshold")
        ner_min_threshold_dict = config.get("ner_min_threshold_dict")
        ner_max_threshold_dict = config.get("ner_max_threshold_dict")
        column_embedding_configs = config.get("column_embedding_configs")
        vector_db_persist_directory = config.get("vector_db_persist_directory")
        vector_db_collection_name = config.get("vector_db_collection_name")
        embedding_pooling_strategy = get_import(
            config.get("embedding_pooling_strategy_type")) if config.get("embedding_pooling_strategy_type") else None
        # Dynamically import the model and dataset classes
        # model_type = get_import(config.get("model_type"))
        dataset_type = get_import(config.get("dataset_type"))
        dataset_splitter_type = get_import(config.get("dataset_splitter_type"))

        combination_type = None
        kwargs_combination_params=None
        if config.get("combination_strategy"):
            combination_type = get_import(config.get("combination_strategy").get("type"))
            kwargs_combination_params = config.get("combination_strategy").get("params")
        combinations = []
        if combination_type is not None:
            combinations = combination_type(**kwargs_combination_params).generate()
      

        pipeline = None
        if type == "general":
            pipeline = Pipeline(
                library=library,
                use_mlflow=use_mlflow,
                experiment_name=experiment_name,
                experiment_description=experiment_description,
                experiment_tags=experiment_tags,
                artifact_location=artifact_location,
                tracking_uri=tracking_uri,
                dataset_type=dataset_type,
                dataset_splitter_type=dataset_splitter_type,
                columns=columns,
                column_embedding_configs=column_embedding_configs,
                vector_db_persist_directory=vector_db_persist_directory,
                vector_db_collection_name=vector_db_collection_name,
                embedding_pooling_strategy_type=embedding_pooling_strategy,
                ner_data_file=ner_data_file,
                ner_threshold=ner_threshold,
                combinations=combinations,
                default_model=default_model,
                multi_modal= multi_modal)
        elif type== "ner_search":
            pipeline = NerParameterSearch(
                library=library,
                experiment_name=experiment_name,
                experiment_description=experiment_description,
                experiment_tags=experiment_tags,
                tracking_uri=tracking_uri,
                dataset_type=dataset_type,
                dataset_splitter_type=dataset_splitter_type,
                umls_code_types = None,
                text_types = None,
                min_threshold_dict=ner_min_threshold_dict,
                max_threshold_dict=ner_max_threshold_dict,
                columns=columns,
                ner_data_file=ner_data_file,
                default_model=default_model,
                multi_modal= multi_modal
            )


        return {
            "name": experiment_name,
            "library": library,
            "pipeline": pipeline}

    def build(self):
        for config in self.experiments_config['experiments']:
            item = self.__create_pipeline(config)
            self.items.append(item)
        return self

    def run(self):
        for item in self.items:
            print(f"{item['name']} is running")
            pipeline = item['pipeline']
            pipeline.build()
            result = pipeline.run()
            self.pipeline_resuts[item['name']] = result
        return self

    def results(self):
        return self.pipeline_resuts