from collections import defaultdict
import numpy as np
import pandas as pd

def find_distinct_elements(frame):
    y = set()
    for x in frame:
        if x is not None:
            for k in x:
                y.add(k)
    return y

class IDF:
    def __init__(self, dataframe, columns):
        self.dataframe = dataframe
        self.columns = columns

    def calculate(self):
        idf_scores = defaultdict(dict)
        total_document_number = self.dataframe.shape[0]
        for column in self.columns:
            score = dict()
            idf_scores[column] = score
            for e in self.dataframe[column]:
                if e is not None:
                    for item in e:
                        if item in score:
                            score[item] = score[item] +1
                        else:
                            score[item] = 1.0
            for key,value in score.items():
                score[key]= np.log(1.0 * total_document_number /  value)
        self.idf_scores = idf_scores

    def calculate_old(self):
        self.idf_scores = defaultdict(dict)
        for column in self.columns:
            data = self.dataframe[column]
            self.distinct_items = find_distinct_elements(data)
            #sorted_distinct_items = sorted(self.distinct_items)
            total_document_number = data.shape[0]
            for item in self.distinct_items:
                document_freq = data.map(set([item]).issubset).sum()
                idf = np.log(total_document_number/document_freq)
                self.idf_scores[column][item] = idf

    def to_dataframe(self):
        return pd.DataFrame.from_dict(self.idf_scores)


# class IDF:
#     def __init__(self, data, threshold = 0):
#         self.data = data
#         self.threshold = threshold
#         self.distinct_items = find_distinct_elements(data)

#     def calculate(self):
#         self.idf_scores = {}
#         sorted_distinct_items = sorted(self.distinct_items)
#         total_document_number = self.data.shape[0]
#         for item in sorted_distinct_items:
#             document_freq = self.data.map(set([item]).issubset).sum()
#             idf = np.log(total_document_number/document_freq)
#             self.idf_scores[item] = idf

#     def find_items_over_threshold(self):
#         return [k for k,v in self.idf_scores.items() if v > self.threshold]
    
#     def filter_dict_by_threshold(self):
#         return {k:v for k,v in self.idf_scores.items() if v > self.threshold}
 