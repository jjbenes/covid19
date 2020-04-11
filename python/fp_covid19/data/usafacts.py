# -*- coding: utf-8 -*-
"""USAFacts COVID-19 Data Import"""
from __future__ import annotations
from typing import Dict
import numpy as np
import pandas as pd
from fp_covid19.data.bears import Bears, CsvSpecs
from fp_covid19.cases.compute import counties2states_df

CSV_URL_ROOT = (
    'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/')
CSV_FILE_PREFIX = 'covid'
CSV_FILE_SUFFIX = 'usafacts'
CSV_COL_UID = None
CSV_ENCODING = None #'ISO-8859-1'
CSV_DATETIME_FMT = '%m/%d/%y'
CSV_COLUMN_RENAME_DICT = {
    'countyFIPS': 'FIPS',
    'State': 'Province_State',
    'County Name': 'Admin2',
    'population': 'Population',
}

def attribution() -> str:
  """Returns data attribution string"""
  return (
      'Created with data by \u0026copy; <a href="https://usafacts.org">'
      'USAFacts</a>. ')


def stitch_time_series_csv_url(
    db_type: str,
    url_root=CSV_URL_ROOT,
    file_prefix=CSV_FILE_PREFIX,
    file_suffix=CSV_FILE_SUFFIX) -> str:
  """Helper function to form a time-series URL

  Args:
    url_root (str): URL prefix for the CSV.
    file_prefix (str): String before `db_type` in the URL.
    file_suffix (str): String after `db_type` in the URL.
    db_type (str): One of `confirmed`, `recovered`, and `deaths`.

  Returns:
    str:
    Concatenation of the arguments as a URL,
    `url_root + file_prefix + '_' + db_type + '_' + file_suffix + '.csv'`
  """
  return url_root + file_prefix + '_' + db_type + '_' + file_suffix + '.csv'

def _canonical_df(dataframe, column_rename_dict):
  """Map and order columns"""
  dataframe.rename(columns=column_rename_dict, inplace=True)
  # Turn FIPS into strings without leading zeros to match most GeoJSON files
  dataframe.loc[:, 'FIPS'] = (
      dataframe.FIPS.values.astype(np.int64).astype(str))
  # Create Combined_Key between counties and states
  # Do not add new column in the time-series columns area!
  current_cols = dataframe.columns.to_list()
  dataframe.loc[:, 'Combined_Key'] = dataframe['Admin2'].combine(
      dataframe['Province_State'],
      lambda series1, series2: series1 + ', ' + series2)
  return dataframe[['Combined_Key'] + current_cols]

class Usafacts(Bears):
  """USAFACTS data import"""
  def read_time_series_csv(
      self, csv_specs: CsvSpecs,
      datetime_fmt: str = CSV_FILE_PREFIX) -> pd.DataFrame:
    """Converts USAFACTS time-series CSV to Pandas `DataFrame`.

    * Column labels:
      `countyFIPS, County Name, State, stateFIPS, <date0>,<date1>,...`

    * `countyFIPS` is the unique ID column
    * `State` uses two-letter state codes, e.g. "New York" is `NY`.

    Note:
      This function converts the FIPS code into a string without leading zeros.

    Args:
      csv_specs (CsvSpecs): CSV URL and encoding specifications

    Returns:
      pd.DataFrame:
      Pandas dataframe object of the input CSV file
    """
    dataframe = pd.read_csv(csv_specs.url, encoding=csv_specs.encoding)
    dataframe = _canonical_df(
        dataframe, column_rename_dict=CSV_COLUMN_RENAME_DICT)
    return dataframe


def get_geo_df(
    url=(
        'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/'
        'covid_county_population_usafacts.csv')) -> pd.DataFrame:
  """Creates Pandas data frame from the USAFACTS geo code look-up table.

    `UID,iso2,iso3,code3,FIPS,Admin2,Province_State,Country_Region,Lat,
    Long_,Combined_Key`

    Args:
      url (str): URL to CSV

    Returns:
      pd.DataFrame:
      Pandas `DataFrame` indexed by `uid_col_label`.
  """
  geo_df = _canonical_df(
      dataframe=pd.read_csv(url, encoding=CSV_ENCODING),
      column_rename_dict=CSV_COLUMN_RENAME_DICT
  )
  return geo_df


