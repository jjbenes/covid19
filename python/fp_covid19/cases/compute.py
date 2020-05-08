# -*- coding: utf-8 -*-
"""Module for computing cases"""
from typing import Dict, List
from time import strptime, mktime
from dateutil.parser import parse
import numpy as np
import pandas as pd
from fp_covid19.data.bears import Bears

def check_cumulatives(in_dict: Dict) -> pd.DataFrame:
  """

  Args:
    in_dict (Dict[Dict[Bears]]): `Bears` objects supposedly carrying cumulative
      data in a nested dictionary of the form `in_dict[db_type][geo_level]`

  Returns:
    Tuple:
    ::

    `(not_monotonic_increasing_index[db_type][geo_level],
      not_exactly_cumulatives)`

    * A boolean `pd.DataFrame` indicating where decreasing cases
      over two consecutive days occurs.
    * A `pd.DataFrame` summarizing what fraction of the data shows decreases
  """
  not_monotonic_increasing_index = {}
  not_exactly_cumulatives = pd.DataFrame()
  for db_type, dicts in in_dict.items():
    not_monotonic_increasing_index[db_type] = {}
    for geo_level, bears in dicts.items():
      not_monotonic_increasing_index[db_type][geo_level] = bears.df[
          bears.datetime_index].T.apply(lambda x: not x.is_monotonic_increasing)
      not_exactly_cumulatives.loc[
          '{} ({} items)'.format(
              geo_level.capitalize(),
              len(not_monotonic_increasing_index[db_type][geo_level])
          ),
          db_type.capitalize()] = (
              not_monotonic_increasing_index[db_type][geo_level].sum()
              /len(not_monotonic_increasing_index[db_type][geo_level]))
  return not_monotonic_increasing_index, not_exactly_cumulatives


def new_cases(bears: Bears, periods=1) -> Bears:
  """Computes new cases.

  Args:
    bears (Bears): Time-series :math:`x[n]`
    periods (int): Time difference, :math:`p` to shift for computing
      :math:`y[n] = x[n] - x[n - p]`.

  Returns:
    The difference time-series :math:`y[n] = x[n] - x[n - p]`
  """
  assert len(bears.datetime_index) > 1
  new_df, datetime_index = bears.df.copy(), bears.datetime_index
  new_df[datetime_index] = (
      bears.df[datetime_index].diff(periods=periods, axis='columns'))
  return type(bears)(dataframe=new_df)

def per_capita(bears: Bears, population: pd.DataFrame) -> Bears:
  """Computes per-capita cases.

  Args:
    bears (Bears): `Bears` time-series
    population (pd.DataFrame): Population dataframe with only one column,
      for instance, using :py:func:`get_us_population()['Population']`.

  Returns:
    Bears
    Per-capita :py:class:`Bears` time-series
  """
  per_capita_b = bears.copy(deep=True)
  per_capita_b.df.loc[:, bears.datetime_index] = (
      bears.df.loc[:, bears.datetime_index].truediv(population, axis='index'))
  per_capita_b.df = per_capita_b.df[
      ~per_capita_b.df.isin([np.nan, np.inf, -np.inf]).any(1)]
  return per_capita_b


def assert_all_not_na(dataframe, col=None):
  """Asserts all fields in a col are not N/A."""
  notna_bool = (dataframe.notna().all() if col is None
                else dataframe[col].notna())
  assert notna_bool.all(), (
      'Found N/A cells in column {}: {}'.format(
          col, dataframe[not notna_bool] if col
          else dataframe[dataframe.notna()]))


def counties2states_df(
    counties_df: pd.DataFrame,
    sum_col_index: List[str],
    index='Province_State') -> pd.DataFrame:
  """Sums counties cases to create state-level data frame.

  Args:
    counties_df: County-level `DataFrame`
    sum_col_index (`[str]`): List of columns to be summed in parallel.
      Pandas' `pivot_table()` may reorder columns, so this function calls
      `reindex()` to preserve column order in `sum_col_index`.
    index: Output `DataFrame` row index as a string

  Returns:
    pd.DataFrame:
    States dataframe pivot table
  """
  return pd.pivot_table(
      counties_df.loc[:, [index] + sum_col_index],
      index=index,
      values=sum_col_index,
      aggfunc='sum').reindex(sum_col_index, axis=1)


def to_epoch(date_str: str, date_format: str = None) -> int:
  """Converts string to datetime to POSIX time.

  Args:
    date_str (str): Date as a string
    date_format (str): Date format, e.g. `%m/%d/%y`. If `None`, uses
      `dateutil.parser.parse()` to convert `date_str` to POSIX time

  Returns:
    int:
    POSIX time, a.k.a. seconds since the Epoch, Unix time, and Epoch time
  """
  return int(mktime(strptime(date_str, date_format)) if date_format
             else parse(date_str).timestamp())
