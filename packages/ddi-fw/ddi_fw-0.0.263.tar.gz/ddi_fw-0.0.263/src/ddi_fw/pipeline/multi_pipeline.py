import json
from typing import Optional, Type
from ddi_fw.langchain.faiss_storage import BaseVectorStoreManager
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
        experiment_name = config.get("experiment_name")
        experiment_description = config.get("experiment_description")
          
        # Tracking configuration
        tracking_config = config.get("tracking_config", {})
        tracking_library = tracking_config.get("library")
        use_tracking = tracking_config.get("use_tracking", False)
        tracking_params = tracking_config.get("params", {}).get(tracking_library, {})
        
        # tracking_uri = config.get("tracking_uri")
        # artifact_location = config.get("artifact_location")
      
         # Dataset configuration
        dataset_config = config.get("dataset", {})
        dataset_type = get_import(dataset_config.get("dataset_type"))
        dataset_splitter_type = get_import(dataset_config.get("dataset_splitter_type"))
        columns = dataset_config.get("columns", [])
        additional_config = dataset_config.get("additional_config", {})
        
         # Vector database configuration
        vector_database = config.get("vector_databases", {})
        vector_store_manager_type:Type[BaseVectorStoreManager]|None = None
        vector_db_persist_directory = None
        vector_db_collection_name = None
        embedding_pooling_strategy = None
        column_embedding_configs = None
        if vector_database:
            vector_store_manager_type = get_import(vector_database.get("db_type"))
            vector_db_persist_directory = vector_database.get("vector_db_persist_directory")
            vector_db_collection_name = vector_database.get("vector_db_collection_name")
            embedding_pooling_strategy = get_import(vector_database.get("embedding_pooling_strategy"))
            column_embedding_configs = vector_database.get("column_embedding_configs")
            
        # Combination strategy
        combination_strategy_config = config.get("combination_strategy", {})
        combination_type = get_import(combination_strategy_config.get("type")) if combination_strategy_config else None
        kwargs_combination_params = combination_strategy_config.get("params", {})
        combinations = combination_type(**kwargs_combination_params).generate() if combination_type else []

        # Default model configuration
        default_model = config.get("default_model", {})
        default_model_type = get_import(default_model.get("model_type"))
        default_model_params = default_model.get("params", {})
        
        multi_modal = config.get("multi_modal")
        


        #ner move it to related dataset
        
        # ner_data_file = config.get("ner_data_file")
        # ner_threshold = config.get("ner_threshold")
      

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
                tracking_library=tracking_library,
                tracking_params=tracking_params,
                experiment_name=experiment_name,
                experiment_description=experiment_description,
                dataset_type=dataset_type,
                dataset_additional_config=additional_config,
                dataset_splitter_type=dataset_splitter_type,
                columns=columns,
                vector_store_manager_type=vector_store_manager_type,
                column_embedding_configs=column_embedding_configs,
                vector_db_persist_directory=vector_db_persist_directory,
                vector_db_collection_name=vector_db_collection_name,
                embedding_pooling_strategy_type=embedding_pooling_strategy,
                combinations=combinations,
                default_model=default_model,
                multi_modal= multi_modal)
        elif type== "ner_search":
            pipeline = NerParameterSearch(
                library=library,
                tracking_library=tracking_library,
                tracking_params=tracking_params,
                experiment_name=experiment_name,
                experiment_description=experiment_description,
                dataset_type=dataset_type,
                dataset_additional_config=additional_config,
                umls_code_types = None,
                text_types = None,
                columns=columns,
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