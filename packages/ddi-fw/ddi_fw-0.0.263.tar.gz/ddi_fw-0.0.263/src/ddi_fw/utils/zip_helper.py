import zipfile as z
import os
from os.path import basename
from collections import defaultdict
import math

from ddi_fw.utils.utils import create_folder_if_not_exists


def get_file_name_and_folder(file_path):
    file_path_components = file_path.split('/')
    file_name = file_path_components[-1]
    file_path = file_path[:len(file_name)*-1-1]
    return file_name, file_path


class ZipHelper:
    def __init__(self):
        pass

    def __zipdir__(self, file_path, zipf):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(file_path):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(file_path, '..')))

    def zip_dir(self, zip_name, file_path, output_path):
        create_folder_if_not_exists(output_path)
        with z.ZipFile(f'{output_path}/{zip_name}.zip', 'w', z.ZIP_DEFLATED) as zipf:
            self.__zipdir__(file_path, zipf)

    def zip_single_file(self, zip_name, file_path, output_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        with z.ZipFile(f'{output_path}/{zip_name}.zip', 'w', compression=z.ZIP_LZMA, compresslevel=z.ZIP_LZMA) as zipObj:
            zipObj.write(file_path, basename(file_path))

    def zip_as_multipart(self, zip_name, file_path, output_path, chunk_size):
        parent_folder = os.path.dirname(file_path)

        # parts_path = f"{parent_folder}/parts"
        # create_folder_if_not_exists(parts_path)
        # file_name, file_extension = os.path.splitext(file_path)
        # file_name = os.path.basename(file_path)
        file_name, folder = get_file_name_and_folder(file_path)

        if os.path.isdir(file_path):
            self.zip_dir(zip_name, file_path, output_path)
        elif os.path.isfile(file_path):
            self.zip_single_file(zip_name, file_path, output_path)
        else:
            return
        with open(output_path+'/'+zip_name+'.zip', 'rb') as f:
            chunk_number = 1
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                with open(f"{output_path}/{zip_name}.zip.part{chunk_number:03}", 'wb') as chunk_file:
                    chunk_file.write(chunk)
                chunk_number += 1
        if os.path.exists(output_path+'/'+zip_name+'.zip'):
            os.remove(output_path+'/'+zip_name+'.zip')

    def zip(self, zip_prefix, input_path, output_path, chunk_size):
        files_paths = [input_path+'/' + p for p in os.listdir(input_path)]
        count_of_chunks = math.ceil(len(files_paths) / chunk_size)
        zero_padding_length = len(str(int(count_of_chunks))) + 2

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        part = 1
        i = 0
        zip_dict = defaultdict(list)
        for filePath in files_paths:
            padded_part = f'{part}'.zfill(zero_padding_length)
            key = f'{zip_prefix}.{padded_part}'
            zip_dict[key].append(filePath)
            i += 1
            if i % chunk_size == 0:
                i = 0
                part += 1

        for key, value in zip_dict.items():
            with z.ZipFile(f'{output_path}/{key}.zip', 'w', compression=z.ZIP_LZMA, compresslevel=z.ZIP_LZMA) as zipObj:
                for file_path in value:
                    zipObj.write(file_path, basename(file_path))

    def extract_single_file(self, file_path, output_path):
        with z.ZipFile(file_path, 'r') as z1:
             z1.extractall(path=output_path)

    '''
    Extract zip files from the given path to the output path
    '''
    def extract(self, input_path, output_path):
        files_paths = [input_path+'/' + p for p in os.listdir(input_path)]
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for file_path in files_paths:
            if file_path.endswith('zip'):
                with z.ZipFile(file_path, 'r') as z1:
                    z1.extractall(path=output_path)
                    print(f'{file_path} has been extracted')

    def extract_multiparts(self, input_path, output_path, output_file):
        parts = [input_path+'/' + p for p in os.listdir(input_path)]
        sorted_parts = sorted(parts, key = lambda x: int(x.split(".")[-1][4:]))
        create_folder_if_not_exists(output_path)
        with open(f"{output_path}/{output_file}", 'wb') as outfile:
            for part in sorted_parts:
                with open(part, 'rb') as infile:
                    outfile.write(infile.read())
        self.extract_single_file(f"{output_path}/{output_file}", output_path)
        os.remove(f"{output_path}/{output_file}")


# if __name__ == "__main__":
#     helper = ZipHelper()
    # helper.zip(zip_prefix='drugs', input_path='drugbank/drugs',
    #            output_path='drugbank/drugs-zips', chunk_size=1000)
    # helper.extract(input_path='drugbank/drugs-zips',
    #                output_path='drugbank/drugs-extracted')
    # path = ''
    # import pandas as pd
    # d = {'col1': [1, 2], 'col2': [3, 4]}
    # df = pd.DataFrame(data=d)
    # df.to_pickle('test/dataframe.pickle')
    # helper.zip_single_file(file_path='test/dataframe.pickle',output_path='test/output', name='zip')
    # helper.extract(input_path='test/output', output_path='test/output')
