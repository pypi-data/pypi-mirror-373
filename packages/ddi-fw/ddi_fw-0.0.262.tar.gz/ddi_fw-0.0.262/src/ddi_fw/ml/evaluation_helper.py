from typing import Any, Dict, List, Literal, Union
import numpy as np
from pydantic import BaseModel, Field
from sklearn import metrics
from sklearn.metrics import accuracy_score, precision_recall_curve
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import auc
from sklearn.metrics import classification_report
from sklearn.preprocessing import OneHotEncoder


def __format__(d: Union[Dict[str, Union[List[float], float]], float], floating_number_precision=4) -> Union[Dict[str, Union[List[float], float]], float]:
    if isinstance(d, dict):
        d = {k: __round__(v, floating_number_precision) for k, v in d.items()}
    else:
        d = round(d, floating_number_precision)
    return d


def __round__(v, floating_number_precision=4) -> Union[List[float], float]:
    if type(v) is list or type(v) is set:
        return [round(item, floating_number_precision) for item in v]
    else:
        return round(v, floating_number_precision)


class Metrics(BaseModel):
    label: str
    accuracy: float = 0.0
    precision: Any = None
    recall: Any = None
    f1_score: Any = None
    roc_auc: Any = None
    roc_aupr: Any = None
    classification_report: Any = None

    def set_classification_report(self, classification_report):
        self.classification_report = classification_report

    def set_accuracy(self, accuracy):
        self.accuracy = accuracy

    def set_precision(self, precision):
        self.precision = precision

    def set_recall(self, recall):
        self.recall = recall

    def set_f1_score(self, f1_score):
        self.f1_score = f1_score

    def set_roc_auc(self, roc_auc):
        self.roc_auc = roc_auc

    def set_roc_aupr(self, roc_aupr):
        self.roc_aupr = roc_aupr

    def format_float(self, floating_number_precision=4):
        self.accuracy = round(self.accuracy, floating_number_precision)
        self.precision = __format__(self.precision, floating_number_precision)
        self.recall = __format__(self.recall, floating_number_precision)
        self.f1_score = __format__(self.f1_score, floating_number_precision)
        self.roc_auc = __format__(self.roc_auc, floating_number_precision)
        self.roc_aupr = __format__(self.roc_aupr, floating_number_precision)


# taken from https://github.com/YifanDengWHU/DDIMDL/blob/master/DDIMDL.py#L214
def roc_aupr_score(y_true, y_score, average="macro"):
    def _binary_roc_aupr_score(y_true, y_score):
        precision, recall, pr_thresholds = precision_recall_curve(
            y_true, y_score)
        # precision, recall, pr_thresholds = metrics.roc_curve(y, pred, pos_label=2)
        return auc(precision, recall)

    def _average_binary_score(binary_metric, y_true, y_score, average):  # y_true= y_one_hot
        if average == "binary":
            return binary_metric(y_true, y_score)
        if average == "micro":
            y_true = y_true.ravel()
            y_score = y_score.ravel()
        if y_true.ndim == 1:
            y_true = y_true.reshape((-1, 1))
        if y_score.ndim == 1:
            y_score = y_score.reshape((-1, 1))
        n_classes = y_score.shape[1]
        score = np.zeros((n_classes,))
        for c in range(n_classes):
            y_true_c = y_true.take([c], axis=1).ravel()
            y_score_c = y_score.take([c], axis=1).ravel()
            score[c] = binary_metric(y_true_c, y_score_c)
        return np.average(score)

    return _average_binary_score(_binary_roc_aupr_score, y_true, y_score, average)


