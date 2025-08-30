from typing import Any, Callable
from ddi_fw.ml.model_wrapper import ModelWrapper
import tensorflow as tf
from tensorflow import keras
# from keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, Callback
from sklearn.model_selection import train_test_split, KFold, StratifiedKFold
import numpy as np
from tensorflow.keras import Model
from ddi_fw.ml.evaluation_helper import Metrics, evaluate

# import tf2onnx
# import onnx

from ddi_fw.ml.tracking_service import TrackingService
import ddi_fw.utils as utils
import os


def convert_to_categorical(arr, num_classes):
    """
    This function takes an array of labels and converts them to one-hot encoding 
    if they are not binary-encoded. If the array is already in a 
    compatible format, it returns the original array.

    Parameters:
    - arr: numpy array with label data (could be binary-encoded or label-encoded)
    - num_classes: number of classes to be used in one-hot encoding

    Returns:
    - The one-hot encoded array if the original array was binary or label encoded
    - The original array if it doesn't require any conversion
    """

    try:
        # First, check if the array is binary-encoded
        if not utils.is_binary_encoded(arr):
            # If the arr labels are binary-encoded, convert them to one-hot encoding
            return tf.keras.utils.to_categorical(np.argmax(arr, axis=1), num_classes=num_classes)
        else:
            print("No conversion needed, returning original array.")
            return arr
    except Exception as e:
        # If binary encoding check raises an error, print it and continue to label encoding check
        print(f"Error while checking binary encoding: {e}")

    try:
        # Check if the array is label-encoded
        if utils.is_label_encoded(arr):
            # If the arr labels are label-encoded, convert them to one-hot encoding
            return tf.keras.utils.to_categorical(arr, num_classes=num_classes)
    except Exception as e:
        # If label encoding check raises an error, print it
        print(f"Error while checking label encoding: {e}")
        # If the arr labels don't match any of the known encodings, raise an error
        raise ValueError("Unknown label encoding format.")

    # If no conversion was needed, return the original array

    return arr


