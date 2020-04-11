# -*- coding: utf-8 -*-
"""A Python Class that Encapsulates a Panda Series or Dataframe"""
from __future__ import annotations
from abc import ABC
from typing import List, Tuple
import copy
import datetime
from collections import namedtuple
import pandas as pd

CsvSpecs = namedtuple('CsvSpecs', ['url', 'uid_col_label', 'encoding'])
""" CSV Specifications

.. py:attribute:: url

    URL of the CSV file

.. py:attribute:: uid_col_label

    Column label for the unique ID. If missing, insert a unique-ID column
    in the CSV file before using this package.

.. py:attribute:: encoding

   Python standard encoding
   (https://docs.python.org/3/library/codecs.html#standard-encodings),
   for instance, `ISO-8859-1`
"""

class Bears(ABC):
  """Pandas are more like bears than racoons, DNA-wise."""
  def __init__(
      self,
      datetime_fmt: str = '%m/%d/%y',
      from_csv: bool = None,
      csv_specs: CsvSpecs = None,
      dataframe: pd.DataFrame = None):
    assert isinstance(datetime_fmt, str), (
        'Argument `datetime_fmt` must be a string but is instead of '
        'type {}'.format(type(datetime_fmt)))
    assert from_csv or dataframe is not None, (
        'Use either `from_csv` and `csv_specs` or `dataframe`')
    self._datetime_fmt = datetime_fmt
    if from_csv:
      self._df = self.read_time_series_csv(csv_specs, datetime_fmt)
    else:
      self._df = dataframe

  def __repr__(self) -> str:
    """Returns a string representation of this object"""
    return ('{}\n{}\n{}'.format(
        self.non_datetime_index.__repr__(),
        self.datetime_index.__repr__(),
        self.df.__repr__()))

  def _repr_html_(self) -> str:
    """For IPython notebook display"""
    return  r'''
    <p><b>Datetime format: {}</b></p>
    <p><b>Non Datetime Columns: </b> {}</p>
    <p><b>Datetime Columns:</b> {}</p>
    <p>{}</p>
    '''.format(
        self.datetime_fmt,
        self.non_datetime_index,
        self.datetime_index,
        self.df._repr_html_()) # pylint: disable=protected-access

  @property
  def df(self):
    """Returns `Pandas` dataframe initialized by `read_time_series_csv()`"""
    return self._df

  @df.setter
  def df(self, dataframe): # pylint: disable=invalid-name
    self._df = dataframe

  @property
  def datetime_fmt(self):
    """Returns datetime format suitable for `datetime`"""
    return self._datetime_fmt

  @property
  def non_datetime_index(self):
    """Returns non-datetime column labels in the `Pandas` dataframe"""
    non_datetime_index, _ = self.partition_datetime_columns(
        self.datetime_fmt)
    return non_datetime_index

  @property
  def datetime_index(self):
    """Returns datetime column labels in the `Pandas` dataframe"""
    _, datetime_index = self.partition_datetime_columns(
        self.datetime_fmt)
    return datetime_index

  def read_time_series_csv(
      self, csv_specs: CsvSpecs, datetime_fmt: str) -> pd.DataFrame:
    """Initializes obejct from a CSV file

    This function must keep all member variables self-consistent.

    Args:
      csv_specs.url (str): URL of the CSV file.
      csv_specs.unique_id_col_label (str): Column label of the unique ID.
        Used as the `Pandas` index if not `None`. If `None`, `Pandas`
        generates unique row indices.
      csv_specs.encoding (str): Encoding of CSV file, e.g. `ISO-8859-1`
      datetime_fmt (str): Datetime format, e.g. '%m/%d/%y'

    Returns:
      pd.DataFrame` read from the input CSV file
    """
    raise NotImplementedError

  def partition_datetime_columns(
      self, datetime_fmt='%m/%d/%y') -> Tuple[List, List]:
    """Partitions dataframe columns into non-datetime vs. datetime"""
    # Time-series column labels are packed to the right
    first_date_col = None
    for first_date_col_label in self.df.columns:
      first_date_col = 0 if first_date_col is None else first_date_col + 1
      try:
        datetime.datetime.strptime(first_date_col_label, datetime_fmt)
        break
      except ValueError:
        continue
    assert first_date_col is not None and first_date_col < self.df.shape[1], (
        'Could not find time-series column labels in the form {fmt}. Expected '
        'a consecutive list of date labels but instead saw this list of '
        'column labels: {col_labels}').format(
            fmt=datetime_fmt, col_labels=self.df.columns)
    for should_be_date_label in self.df.columns[first_date_col:]:
      try:
        datetime.datetime.strptime(should_be_date_label, datetime_fmt)
      except ValueError:
        raise ValueError((
            'Expecting all column labels to be dates starting with {} in '
            '{}').format(self.df[first_date_col], self.df.columns))
    return (self.df.columns[0:first_date_col].tolist(),
            self.df.columns[first_date_col:].tolist())

  def copy(self, deep=True) -> Bears:
    """Makes a copy of the Pandas `DataFrame`.

    Args:
      deep (bool): `True` if deep copy. Calls `pd.DataFrame.copy(deep)`.

    Returns:
      A new instance of `Bears`
    """
    new_self = copy.copy(self)
    new_self.df = self.df.copy(deep)
    return new_self

  def latest(self, deep=True) -> Bears:
    """Returns the latest date in the time series"""
    new_self = self.copy(deep)
    new_self.df = new_self.df[
        new_self.non_datetime_index + [new_self.datetime_index[-1]]]
    return new_self