def evaluate(actual: np.ndarray, pred: np.ndarray, info='', print_detail=False):
    y_true = actual
    y_pred = pred

    # Generate classification report
    c_report = classification_report(y_true, y_pred, output_dict=True)

    # Metrics initialization
    metrics = Metrics(label=info)

    n_classes = actual.shape[1]
    # n_classes = len(np.unique(actual))

    precision = {}
    recall = {}
    f_score = {}
    roc_aupr = {}
    roc_auc = {
        "weighted": 0.0,
        "macro": 0.0,
        "micro": 0.0
    }

    # Preallocate lists
    precision_vals: List[np.ndarray] = [np.array([]) for _ in range(n_classes)]
    recall_vals: List[np.ndarray] = [np.array([]) for _ in range(n_classes)]

    # Compute metrics for each class
    for i in range(n_classes):
        precision_vals[i], recall_vals[i], _ = precision_recall_curve(
            actual[:, i], pred[:, i])
        roc_aupr[i] = auc(recall_vals[i], precision_vals[i])

    # Calculate ROC AUC scores
    roc_auc["weighted"] = float(roc_auc_score(
        actual, pred, multi_class='ovr', average='weighted'))
    roc_auc["macro"] = float(roc_auc_score(
        actual, pred, multi_class='ovr', average='macro'))
    roc_auc["micro"] = float(roc_auc_score(
        actual, pred, multi_class='ovr', average='micro'))

    # Micro-average Precision-Recall curve and ROC-AUPR
    precision["micro_event"], recall["micro_event"], _ = precision_recall_curve(
        actual.ravel(), pred.ravel())
    roc_aupr["micro"] = auc(recall["micro_event"], precision["micro_event"])

    # Convert lists to numpy arrays for better performance
    precision["micro_event"] = precision["micro_event"].tolist()
    recall["micro_event"] = recall["micro_event"].tolist()

    # Overall accuracy
    acc = accuracy_score(y_true, y_pred)

    # Aggregate precision, recall, and f_score
    # for avg_type in ['weighted', 'macro', 'micro']:
    for avg_type in Literal['weighted', 'macro', 'micro'].__args__:
        precision[avg_type] = precision_score(y_true, y_pred, average=avg_type)
        recall[avg_type] = recall_score(y_true, y_pred, average=avg_type)
        f_score[avg_type] = f1_score(y_true, y_pred, average=avg_type)

    if print_detail:
        print(
            f'''Accuracy: {acc}
            , Precision:{precision['weighted']}
            , Recall: {recall['weighted']}
            , F1-score: {f_score['weighted']}
            ''')

    logs = {'accuracy': acc,
            'weighted_precision': precision['weighted'],
            'macro_precision': precision['macro'],
            'micro_precision': precision['micro'],
            'weighted_recall_score': recall['weighted'],
            'macro_recall_score': recall['macro'],
            'micro_recall_score': recall['micro'],
            'weighted_f1_score': f_score['weighted'],
            'macro_f1_score': f_score['macro'],
            'micro_f1_score': f_score['micro'],
            # 'weighted_roc_auc_score': weighted_roc_auc_score,
            # 'macro_roc_auc_score': macro_roc_auc_score,
            # 'micro_roc_auc_score': micro_roc_auc_score,
            # 'macro_aupr_score': macro_aupr_score,
            # 'micro_aupr_score': micro_aupr_score
            "micro_roc_aupr": roc_aupr['micro'],
            # "micro_precision_from_precision_recall_curve":precision["micro"],
            # "micro_recall_from_precision_recall_curve":recall["micro"],
            "weighted_roc_auc": roc_auc['weighted'],
            "macro_roc_auc": roc_auc['macro'],
            "micro_roc_auc": roc_auc['micro']
            }
    metrics.set_accuracy(acc)
    metrics.set_precision(precision)
    metrics.set_recall(recall)
    metrics.set_f1_score(f_score)
    metrics.set_roc_auc(roc_auc)
    metrics.set_roc_aupr(roc_aupr)
    metrics.set_classification_report(c_report)
    return logs, metrics


