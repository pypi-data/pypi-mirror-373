from ddi_fw.ml.model_wrapper import Result
from ddi_fw.ml.pytorch_wrapper import PTModelWrapper
from ddi_fw.ml.tensorflow_wrapper import TFModelWrapper
from ddi_fw.utils.package_helper import get_import
import numpy as np
from ddi_fw.ml.evaluation_helper import  evaluate

# import tf2onnx
# import onnx

import itertools
import ddi_fw.utils as utils

# tf.random.set_seed(1)
# np.random.seed(2)
# np.set_printoptions(precision=4)


class MultiModalRunner:
    # todo model related parameters to config
    def __init__(self, library, multi_modal, default_model, tracking_service):
        self.library = library
        self.multi_modal = multi_modal
        self.default_model = default_model
        self.tracking_service = tracking_service
        self.result = Result()

    # def _mlflow_(self, func: Callable):
    #     if self.use_mlflow:
    #         func()

    def set_data(self, items, train_idx_arr, val_idx_arr, y_test_label):
        self.items = items
        self.train_idx_arr = train_idx_arr
        self.val_idx_arr = val_idx_arr
        self.y_test_label = y_test_label

    def __create_model(self, library):
        if library == 'tensorflow':
            return TFModelWrapper
        elif library == 'pytorch':
            return PTModelWrapper
        else:
            raise ValueError(
                "Unsupported library type. Choose 'tensorflow' or 'pytorch'.")

    # TODO check single_results, 1d,2d ...
    def __predict(self, single_results):
        item_dict = {t[0]: t for t in self.items}
        if self.default_model is None and not self.multi_modal:
            raise Exception("Default model and multi modal cannot be None at the same time")

        if self.multi_modal:
            for m in self.multi_modal:
                name = m.get('name')
                # input_type = m.get('input_type')
                input = m.get('input')
                inputs = m.get('inputs')
                model_type = get_import(m.get("model_type"))
                kwargs = m.get('params')
                T = self.__create_model(self.library)
                single_modal = T(self.date, name, model_type,
                                tracking_service=self.tracking_service,  **kwargs)
                
                if input is not None and inputs is not None:
                    raise Exception("input and inputs should not be used together")
                
                if input:
                    item = item_dict[input]
                    single_modal.set_data(
                        self.train_idx_arr, self.val_idx_arr, item[1], item[2], item[3], item[4])
                elif inputs:
                    # check keys
                    filtered_dict = {k: item_dict[k]
                                    for k in inputs if k in item_dict}
                    print(filtered_dict.keys())
                    first_input = next(iter(filtered_dict.values()))
                    train_data_list = [f[1] for f in filtered_dict.values()]
                    test_data_list = [f[3] for f in filtered_dict.values()]
                    train_data = np.stack(train_data_list, axis=1)
                    test_data = np.stack(test_data_list, axis=1)
                    train_label = first_input[2]
                    test_label = first_input[4]
                    single_modal.set_data(
                        self.train_idx_arr, self.val_idx_arr, train_data, train_label, test_data, test_label)
                else:
                    raise Exception("check configurations")
                logs, metrics, prediction = single_modal.fit_and_evaluate()
                self.result.add_metric(name, metrics)
                single_results[name] = prediction
        else: # TODO default model maybe?
            print("Default model will be used")
            model_type = get_import(self.default_model.get("model_type"))
            kwargs = self.default_model.get('params')
            for item in self.items:
                name = item[0]
                T = self.__create_model(self.library)
                single_modal = T(self.date, name, model_type,
                                tracking_service=self.tracking_service,  **kwargs)
                single_modal.set_data(
                        self.train_idx_arr, self.val_idx_arr, item[1], item[2], item[3], item[4])

                logs, metrics, prediction = single_modal.fit_and_evaluate()
                self.result.add_metric(name, metrics)
                single_results[name] = prediction

    def predict(self, combinations: list = [], generate_combinations=False):
        self.prefix = utils.utc_time_as_string()
        self.date = utils.utc_time_as_string_simple_format()
        # sum = np.zeros(
        #     (self.y_test_label.shape[0], self.y_test_label.shape[1]))
        single_results = dict()

        if generate_combinations:
            l = [item[0] for item in self.items]
            combinations = []
            for i in range(2, len(l) + 1):
                combinations.extend(list(itertools.combinations(l, i)))  # all
                
        def _f():
            self.__predict(single_results)
            if combinations:
                self.evaluate_combinations(single_results, combinations)
            
        if self.tracking_service:
            self.tracking_service.run(run_name=self.prefix, description="***", func = _f , nested_run=False)
        else:
            self.__predict(single_results)
            if combinations:
                self.evaluate_combinations(single_results, combinations)
        # TODO: sum'a gerek yok
        return self.result

    def evaluate_combinations(self, single_results, combinations):
        for combination in combinations:
            combination_descriptor = '-'.join(combination)
            if self.tracking_service:
                def evaluate_combination(artifact_uri=None):
                    self.__evaluate_combinations(
                        single_results, combination, combination_descriptor, artifact_uri
                )
                 
                self.tracking_service.run(run_name=combination_descriptor, 
                                          description="***", 
                                          nested_run=True, 
                                          func=evaluate_combination)
                
                # with mlflow.start_run(run_name=combination_descriptor, description="***", nested=True) as combination_run:
                #     self.__evaluate_combinations(
                #         single_results, combination, combination_descriptor, combination_run.info.artifact_uri)
            else:
                self.__evaluate_combinations(
                    single_results, combination, combination_descriptor, None)

    def __evaluate_combinations(self, single_results, combination, combination_descriptor, artifact_uri):
        prediction = np.zeros(
            (self.y_test_label.shape[0], self.y_test_label.shape[1]))
        for item in combination:
            prediction = prediction + single_results[item]
        prediction = utils.to_one_hot_encode(prediction)
        logs, metrics = evaluate(
            actual=self.y_test_label, pred=prediction, info=combination_descriptor)
        if self.tracking_service:
            self.tracking_service.log_metrics(logs)
        metrics.format_float()
        # TODO path bulunamadı hatası aldık
        if artifact_uri:
            print(
                f'combination_artifact_uri:{artifact_uri}')
            utils.compress_and_save_data(
                metrics.__dict__, artifact_uri, f'{self.date}_metrics.gzip')
        # self.result.add_log(combination_descriptor,logs)
        # self.result.add_metric(combination_descriptor,metrics)
