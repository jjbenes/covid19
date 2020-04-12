# -*- coding: utf-8 -*-
"""Johns Hopkins CSSE COVID-19 Data Import"""
from __future__ import annotations
from typing import Dict
import numpy as np
import pandas as pd
from fp_covid19.data.bears import Bears, CsvSpecs
from fp_covid19.cases.compute import (
    counties2states_df, assert_all_not_na)

CSV_URL_ROOT = (
    'https://raw.githubusercontent.com/'
    'CSSEGISandData/COVID-19/master/csse_covid_19_data/'
    'csse_covid_19_time_series/')
CSV_FILE_PREFIX = 'time_series_covid19'
CSV_COL_UID = 'UID'
CSV_ENCODING = 'ISO-8859-1'
CSV_COLUMN_RENAME_DICT = {} # de facto standard

def attribution() -> str:
  """Returns data attribution string"""
  return (
      '\u0026copy; '
      '<a href="https://github.com/CSSEGISandData/COVID-19">'
      'Johns Hopkins University</a>. ')


def stitch_time_series_csv_url(
    db_type: str,
    region: str,
    url_root=CSV_URL_ROOT,
    file_prefix=CSV_FILE_PREFIX) -> str:
  """Helper function to form a time-series URL

  Args:
    url_root (str): URL prefix for the CSV.
    file_prefix (str): String before `db_type` in the URL.
    db_type (str): One of `confirmed`, `recovered`, and `deaths`.
    region (str): One of `US` and `global`.

  Returns:
    str:
    Concatenation of the arguments as a URL,
    `url_root + file_prefix + '_' + db_type + '_' + region + '.csv'`
  """
  return url_root + file_prefix + '_' + db_type + '_' + region + '.csv'


class JhuCsse(Bears):
  """JHU CSSE data import"""
  def read_time_series_csv(
      self, csv_specs: CsvSpecs) -> pd.DataFrame:
    """Converts JHU CSSE time-series CSV to Pandas `DataFrame`.

    Column labels:
    `UID,iso2,iso3,code3,FIPS,Admin2,Province_State,Country_Region,Lat,
    Long_,Combined_Key,<date0>,<date1>,...`

    Note:
      This function converts the FIPS code into a string without leading zeros.

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
      csv_specs (CsvSpecs): CSV URL and encoding specifications

    Returns:
      pd.DataFrame:
      Pandas dataframe object of the input CSV file
    """
    if csv_specs.uid_col_label:
      dataframe = pd.read_csv(
          csv_specs.url, encoding=csv_specs.encoding).set_index(
              csv_specs.uid_col_label)
    else:
      dataframe = pd.read_csv(csv_specs.url, encoding=csv_specs.encoding)

    # Turn FIPS into strings without leading zeros to match most GeoJSON files
    dataframe.loc[:, 'FIPS'] = (
        dataframe.FIPS.values.astype(np.int64).astype(str))
    return dataframe


def get_geo_df(
    url=(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/'
        'csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv'),
    uid_col_label=CSV_COL_UID) -> pd.DataFrame:
  """Creates Pandas data frame from the JHU geo code look-up table.

    `UID,iso2,iso3,code3,FIPS,Admin2,Province_State,Country_Region,Lat,
    Long_,Combined_Key`

    Args:
      url (str): URL to CSV
      uid_col_label (str): Unique ID. Shared across all JHU CSSE CSV files

    Returns:
      pd.DataFrame:
      Pandas `DataFrame` indexed by `uid_col_label`.
  """
  return pd.read_csv(url, encoding=CSV_ENCODING).set_index(
      uid_col_label)


def get_covid19_us_bears(
    url_root=CSV_URL_ROOT,
    file_prefix=CSV_FILE_PREFIX,
    uid_col_label=CSV_COL_UID,
    encoding=CSV_ENCODING) -> Dict[Dict[Bears]]:
  """Converts JHU CSSE U.S. confirmed and deaths CSV files to state and county
  `Bears` to a dictionary of dictionaries.

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
    covid19[db_type]['counties'] = JhuCsse(
        from_csv=True,
        csv_specs=CsvSpecs(
            url=stitch_time_series_csv_url(
                db_type, 'US', url_root=url_root, file_prefix=file_prefix),
            uid_col_label=uid_col_label,
            encoding=encoding))
    assert_all_not_na(covid19[db_type]['counties'].df, 'Province_State')
  for db_type in ['confirmed', 'deaths']:
    counties = covid19[db_type]['counties']
    covid19[db_type]['states'] = JhuCsse(
        dataframe=counties2states_df(counties.df, counties.datetime_index))
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
  # deaths file have an extra non-datetime column: "Population"
  covid19 = JhuCsse(
      from_csv=True,
      csv_specs=CsvSpecs(
          url=stitch_time_series_csv_url(
              'deaths', 'US',
              url_root=CSV_URL_ROOT,
              file_prefix=CSV_FILE_PREFIX),
          uid_col_label=CSV_COL_UID,
          encoding=CSV_ENCODING))
  population_col = covid19.non_datetime_index[-1]
  assert population_col == 'Population'
  population = {}
  population['counties'] = covid19.df[[
      'FIPS', 'Admin2', 'Province_State', population_col]].copy()
  population['states'] = population['counties'][
      ['Province_State', population_col]].pivot_table(
          index=['Province_State'], aggfunc=np.sum)
  population['states']['index'] = population['states'].index
  population['states'].set_index('index', inplace=True)
  population['states']['Province_State'] = population['states'].index
  return population