class TFModelWrapper(ModelWrapper):

    def __init__(self, date, descriptor, model_func, tracking_service: TrackingService | None = None, **kwargs):
        super().__init__(date, descriptor, model_func, **kwargs)
        self.batch_size = kwargs.get('batch_size', 128)
        self.epochs = kwargs.get('epochs', 100)
        self.tracking_service = tracking_service

    # TODO think different settings for num_classes
    def fit_model(self, X_train, y_train, X_valid, y_valid):
        self.kwargs['input_shape'] = self.train_data.shape
        self.num_classes = len(np.unique(y_train, axis=0))
        self.kwargs['num_classes'] = self.num_classes
        model = self.model_func(**self.kwargs)
        checkpoint = ModelCheckpoint(
            filepath=f'{self.descriptor}_validation.weights.h5',
            monitor='val_loss',
            save_best_only=True,
            save_weights_only=True,
            verbose=1,
            mode='min'
        )
        early_stopping = EarlyStopping(
            monitor='val_loss', patience=10, mode='auto')
        if self.tracking_service:
            custom_callback = CustomCallback(self.tracking_service)
            callbacks=[early_stopping, checkpoint, custom_callback]
        else:
            callbacks=[early_stopping, checkpoint]
        train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train))
        train_dataset = train_dataset.batch(batch_size=self.batch_size)

        if X_valid is not None and y_valid is not None:
            val_dataset = tf.data.Dataset.from_tensor_slices(
                (X_valid, y_valid))
            val_dataset = val_dataset.batch(batch_size=self.batch_size)
        else:
            val_dataset = None

        history = model.fit(
            train_dataset,
            epochs=self.epochs,
            validation_data=val_dataset,
            callbacks=callbacks
        )
        
            # Check if early stopping was applied
        if early_stopping.stopped_epoch > 0:
            print(f"Early stopping was applied at epoch {early_stopping.stopped_epoch}.")
        else:
            print("Early stopping was not applied.")
        if self.tracking_service:
            self.tracking_service.log_param("early_stopping_applied", early_stopping.stopped_epoch > 0)
            self.tracking_service.log_param("early_stopping_epoch", early_stopping.stopped_epoch)
        # ex
        # history = model.fit(
        #     X_train, y_train,
        #     batch_size=self.batch_size,
        #     epochs=self.epochs,
        #     validation_data=(X_valid, y_valid),
        #     callbacks=[early_stopping, checkpoint, custom_callback]
        # )

        if os.path.exists(f'{self.descriptor}_validation.weights.h5'):
            os.remove(f'{self.descriptor}_validation.weights.h5')

        return checkpoint.model, checkpoint

    def fit(self):
        print(self.train_data.shape)
        models = {}
        models_val_acc = {}
        if self.train_idx_arr and self.val_idx_arr:
            for i, (train_idx, val_idx) in enumerate(zip(self.train_idx_arr, self.val_idx_arr)):
                print(f"Validation {i}")
                X_train_cv = self.train_data[train_idx]
                y_train_cv = self.train_label[train_idx]
                X_valid_cv = self.train_data[val_idx]
                y_valid_cv = self.train_label[val_idx]

                def fit_model_cv_func():
                    model, checkpoint = self.fit_model(
                        X_train_cv, y_train_cv, X_valid_cv, y_valid_cv)
                    return model, checkpoint

                if self.tracking_service:
                    model, checkpoint = self.tracking_service.run(
                        run_name=f'Validation {i}', description='CV models', nested_run=True, func=fit_model_cv_func)
                    # with mlflow.start_run(run_name=f'Validation {i}', description='CV models', nested=True) as cv_fit:

                    #     model, checkpoint = self.fit_model(
                    #         X_train_cv, y_train_cv, X_valid_cv, y_valid_cv)
                    #     models[f'{self.descriptor}_validation_{i}'] = model
                    #     models_val_acc[f'{self.descriptor}_validation_{i}'] = checkpoint.best
                else:
                    model, checkpoint = fit_model_cv_func()
                    # model, checkpoint = self.fit_model(
                    #     X_train_cv, y_train_cv, X_valid_cv, y_valid_cv)
                models[f'{self.descriptor}_validation_{i}'] = model
                models_val_acc[f'{self.descriptor}_validation_{i}'] = checkpoint.best
        else:
            def fit_model_func():
                model, checkpoint = self.fit_model(
                    self.train_data, self.train_label, None, None)
                return model, checkpoint

            if self.tracking_service:
                model, checkpoint = self.tracking_service.run(
                    run_name=f'Training', description='Training', nested_run=True, func=fit_model_func)
                # with mlflow.start_run(run_name=f'Training', description='Training', nested=True) as cv_fit:
                #     model, checkpoint = self.fit_model(
                #         self.train_data, self.train_label, None, None)
                #     models[self.descriptor] = model
                #     models_val_acc[self.descriptor] = checkpoint.best
            else:
                model, checkpoint = fit_model_func()
                # models[self.descriptor] = model
                # models_val_acc[self.descriptor] = checkpoint.best
            models[self.descriptor] = model
            models_val_acc[self.descriptor] = checkpoint.best
        if models_val_acc == {}:
            return model, None
        best_model_key = max(models_val_acc, key=lambda k: models_val_acc[k])
        print("best model key: ", best_model_key)
        # best_model_key = max(models_val_acc, key=models_val_acc.get)
        best_model = models[best_model_key]
        return best_model, best_model_key

    # https://github.com/mlflow/mlflow/blob/master/examples/tensorflow/train.py

    def predict(self):
        test_dataset = tf.data.Dataset.from_tensor_slices(
            (self.test_data, self.test_label))
        test_dataset = test_dataset.batch(batch_size=1)
        # pred = self.best_model.predict(self.test_data)
        pred = self.best_model.predict(test_dataset)
        return pred

    # def fit_and_evaluate(self, print_detail=False) -> tuple[dict[str, Any], Metrics, Any]:
    #     if self.use_mlflow:
    #         with mlflow.start_run(run_name=self.descriptor, description="***", nested=True) as run:
    #             best_model, best_model_key = self.fit()
    #             self.best_model: Model = best_model
    #             pred = self.predict()
    #             actual = self.test_label
    #             # if not utils.is_binary_encoded(pred):
    #             #     pred = tf.keras.utils.to_categorical(np.argmax(pred,axis=1), num_classes=self.num_classes)
    #             pred_as_cat = convert_to_categorical(pred, self.num_classes)
    #             actual_as_cat = convert_to_categorical(
    #                 actual, self.num_classes)

    #             logs, metrics = evaluate(
    #                 actual=actual_as_cat, pred=pred_as_cat, info=self.descriptor, print_detail=print_detail)
    #             metrics.format_float()
    #             mlflow.log_metrics(logs)
    #             mlflow.log_param('best_cv', best_model_key)
    #             utils.compress_and_save_data(
    #                 metrics.__dict__, run.info.artifact_uri, f'{self.date}_metrics.gzip')
    #             mlflow.log_artifact(
    #                 f'{run.info.artifact_uri}/{self.date}_metrics.gzip')

    #             return logs, metrics, pred
    #     else:
    #         best_model, best_model_key = self.fit()
    #         self.best_model = best_model
    #         pred = self.predict()
    #         actual = self.test_label

    #         pred_as_cat = convert_to_categorical(pred, self.num_classes)
    #         actual_as_cat = convert_to_categorical(actual, self.num_classes)
    #         logs, metrics = evaluate(
    #             actual=actual_as_cat, pred=pred_as_cat, info=self.descriptor)
    #         metrics.format_float()
    #         return logs, metrics, pred

    def fit_and_evaluate(self, print_detail=False) -> tuple[dict[str, Any], Metrics, Any]:
        """
        Fit the model, evaluate it, and log results using the tracking service.

        Args:
            print_detail (bool): Whether to print detailed evaluation logs.

        Returns:
            tuple: A tuple containing logs, metrics, and predictions.
        """
        self.best_model: Model = None
        def evaluate_and_log(artifact_uri=None):
            # Fit the model
            best_model, best_model_key = self.fit()
            self.best_model = best_model

            # Make predictions
            pred = self.predict()
            actual = self.test_label

            # Convert predictions and actual labels to categorical format
            pred_as_cat = convert_to_categorical(pred, self.num_classes)
            actual_as_cat = convert_to_categorical(actual, self.num_classes)

            # Evaluate the model
            logs, metrics = evaluate(
                actual=actual_as_cat, pred=pred_as_cat, info=self.descriptor, print_detail=print_detail
            )
            metrics.format_float()

            if self.tracking_service:
                # Log metrics and parameters
                self.tracking_service.log_metrics(logs)
                self.tracking_service.log_param('best_cv', best_model_key)

                # Save metrics to the artifact URI if provided
                if artifact_uri:
                    utils.compress_and_save_data(
                        metrics.__dict__, artifact_uri, f'{self.date}_metrics.gzip'
                    )
                    self.tracking_service.log_artifact(
                        f'{artifact_uri}/{self.date}_metrics.gzip'
                    )

            return logs, metrics, pred

        # Use the tracking service to run the evaluation
        if self.tracking_service:
            return self.tracking_service.run(
                run_name=self.descriptor,
                description="Fit and evaluate the model",
                nested_run=True,
                func=evaluate_and_log
            )
        else:
            # If no tracking service is provided, run the evaluation directly
            return evaluate_and_log()


