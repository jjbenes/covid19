# -*- coding: utf-8 -*-
"""New cases"""
from typing import List
import numpy as np
import pandas as pd

def new_cases_df(
    dataframe: pd.DataFrame, datetime_index: List[str]) -> pd.DataFrame:
  """Computes new case in DataFrame"""
  assert len(datetime_index) > 1
  new_df = dataframe.copy()
  new_df[datetime_index] = (
      dataframe[datetime_index].diff(periods=1, axis='columns'))
  new_df.drop(datetime_index[0], 'columns', inplace=True)
  return new_df

def per_capita_df(
    dataframe: pd.DataFrame,
    datetime_index: List[str],
    population: pd.DataFrame) -> pd.DataFrame:
  """Computes per-capita cases.

  Args:
    dataframe: Contains time series for number of cases.
    datetime_index: List of column labels for time series
    population:
  """
  per_capita = dataframe.copy(deep=True)
  per_capita.loc[:, datetime_index] = (
      dataframe.loc[:, datetime_index].truediv(population, axis='index'))
  return per_capita[~per_capita.isin([np.nan, np.inf, -np.inf]).any(1)]