def get_covid19_us_bears(
    url_root=CSV_URL_ROOT,
    file_prefix=CSV_FILE_PREFIX,
    file_suffix=CSV_FILE_SUFFIX,
    encoding=CSV_ENCODING,
    datetime_fmt=CSV_DATETIME_FMT) -> Dict[Dict[Bears]]:
  """Converts USAFACTS confirmed and deaths CSV files to state and county
  `Bears` to a dictionary of dictionaries

  Args:
    url_root (str): URL prefix for the CSV
    file_prefix (str): CSV file prefix
    uid_col_label (str): Unique ID column label
    encoding (str): CSV encoding

  Returns:
    Dict[Dict[Bears]]:
    ::

    {'confirmed': {'counties': Bears,
                   'states': Bears},
     'deaths': {'counties': Bears,
                'states': Bears}}
  """
  covid19 = {'confirmed': {'counties': None, 'states': None},
             'deaths': {'counties': None, 'states': None}}
  for db_type in ['confirmed', 'deaths']:
    covid19[db_type]['counties'] = Usafacts(
        from_csv=True,
        csv_specs=CsvSpecs(
            url=stitch_time_series_csv_url(
                db_type=db_type, url_root=url_root, file_prefix=file_prefix,
                file_suffix=file_suffix),
            uid_col_label=CSV_COL_UID,
            encoding=encoding),
        datetime_fmt=datetime_fmt)
  for db_type in ['confirmed', 'deaths']:
    counties = covid19[db_type]['counties']
    covid19[db_type]['states'] = Usafacts(
        dataframe=counties2states_df(counties.df, counties.datetime_index),
        datetime_fmt=counties.datetime_fmt)
  return covid19


def get_us_population() -> Dict:
  """Creates U.S. state and county population dataframes.

  Args:
    url_root (str): URL prefix for the CSV
    file_prefix (str): CSV file prefix
    uid_col_label (str): Unique ID column label. Used as the
      Pandas index.

  Examples:
    >>> population = get_us_population()
    >>> population['counties']
               FIPS      Admin2            Province_State  Population
    UID
    16           60         NaN            American Samoa       55641
    316          66         NaN                      Guam      164229
    580          69         NaN  Northern Mariana Islands       55144
    630          72         NaN               Puerto Rico     2933408
    850          78         NaN            Virgin Islands      107268
    ...         ...         ...                       ...         ...
    84090053  90053  Unassigned                Washington           0
    84090054  90054  Unassigned             West Virginia           0
    84090055  90055  Unassigned                 Wisconsin           0
    84090056  90056  Unassigned                   Wyoming           0
    84099999  99999         NaN            Grand Princess           0
    [3253 rows x 4 columns]
    >>> population['counties'][population['counties']['Province_State']=='Nevada']
               FIPS       Admin2 Province_State  Population
    UID
    84032001  32001    Churchill         Nevada       24909
    84032003  32003        Clark         Nevada     2266715
    84032005  32005      Douglas         Nevada       48905
    84032007  32007         Elko         Nevada       52778
    84032009  32009    Esmeralda         Nevada         873
    84032011  32011       Eureka         Nevada        2029
    84032013  32013     Humboldt         Nevada       16831
    84032015  32015       Lander         Nevada        5532
    84032017  32017      Lincoln         Nevada        5183
    84032019  32019         Lyon         Nevada       57510
    84032021  32021      Mineral         Nevada        4505
    84032023  32023          Nye         Nevada       46523
    84032027  32027     Pershing         Nevada        6725
    84032029  32029       Storey         Nevada        4123
    84032031  32031       Washoe         Nevada      471519
    84032033  32033   White Pine         Nevada        9580
    84032510  32510  Carson City         Nevada       55916
    84080032  80032    Out of NV         Nevada           0
    84090032  90032   Unassigned         Nevada           0
    >>> population['states'].sort_values(by='Population', ascending=False)
                              Population            Province_State
    index
    California                  39512223                California
    Texas                       28995881                     Texas
    New York                    23628065                  New York
    Florida                     21477737                   Florida
    Pennsylvania                12801989              Pennsylvania
    Illinois                    12671821                  Illinois
    Ohio                        11689100                      Ohio
    Georgia                     10617423                   Georgia
    North Carolina              10488084            North Carolina
    Michigan                     9986857                  Michigan
    New Jersey                   8882190                New Jersey
    ...

  Returns:
    Dict[Bears]:
    A dictionary of two U.S. population `Bears` objects, one for the states
    and one for the counties.
    ::

    {'states': Bears, 'counties': Bears}

      * The county population dataframe is indexed by `UID` and the column
        labels are `['FIPS', 'Admin2', 'Province_State', 'Population']`.
      * The state population dataframe is indexed by the name of the state.
        The column labels are `['Population', 'Province_State']`. The column
        `Province_State` is identical to the index, allowing Pandas operations
        to use either the index or this column label.
  """
  geo_df = get_geo_df()
  population_col = 'Population'
  population = {}
  population['counties'] = geo_df[[
      'FIPS', 'Admin2', 'Province_State', population_col]].copy()
  population['states'] = population['counties'][
      ['Province_State', population_col]].pivot_table(
          index=['Province_State'], aggfunc=np.sum)
  population['states']['index'] = population['states'].index
  population['states'].set_index('index', inplace=True)
  population['states']['Province_State'] = population['states'].index
  return population
