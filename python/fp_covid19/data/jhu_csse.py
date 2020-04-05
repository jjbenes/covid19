# -*- coding: utf-8 -*-
"""Johns Hopkins CSSE COVID-19 Data Import"""
from typing import List
import datetime
from posixpath import join as urljoin
import numpy as np
import pandas as pd

def get_geo_df(
    url=(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/'
        'csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv'),
    unique_id_col_label='UID') -> pd.DataFrame:
  """Creates Pandas data frame from the JHU geo code look-up table.

    `UID,iso2,iso3,code3,FIPS,Admin2,Province_State,Country_Region,Lat,
    Long_,Combined_Key`

    Args:
      url (str): URL to CSV
      unique_id_col_label (str): Unique ID. Shared across all JHU CSSE CSV files

    Returns:
      Pandas `DataFrame` indexed by `unique_id_col_label`.
  """
  return pd.read_csv(url, encoding='ISO-8859-1').set_index(
      unique_id_col_label)

def get_time_series_df(
    db_type: str,
    region: str,
    url_root=(
        'https://raw.githubusercontent.com/'
        'CSSEGISandData/COVID-19/master/csse_covid_19_data/'
        'csse_covid_19_time_series/'),
    file_prefix='time_series_covid19',
    unique_id_col_label='UID') -> pd.DataFrame:
  """Converts JHU CSSE time-series CSV to Pandas `DataFrame`.

  Column labels:
  `UID,iso2,iso3,code3,FIPS,Admin2,Province_State,Country_Region,Lat,
  Long_,Combined_Key,<date0>,<date1>,...`

  The complete URL of the data file is
  `url_root + file_prefix + '_' + db_type + '_' + region + '.csv'`.

  Note:
    This function converts the FIPS code into a string without leading zeros.
    Many geo json files are written this way.

  Note:
    As of 4/4/2020, the U.S. county file
    `csse_covid_19_time_series/time_series_covid19_confirmed_US.csv`
      * The unique ID field `UID` is roughly `concat(code3, FIPS)`
      * U.S. county names in Admin2
      * Some U.S. County Data Inconsistencies

        * "Dukes and Nantucket" and Kansas City have no FIPS.
        * Dukes and Nantucket should be two separate counties in MA but are
          listed as "Dukes and Nantucket."
        * Kansas City, MO is not a county but a city that spans multiple
          counties.

    For now, will not fix these problems. Ignore rows without FIPS in county
    data frame. Include them only at the state level.

  Args:
    db_type (str): One of `confirmed`, `recovered`, and `deaths`
    region (str): One of `US` and `global`
    url_root (str): URL prefix for the CSV
    file_prefix (str): String before `db_type` in the URL
    unique_id_col_label (str): Column label of the unique ID. Used as the
      Pandas index.

  Returns:
    Pandas data frame, non-datetime column labels, datetime column labels:
    `pandas.DataFrame, [str], [str]`
  """
  assert db_type in ['confirmed', 'recovered', 'deaths']
  assert region in ['US', 'global']

  url = urljoin(url_root, file_prefix + '_' + db_type + '_' + region + '.csv')
  try:
    jhu_df = pd.read_csv(
        url, encoding='ISO-8859-1').set_index(unique_id_col_label)
  except FileNotFoundError as mesg:
    raise FileNotFoundError((
        'Could not find COVID-19 {} cases for "{}"\n{}').format(
            db_type, region, mesg))
  # Time-series column labels are packed to the right
  first_date_col = None
  for first_date_col_label in jhu_df.columns:
    first_date_col = 0 if first_date_col is None else first_date_col + 1
    try:
      datetime.datetime.strptime(first_date_col_label, '%m/%d/%y')
      break
    except ValueError:
      continue
  assert first_date_col is not None and first_date_col < jhu_df.shape[1], (
      'Could not find time-series column labels. Expected a consecutive list '
      'of date labels in {url} but saw this list of column labels '
      '{col_labels}'.format(url=url, col_labels=jhu_df.columns))
  for should_be_date_label in jhu_df.columns[first_date_col:]:
    try:
      datetime.datetime.strptime(should_be_date_label, '%m/%d/%y')
    except ValueError:
      raise ValueError((
          'Expecting all column labels to be dates starting with {} in'
          'column labels {}').format(jhu_df[first_date_col], jhu_df.columns))
  jhu_df.loc[:, 'FIPS'] = (jhu_df.FIPS.values.astype(np.int64).astype(str))
  return (jhu_df,
          jhu_df.columns[0:first_date_col].tolist(),
          jhu_df.columns[first_date_col:].tolist())

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
  """
  return pd.pivot_table(
      counties_df.loc[:, [index] + sum_col_index],
      index=index,
      values=sum_col_index,
      aggfunc='sum').reindex(sum_col_index, axis=1)

def get_covid19_us_dfs(
    url_root=(
        'https://raw.githubusercontent.com/'
        'CSSEGISandData/COVID-19/master/csse_covid_19_data/'
        'csse_covid_19_time_series/'),
    file_prefix='time_series_covid19',
    unique_id_col_label='UID') -> pd.DataFrame:
  """Converts JHU CSSE U.S. confirmed and deaths CSV files to Pandas `DataFrame`

  Args:
    url_root (str): URL prefix for the CSV
    file_prefix (str): CSV file prefix
    unique_id_col_label (str): Column label of the unique ID. Used as the
      Pandas index.

  Returns
    A triple:
      * Dictionary of Pandas `pandas.DataFrame`s ,
      * non-datetime column label dictionary, and
      * datetime column labels.
        `{'confirmed': counties': None, 'states': None},
          'deaths': {'counties': None, 'states': None}}`
  """
  covid19 = {'confirmed': {'counties': None, 'states': None},
             'deaths': {'counties': None, 'states': None}}
  # deaths file have an extra non-datetime column: "Population"
  non_datetime_index = {'confirmed': None, 'deaths': None}
  for db_type in ['confirmed', 'deaths']:
    (covid19[db_type]['counties'],
     non_datetime_index[db_type],
     datetime_index) = get_time_series_df(
         db_type, 'US', url_root=url_root, file_prefix=file_prefix,
         unique_id_col_label=unique_id_col_label)
    assert_all_not_na(covid19[db_type]['counties'], 'Province_State')
  for db_type in ['confirmed', 'deaths']:
    covid19[db_type]['states'] = counties2states_df(
        covid19[db_type]['counties'], datetime_index)
  return covid19, non_datetime_index, datetime_index

def get_us_population(
    url_root=(
        'https://raw.githubusercontent.com/'
        'CSSEGISandData/COVID-19/master/csse_covid_19_data/'
        'csse_covid_19_time_series/'),
    file_prefix='time_series_covid19',
    unique_id_col_label='UID') -> pd.DataFrame:
  """Creates U.S. state and county population dataframes."""
  covid19, pop_non_datetime_index, _ = get_time_series_df(
      'deaths', 'US', url_root=url_root, file_prefix=file_prefix,
      unique_id_col_label=unique_id_col_label)
  population_col = pop_non_datetime_index[-1]
  assert population_col == 'Population'
  population = {}
  population['counties'] = covid19[[
      'FIPS', 'Admin2', 'Province_State', population_col]].copy()
  population['states'] = population['counties'][
      ['Province_State', population_col]].pivot_table(
          index=['Province_State'], aggfunc=np.sum)
  population['states']['index'] = population['states'].index
  population['states'].set_index('index', inplace=True)
  population['states']['Province_State'] = population['states'].index
  return population
