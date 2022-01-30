import os
import pandas as pd


def list_datasets():
    """
    List all datasets in KonoPyUtil library
    :return: a list of filenames corresponding to datasets
    """
    _here = os.path.abspath(os.path.dirname(__file__))
    data_directory = os.path.join(_here, "data")
    return os.listdir(data_directory)


def load_dataset(dataset):
    """
    Loads a specific dataset in KonoPyUtil library
    :param dataset: name of dataset (options can be found via list_datasets()
    :return: a Pandas dataframe of the requested dataset
    """
    _here = os.path.abspath(os.path.dirname(__file__))
    file_and_path = os.path.join(_here, "data", dataset)
    if dataset in list_datasets():
        return pd.read_csv(file_and_path)
    return pd.DataFrame()
