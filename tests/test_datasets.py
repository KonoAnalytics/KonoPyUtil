import pandas as pd

from KonoPyUtil import list_datasets, load_dataset


def test_list_datasets_includes_bundled_dataset():
    assert "copa_rayados.2021.csv" in list_datasets()


def test_load_dataset_returns_dataframe():
    df = load_dataset("copa_rayados.2021.csv")
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (59, 7)


def test_load_dataset_unknown_name_returns_empty_frame():
    df = load_dataset("does_not_exist.csv")
    assert isinstance(df, pd.DataFrame)
    assert df.empty