class CustomCallback(Callback):
    """
    Custom Keras callback for logging training metrics and model summary to MLflow.
    """
    def __init__(self, tracking_service: TrackingService):
        super().__init__()
        self.tracking_service = tracking_service

    # def _mlflow_log(self, func: Callable):
    #     if self.use_mlflow:
    #         func()

    def on_train_begin(self, logs=None):
        if logs is None:
            logs = {}
        if not isinstance(self.model, Model):
            raise TypeError("self.model must be an instance of Model")

        keys = list(logs.keys())

        self.tracking_service.log_param("train_begin_keys", keys)
        # self._mlflow_log(lambda: mlflow.log_param("train_begin_keys", keys))

        # config = self.model.optimizer.get_config()
        config = self.model.get_config()
        for attribute in config:
            self.tracking_service.log_param(
                "opt_" + attribute, config[attribute])
            # self._mlflow_log(lambda: mlflow.log_param(
            #     "opt_" + attribute, config[attribute]))

        sum_list = []
        self.model.summary(print_fn=sum_list.append)
        summary = "\n".join(sum_list)
        self.tracking_service.log_text(
            summary, file_name="model_summary.txt")
        # self._mlflow_log(lambda: mlflow.log_text(
        #     summary, artifact_file="model_summary.txt"))

    def on_train_end(self, logs=None):
        if logs is None:
            logs = {}
        print(logs)
        self.tracking_service.log_metrics(logs)
        # self._mlflow_log(lambda: mlflow.log_metrics(logs))

    def on_epoch_begin(self, epoch, logs=None):
        if logs is None:
            logs = {}
        keys = list(logs.keys())

    def on_epoch_end(self, epoch, logs=None):
        if logs is None:
            logs = {}
        keys = list(logs.keys())

    def on_test_begin(self, logs=None):
        if logs is None:
            logs = {}
        keys = list(logs.keys())

    def on_test_end(self, logs=None):
        if logs is None:
            logs = {}
        self.tracking_service.log_metrics(logs)
        # self._mlflow_log(lambda: mlflow.log_metrics(logs))
        print(logs)

    def on_predict_begin(self, logs=None):
        if logs is None:
            logs = {}
        keys = list(logs.keys())

    def on_predict_end(self, logs=None):
        if logs is None:
            logs = {}
        keys = list(logs.keys())
        self.tracking_service.log_metrics(logs)
        # self._mlflow_log(lambda: mlflow.log_metrics(logs))

    def on_train_batch_begin(self, batch, logs=None):
        if logs is None:
            logs = {}
        keys = list(logs.keys())

    def on_train_batch_end(self, batch, logs=None):
        if logs is None:
            logs = {}
        keys = list(logs.keys())

    def on_test_batch_begin(self, batch, logs=None):
        if logs is None:
            logs = {}
        keys = list(logs.keys())

    def on_test_batch_end(self, batch, logs=None):
        if logs is None:
            logs = {}
        keys = list(logs.keys())

    def on_predict_batch_begin(self, batch, logs=None):
        if logs is None:
            logs = {}
        keys = list(logs.keys())

    def on_predict_batch_end(self, batch, logs=None):
        if logs is None:
            logs = {}
        keys = list(logs.keys())
