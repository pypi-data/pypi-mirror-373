
import pickle
import os
import numpy as np



"""-----------------------------------------------------------------------------------------
    File Management Functions
-----------------------------------------------------------------------------------------"""

def scan_folder_for_files(folder, types):
    files = []

    for filename in os.listdir(folder):
        for file_type in types:
            if filename.endswith(file_type):
                files.append(os.path.join(folder, filename))

    return np.array(files)


def save_pickle(obj, filename: str) -> None:
    with open(filename, "wb") as f:
        pickle.dump(obj, f)


def load_pickle(path):
    with open(path, 'rb') as f:
        obj = pickle.load(f)
    return obj