def evaluate_ex(actual, pred, info='', print_detail=False):
    # Precompute y_true and y_pred
    y_true = np.argmax(actual, axis=1)
    y_pred = np.argmax(pred, axis=1)

    # Generate classification report
    c_report = classification_report(y_true, y_pred, output_dict=True)

    # Metrics initialization
    metrics = Metrics(label=info)

    n_classes = actual.shape[1]

    precision = {}
    recall = {}
    f_score = {}
    roc_aupr = {}
    roc_auc = {
        "weighted": 0.0,
        "macro": 0.0,
        "micro": 0.0
    }

    # Preallocate lists
    precision_vals: List[np.ndarray] = [np.array([]) for _ in range(n_classes)]
    recall_vals: List[np.ndarray] = [np.array([]) for _ in range(n_classes)]

    # Compute metrics for each class
    for i in range(n_classes):
        precision_vals[i], recall_vals[i], _ = precision_recall_curve(
            actual[:, i], pred[:, i])
        roc_aupr[i] = auc(recall_vals[i], precision_vals[i])

    # Calculate ROC AUC scores
    roc_auc["weighted"] = float(roc_auc_score(
        actual, pred, multi_class='ovr', average='weighted'))
    roc_auc["macro"] = float(roc_auc_score(
        actual, pred, multi_class='ovr', average='macro'))
    roc_auc["micro"] = float(roc_auc_score(
        actual, pred, multi_class='ovr', average='micro'))

    # Micro-average Precision-Recall curve and ROC-AUPR
    precision["micro_event"], recall["micro_event"], _ = precision_recall_curve(
        actual.ravel(), pred.ravel())
    roc_aupr["micro"] = auc(recall["micro_event"], precision["micro_event"])

    # Convert lists to numpy arrays for better performance
    precision["micro_event"] = precision["micro_event"].tolist()
    recall["micro_event"] = recall["micro_event"].tolist()

    # Overall accuracy
    acc = accuracy_score(y_true, y_pred)

    # Aggregate precision, recall, and f_score
    # for avg_type in ['weighted', 'macro', 'micro']:
    for avg_type in Literal['weighted', 'macro', 'micro'].__args__:
        precision[avg_type] = precision_score(y_true, y_pred, average=avg_type)
        recall[avg_type] = recall_score(y_true, y_pred, average=avg_type)
        f_score[avg_type] = f1_score(y_true, y_pred, average=avg_type)

    if print_detail:
        print(
            f'''Accuracy: {acc}
            , Precision:{precision['weighted']}
            , Recall: {recall['weighted']}
            , F1-score: {f_score['weighted']}
            ''')

    logs = {'accuracy': acc,
            'weighted_precision': precision['weighted'],
            'macro_precision': precision['macro'],
            'micro_precision': precision['micro'],
            'weighted_recall_score': recall['weighted'],
            'macro_recall_score': recall['macro'],
            'micro_recall_score': recall['micro'],
            'weighted_f1_score': f_score['weighted'],
            'macro_f1_score': f_score['macro'],
            'micro_f1_score': f_score['micro'],
            # 'weighted_roc_auc_score': weighted_roc_auc_score,
            # 'macro_roc_auc_score': macro_roc_auc_score,
            # 'micro_roc_auc_score': micro_roc_auc_score,
            # 'macro_aupr_score': macro_aupr_score,
            # 'micro_aupr_score': micro_aupr_score
            "micro_roc_aupr": roc_aupr['micro'],
            # "micro_precision_from_precision_recall_curve":precision["micro"],
            # "micro_recall_from_precision_recall_curve":recall["micro"],
            "weighted_roc_auc": roc_auc['weighted'],
            "macro_roc_auc": roc_auc['macro'],
            "micro_roc_auc": roc_auc['micro']
            }
    metrics.set_accuracy(acc)
    metrics.set_precision(precision)
    metrics.set_recall(recall)
    metrics.set_f1_score(f_score)
    metrics.set_roc_auc(roc_auc)
    metrics.set_roc_aupr(roc_aupr)
    metrics.set_classification_report(c_report)
    return logs, metrics
