from collections import defaultdict
import math
from ddi_fw.utils.utils import clear_directory, create_folder_if_not_exists
import py7zr
import os
from os.path import basename

# https://py7zr.readthedocs.io/en/latest/user_guide.html
# import multivolumefile
#https://github.com/miurahr/py7zr/issues/497
class Py7ZipHelper:
    def __init__(self):
        pass

    def create_archive_from_file(self, archive_name, file_path, output_path):
        with py7zr.SevenZipFile(output_path+'/'+archive_name, 'w') as archive:
            # for file in files_to_archive:
            archive.write(file_path)

    def create_archive_from_folder(self, archive_name, folder_path, output_path):
        with py7zr.SevenZipFile(output_path+'/'+archive_name, 'w') as archive:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    archive.write(os.path.join(root, file),
                                  os.path.relpath(os.path.join(root, file),
                                                  os.path.join(folder_path, '..')))
                    # archive.write(root+"/"+file)

    def create_archive_multiparts(self, zip_name, file_path, output_path, chunk_size, delete_existing_files=True):
        parent_folder = os.path.dirname(file_path)
        if delete_existing_files:
            clear_directory(output_path)
        # parts_path = f"{parent_folder}/parts"
        create_folder_if_not_exists(output_path)
        # file_name, file_extension = os.path.splitext(file_path)
        # file_name = os.path.basename(file_path)
        # file_name, folder = get_file_name_and_folder(file_path)

        if os.path.isdir(file_path):
            self.create_archive_from_folder(zip_name, file_path, output_path)
        elif os.path.isfile(file_path):
            self.create_archive_from_file(zip_name, file_path, output_path)
        else:
            return
        with open(output_path+'/'+zip_name, 'rb') as f:
            chunk_number = 1
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                with open(f"{output_path}/{zip_name}.part{chunk_number:03}", 'wb') as chunk_file:
                    chunk_file.write(chunk)
                chunk_number += 1
        if os.path.exists(output_path+'/'+zip_name):
            os.remove(output_path+'/'+zip_name)

    def create_archive(self, zip_prefix, input_path, output_path, chunk_size):
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
            with py7zr.SevenZipFile(f'{output_path}/{key}.7z', 'w') as archive:
                for file_path in value:
                    archive.write(file_path, basename(file_path))

    def extract(self, input_path, output_path):
        files_paths = [input_path+'/' + p for p in os.listdir(input_path)]
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        for file_path in files_paths:
            if file_path.endswith('7z'):
                with py7zr.SevenZipFile(file_path, 'r') as z1:
                    z1.extractall(path=output_path)
                    print(f'{file_path} has been extracted')

    def extract_archive(self, archive_name, extract_path):
        with py7zr.SevenZipFile(archive_name, 'r') as archive:
            archive.extractall(path=extract_path)

    def extract_multiparts(self, input_path, output_path, output_file, remove_file = True):
        parts = [input_path+'/' + p for p in os.listdir(input_path)]
        sorted_parts = sorted(parts, key = lambda x: int(x.split(".")[-1][4:]))
        create_folder_if_not_exists(output_path)
        with open(f"{output_path}/{output_file}", 'wb') as outfile:
            for part in sorted_parts:
                with open(part, 'rb') as infile:
                    outfile.write(infile.read())
        self.extract_archive(f"{output_path}/{output_file}", output_path)
        if remove_file:
            os.remove(f"{output_path}/{output_file}")
