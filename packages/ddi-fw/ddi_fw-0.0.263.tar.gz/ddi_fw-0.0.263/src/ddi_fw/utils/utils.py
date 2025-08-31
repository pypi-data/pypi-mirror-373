import gzip
import json
import os
from datetime import datetime, timezone
# from matplotlib import pyplot as plt
import shutil

def create_folder_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def utc_time_as_string():
    utc_datetime = datetime.now(timezone.utc)

    return datetime.strftime(utc_datetime, "%Y-%m-%dT%H:%M:%S.%f")[:-3]

def utc_time_as_string_simple_format():
    utc_datetime = datetime.now(timezone.utc)

    return datetime.strftime(utc_datetime, '%Y%m%d')

# https://gist.github.com/LouisAmon/4bd79b8ab80d3851601f3f9016300ac4


def compress_data(data):
    # Convert to JSON
    # json_data = json.dumps(data, indent=2)
    json_data = json.dumps(data, separators=(',', ":"))
    # Convert to bytes
    encoded = json_data.encode('UTF-8')
    # Compress
    compressed = gzip.compress(encoded)
    return compressed


def compress_and_save_data(data, path, file_name):
    compressed = compress_data(data)
    create_folder_if_not_exists(path)
    with gzip.open(path+f'/{file_name}', 'wb') as f:
        f.write(compressed)

def decompress(gzip_file):
    with gzip.open(gzip_file, 'r') as fin:        # 4. gzip
        json_bytes = fin.read()                      # 3. bytes (i.e. UTF-8)
    json_bytes = gzip.decompress(json_bytes)
    json_str = json_bytes.decode('UTF-8')            # 2. string (i.e. JSON)
    data = json.loads(json_str)
    return data


def clear_directory(directory_path):
    # Check if the directory exists
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        # Iterate through all files and directories in the directory
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            # Check if it's a file or a directory and remove it
            if os.path.isfile(item_path):
                os.remove(item_path)  # Remove file
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove directory
        print(f"Cleared contents of directory: {directory_path}")
    else:
        print(f"The directory does not exist: {directory_path}")


# if __name__ == "__main__":
#     # json_file = f'C:\\Users\\kivanc\\Downloads\\metrics.json'
#     # file_data = open(json_file, "r", 1).read()
#     # a = json.loads(file_data)  # store in json structure
#     # # a = {'key1':1, 'key2':2}
#     # compressed = compress_data(a)
#     # with gzip.open('deneme.gzip', 'wb') as f:
#     #     f.write(compressed)

#     # with gzip.open('deneme.gzip', 'r') as fin:        # 4. gzip
#     #     json_bytes = fin.read()                      # 3. bytes (i.e. UTF-8)
#     # json_bytes = gzip.decompress(json_bytes)
#     # json_str = json_bytes.decode('UTF-8')            # 2. string (i.e. JSON)
#     # data = json.loads(json_str)
#     # print(data)

#     gzip_file = f'C:\\Users\\kivanc\\Downloads\\metrics (2).gzip'
#     stored_file =  f'C:\\Users\\kivanc\\Downloads\\save.png'
#     metrics = decompress(gzip_file)
#     # print(metrics)

#     # Plot Precision-Recall curves for each class and micro-average
#     fig = plt.figure()
#     plt.step(metrics['recall']['micro_event'], metrics['precision']['micro_event'],
#              color='b', alpha=0.2, where='post')
#     plt.fill_between(
#         metrics['recall']["micro_event"], metrics['precision']["micro_event"], step='post', alpha=0.2, color='b')

#     # for i in range(65):
#     #     plt.step( metrics['recall'][str(i)],  metrics['precision'][str(i)], where='post',
#     #              label='Class {0} (AUC={1:0.2f})'.format(i, metrics['roc_aupr'][str(i)]))

#     plt.xlabel('Recall')
#     plt.ylabel('Precision')
#     plt.ylim([0.0, 1.05])
#     plt.xlim([0.0, 1.0])
#     plt.title(
#         'Micro-average Precision-Recall curve: AUC={0:0.2f}'.format(metrics['roc_aupr']["micro"]))
#     plt.legend(loc='best')
#     plt.savefig(stored_file)
#     # plt.show()

#     import plotly.express as px
#     import pandas as pd
#     df = pd.DataFrame(dict(
#     r=[1, 5, 2, 2, 3],
#     theta=['processing cost','mechanical properties','chemical stability',
#             'thermal stability', 'device integration']))
#     fig = px.line_polar(df, r='r', theta='theta', line_close=True)
#     fig.show()