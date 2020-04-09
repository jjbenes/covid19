# -*- coding: utf-8 -*-
"""Module for computing cases"""
import numpy as np
import pandas as pd
from fp_covid19.data.bears import Bears

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
  return type(bears)(dataframe=new_df, datetime_fmt=bears.datetime_fmt)

def per_capita(bears: Bears, population: pd.DataFrame) -> Bears:
  """Computes per-capita cases.

  Args:
    bears (Bears): `Bears` time-series
    population (pd.DataFrame): Population dataframe as returned by, for
      instance, :py:func:`get_us_population()`.
  """
  per_capita_b = bears.copy(deep=True)
  per_capita_b.df.loc[:, bears.datetime_index] = (
      bears.df.loc[:, bears.datetime_index].truediv(population, axis='index'))
  per_capita_b.df = per_capita_b.df[
      ~per_capita_b.df.isin([np.nan, np.inf, -np.inf]).any(1)]
  return per_capita_b
