from collections import defaultdict
from typing import Any, Dict, List, Optional, Type
from itertools import product
import numpy as np
import mlflow
from pydantic import BaseModel, Field, model_validator, root_validator, validator
from ddi_fw.datasets.core import BaseDataset
from ddi_fw.datasets.dataset_splitter import DatasetSplitter
from ddi_fw.ml.tracking_service import TrackingService
from ddi_fw.vectorization.idf_helper import IDF
from ddi_fw.ner.ner import CTakesNER
from ddi_fw.ml.ml_helper import MultiModalRunner
from ddi_fw.utils.enums import DrugBankTextDataTypes, UMLSCodeTypes
import logging

              
class NerParameterSearch(BaseModel):
    library: str
    default_model:  Optional[Any] = None
    multi_modal:  Optional[Any] = None
    experiment_name: str
    experiment_description: Optional[str] = None
    tracking_library: str
    tracking_params: Optional[Dict[str, Any]] = None
    dataset_type: Type[BaseDataset]
    dataset_additional_config: Optional[Dict[str, Any]] = None
    dataset_type: Type[BaseDataset]
    dataset_splitter_type: Type[DatasetSplitter] = DatasetSplitter
    columns: List[str] = Field(default_factory=list)
    umls_code_types: Optional[List[UMLSCodeTypes]] = None
    text_types: Optional[List[DrugBankTextDataTypes]] = None
    min_threshold_dict: Dict[str, float] = Field(default_factory=lambda: defaultdict(float))
    max_threshold_dict: Dict[str, float] = Field(default_factory=lambda: defaultdict(float))
    increase_step: float = 0.5

    # Internal fields (not part of the input)
    _tracking_service: TrackingService | None = None
    datasets: Dict[str, Any] = Field(default_factory=dict, exclude=True)
    items: List[Any] = Field(default_factory=list, exclude=True)
    # ner_df: Optional[Any] = Field(default=None, exclude=True)
    train_idx_arr: Optional[List[np.ndarray]] = Field(default=None, exclude=True)
    val_idx_arr: Optional[List[np.ndarray]] = Field(default=None, exclude=True)
    y_test_label: Optional[np.ndarray] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True
        
    @property
    def tracking_service(self) -> TrackingService | None:
        return self._tracking_service

    # @root_validator(pre=True)
    @model_validator(mode="before")
    def validate_columns_and_thresholds(cls, values):
        """Validate and initialize columns and thresholds."""
        umls_code_types = values.get("umls_code_types")
        text_types = values.get("text_types")
        columns = values.get("columns", [])

        if umls_code_types and text_types:
            _umls_codes = [t.value[0] for t in umls_code_types]
            _text_types = [t.value[0] for t in text_types]
            _columns = [f"{item[0]}_{item[1]}" for item in product(_umls_codes, _text_types)]
            columns.extend(_columns)

        values["columns"] = columns
        return values

    def build(self):
        self._tracking_service = TrackingService(self.experiment_name,
                                                 backend=self.tracking_library, tracking_params=self.tracking_params)
        
        """Build the datasets and items for the parameter search."""
        if not isinstance(self.dataset_type, type):
            raise TypeError("self.dataset_type must be a class, not an instance")

        # Load NER data
        ner_data_file = (
                self.dataset_additional_config.get("ner", {}).get("data_file")
                if self.dataset_additional_config else None
            )        
        
        if ner_data_file:
            ner_df = CTakesNER(df=None).load(filename=ner_data_file)

        # Initialize thresholds if not provided
        if not self.min_threshold_dict or not self.max_threshold_dict:
            idf = IDF(ner_df, self.columns)
            idf.calculate()
            df = idf.to_dataframe()
            self.min_threshold_dict = {key: np.floor(df.describe()[key]["min"]) for key in df.describe().keys()}
            self.max_threshold_dict = {key: np.ceil(df.describe()[key]["max"]) for key in df.describe().keys()}
    
        print("Minimum thresholds:", self.min_threshold_dict)
        print("Maximum thresholds:", self.max_threshold_dict)

        # Generate datasets and items
        for column in self.columns:
            min_threshold = self.min_threshold_dict[column]
            max_threshold = self.max_threshold_dict[column]
            thresholds = {
                "threshold_method": "idf",
                "tui": 0,
                "cui": 0,
                "entities": 0,
            }
            if self.dataset_additional_config:
                additional_config=  self.dataset_additional_config
            else:
                additional_config={}

            for threshold in np.arange(min_threshold, max_threshold, self.increase_step):
                if column.startswith("tui"):
                    thresholds["tui"] = threshold
                if column.startswith("cui"):
                    thresholds["cui"] = threshold
                if column.startswith("entities"):
                    thresholds["entities"] = threshold
                additional_config['ner']['thresholds'] = thresholds
                kwargs = {'additional_config': additional_config}
                print(f"Loading dataset for column: {column} with threshold: {threshold}")
                # Create a new dataset instance for each threshold
                dataset = self.dataset_type(
                    columns=[column],
                    dataset_splitter_type=self.dataset_splitter_type,
                    **kwargs,
                )
                dataset.load()
                group_items = dataset.produce_inputs()

                for item in group_items:
                    item[0] = f"threshold_{item[0]}_{threshold}"
                    # self.datasets[item[0]] = dataset

                self.items.extend(group_items)
                
                # Set if y_test_label is None
                # This ensures that y_test_label is set only once for the first dataset
                if self.y_test_label is None:
                    self.y_test_label = self.items[0][4]
                    self.train_idx_arr = dataset.train_idx_arr
                    self.val_idx_arr = dataset.val_idx_arr
                
                # Clear memory for the current dataset and items
                del dataset
                del group_items
                import gc
                gc.collect()
      

    # def run(self):
    #     """Run the parameter search."""
    #     mlflow.set_tracking_uri(self.tracking_uri)

    #     if mlflow.get_experiment_by_name(self.experiment_name) is None:
    #         mlflow.create_experiment(self.experiment_name)
    #     if self.experiment_tags:
    #         mlflow.set_experiment_tags(self.experiment_tags)
    #     mlflow.set_experiment(self.experiment_name)

    #     multi_modal_runner = MultiModalRunner(
    #         library=self.library,
    #         multi_modal=self.multi_modal,
    #         default_model=self.default_model,
    #         use_mlflow=True,
    #     )
    #     multi_modal_runner.set_data(self.items, self.train_idx_arr, self.val_idx_arr, self.y_test_label)
    #     result = multi_modal_runner.predict()
    #     return result
    
    def run(self):
        if self._tracking_service is None:
            logging.warning("Tracking service is not initialized.")
        else:
            self._tracking_service.setup()

        y_test_label = self.items[0][4]
        multi_modal_runner = MultiModalRunner(
            library=self.library, multi_modal=self.multi_modal, default_model=self.default_model, tracking_service=self._tracking_service)

        multi_modal_runner.set_data(
            self.items, self.train_idx_arr, self.val_idx_arr, y_test_label)
        # combinations = self.combinations if self.combinations is not None else []
        result = multi_modal_runner.predict()
        return result