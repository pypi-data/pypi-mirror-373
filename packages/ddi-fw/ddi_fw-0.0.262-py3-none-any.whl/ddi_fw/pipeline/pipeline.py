from typing import Any, Dict, List, Optional, Type
from ddi_fw.datasets.dataset_splitter import DatasetSplitter

from pydantic import BaseModel
from ddi_fw.datasets.core import TextDatasetMixin
from ddi_fw.langchain.faiss_storage import BaseVectorStoreManager
from ddi_fw.ml.tracking_service import TrackingService
from ddi_fw.langchain.embeddings import PoolingStrategy
from ddi_fw.datasets import BaseDataset
from ddi_fw.ml import MultiModalRunner
import logging


class Pipeline(BaseModel):

    library: str = 'tensorflow'
    experiment_name: str
    experiment_description: str
    tracking_library: str
    tracking_params: Optional[Dict[str, Any]] = None
    dataset_type: Type[BaseDataset]
    dataset_additional_config: Optional[Dict[str, Any]] = None
    dataset_splitter_type: Type[DatasetSplitter] = DatasetSplitter
    columns: Optional[List[str]] = None
    embedding_dict: Optional[Dict[str, Any]] = None
    column_embedding_configs: Optional[List] = None
    vector_db_persist_directory: Optional[str] = None
    vector_db_collection_name: Optional[str] = None
    embedding_pooling_strategy_type: Type[PoolingStrategy] | None = None
    vector_store_manager_type: Type[BaseVectorStoreManager] | None = None
    combinations: Optional[List[tuple]] = None
    model: Optional[Any] = None
    default_model:  Optional[Any] = None
    multi_modal:  Optional[Any] = None
    _tracking_service: TrackingService | None = None
    _dataset: BaseDataset | None = None
    _items: List = []
    _train_idx_arr: List | None = []
    _val_idx_arr: List | None = []

    @property
    def tracking_service(self) -> TrackingService | None:
        return self._tracking_service

    @property
    def dataset(self) -> BaseDataset | None:
        return self._dataset

    @property
    def items(self) -> List:
        return self._items

    @property
    def train_idx_arr(self) -> List | None:
        return self._train_idx_arr

    @property
    def val_idx_arr(self) -> List | None:
        return self._val_idx_arr

    class Config:
        arbitrary_types_allowed = True

    # TODO embedding'leri set etme kimin görevi
    def build(self):
        self._tracking_service = TrackingService(self.experiment_name,
                                                 backend=self.tracking_library, tracking_params=self.tracking_params)

        if self.embedding_pooling_strategy_type is not None and not isinstance(self.embedding_pooling_strategy_type, type):
            raise TypeError(
                "self.embedding_pooling_strategy_type must be a class, not an instance")
        if not isinstance(self.dataset_type, type):
            raise TypeError(
                "self.dataset_type must be a class, not an instance")

        # 'enzyme','target','pathway','smile','all_text','indication', 'description','mechanism_of_action','pharmacodynamics', 'tui', 'cui', 'entities'
        kwargs = {"columns": self.columns,
                  "additional_config": self.dataset_additional_config}
        # DDIMDL Dataset'e aktar
        # if self.ner_threshold:
        #     for k, v in self.ner_threshold.items():
        #         kwargs[k] = v

        # ner_df = CTakesNER(df=None).load(
        #     filename=self.ner_data_file) if self.ner_data_file else None

        dataset_splitter = self.dataset_splitter_type()
        pooling_strategy = self.embedding_pooling_strategy_type(
        ) if self.embedding_pooling_strategy_type else None

        params = {}

        if self.embedding_dict is not None:
            params["embedding_dict"] = self.embedding_dict
        if self.vector_db_persist_directory is not None:
            params["persist_directory"] = self.vector_db_persist_directory
        if self.vector_db_collection_name is not None:
            params["collection_name"] = self.vector_db_collection_name


        vector_store_manager = self.vector_store_manager_type(**params) if self.vector_store_manager_type else None
        if issubclass(self.dataset_type, TextDatasetMixin):
            
            dataset = self.dataset_type(
                vector_store_manager = vector_store_manager,
                embedding_dict=self.embedding_dict,
                pooling_strategy=pooling_strategy,
                column_embedding_configs=self.column_embedding_configs,
                vector_db_persist_directory=self.vector_db_persist_directory,
                vector_db_collection_name=self.vector_db_collection_name,
                dataset_splitter_type=self.dataset_splitter_type,
                **kwargs)

        elif self.dataset_type == BaseDataset:
            dataset = self.dataset_type(
                dataset_splitter_type=self.dataset_splitter_type,
                **kwargs)
        else:
            dataset = self.dataset_type(**kwargs)

        # X_train, X_test, y_train, y_test, train_indexes, test_indexes, train_idx_arr, val_idx_arr = dataset.load()

        dataset.load()
        
        self._dataset = dataset
        self._train_idx_arr = dataset.train_idx_arr
        self._val_idx_arr = dataset.val_idx_arr

        dataframe = dataset.dataframe

        # Check if any of the arrays are None or empty
        is_data_valid = (dataset.X_train is not None and dataset.X_train.size > 0 and
                         dataset.y_train is not None and dataset.y_train.size > 0 and
                         dataset.X_test is not None and dataset.X_test.size > 0 and
                         dataset.y_test is not None and dataset.y_test.size > 0)

        # Check if the dataframe is None or empty
        is_dataframe_valid = dataframe is not None and not dataframe.empty

        if not (is_data_valid or is_dataframe_valid):
            raise ValueError("The dataset is not loaded")

        # column name, train data, train label, test data, test label
        self._items = dataset.produce_inputs()

        print(f"Building the experiment: {self.experiment_name}")
        # print(
        #     f"Name: {self.experiment_name}, Dataset: {dataset}, Model: {self.model}")
        # Implement additional build logic as needed
        return self

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
        combinations = self.combinations if self.combinations is not None else []
        result = multi_modal_runner.predict(combinations)
        return result
