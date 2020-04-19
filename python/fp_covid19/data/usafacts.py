# -*- coding: utf-8 -*-
"""USAFacts COVID-19 Data Import"""
from __future__ import annotations
from typing import Dict
import numpy as np
import pandas as pd
from fp_covid19.data.bears import Bears, CsvSpecs
from fp_covid19.cases.compute import counties2states_df
from fp_covid19.visualization.geojson_helper import USPS_PUB28_DF

CSV_URL_ROOT = (
    'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/')
CSV_FILE_PREFIX = 'covid'
CSV_FILE_SUFFIX = 'usafacts'
CSV_COL_UID = None
CSV_ENCODING = None #'ISO-8859-1'
CSV_COLUMN_RENAME_DICT = {
    'countyFIPS': 'FIPS',
    'State': 'Province_State',
    'County Name': 'Admin2',
    'population': 'Population',
}

def attribution() -> str:
  """Returns data attribution string"""
  return '\u0026copy; <a href="https://usafacts.org">USAFacts</a>. '


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


def _long_state_names(
    dataframe: pd.DataFrame, state_col='Province_State') -> pd.DataFrame:
  """Converts 2-letter U.S. abbreviations to full names"""
  return dataframe[state_col].transform(
      lambda x: (
          USPS_PUB28_DF[['USPS', 'Province_State']]
          .set_index('USPS').loc[x,]))

def _unassigned_fips(dataframe: pd.DataFrame) -> pd.DataFrame:
  """Prepend 2-digit state FIPS code to 3-digit county code for
     unassigned areas"""
  return dataframe.FIPS.combine(
      dataframe.stateFIPS,
      lambda county_fips, state_fips: (
          (int(state_fips)*1000 + int(county_fips)) if county_fips == '0'
          else county_fips))


def _canonical_df(
    dataframe: pd.DataFrame, column_rename_dict: Dict) -> pd.DataFrame:
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
      self, csv_specs: CsvSpecs, drop_all_na_columns=True) -> pd.DataFrame:
    """Converts USAFACTS time-series CSV to Pandas `DataFrame`.

    This function converts the FIPS code into a string without leading zeros,
    and converts 2-letter U.S. abbreviations to their full names.

    USAFacts CSV files assigns 0 to `countyFIPS` for unallocated regions.
    There is one unallocated region for each state plus one for New York City.

    Args:
      csv_specs (CsvSpecs): CSV URL and encoding specifications
      drop_all_na_columns (bool): Drop columns that are completely empty
        (`pd.Dataframe.isna`).

    Returns:
      pd.DataFrame:
      Pandas dataframe object of the input CSV file
    """
    dataframe = super().read_time_series_csv(
        csv_specs=csv_specs, drop_all_na_columns=drop_all_na_columns)
    dataframe = _canonical_df(
        dataframe, column_rename_dict=CSV_COLUMN_RENAME_DICT)
    dataframe.loc[:, 'Province_State'] = _long_state_names(dataframe)
    dataframe.loc[:, 'FIPS'] = _unassigned_fips(dataframe)
    return dataframe


def get_geo_df(
    url=(
        'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/'
        'covid_county_population_usafacts.csv')) -> pd.DataFrame:
  """Creates Pandas data frame from the USAFACTS geo code look-up table.

    `UID,iso2,iso3,code3,FIPS,Admin2,Province_State,Country_Region,Lat,
    Long_,Combined_Key`

    This function converts the FIPS code into a string without leading zeros,
    and converts 2-letter U.S. abbreviations to their full names.

    Args:
      url (str): URL to CSV
      state_fips (pd.DataFrame): A data frame with at least two columns that
        maps a state name to a 2-digit FIPS code, e.g.
        `df.loc[:, ['Province_State', 'stateFIPS']]`

    Returns:
      pd.DataFrame:
      Pandas `DataFrame` indexed by `uid_col_label`.
  """
  dataframe = pd.read_csv(url, encoding=CSV_ENCODING)
  dataframe = (
      _canonical_df(
          dataframe=dataframe,
          column_rename_dict=CSV_COLUMN_RENAME_DICT)
      .rename(columns={'Province_State': 'USPS'}) # abbreviated
      .merge(
          on='USPS', # Also abbreviated
          right=USPS_PUB28_DF[['USPS', 'Province_State']]))
  return dataframe


def get_covid19_us_bears(
    url_root=CSV_URL_ROOT,
    file_prefix=CSV_FILE_PREFIX,
    file_suffix=CSV_FILE_SUFFIX,
    encoding=CSV_ENCODING) -> Dict[Dict[Bears]]:
  """Converts USAFACTS confirmed and deaths CSV files to state and county
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
    covid19[db_type]['counties'] = Usafacts(
        from_csv=True,
        csv_specs=CsvSpecs(
            url=stitch_time_series_csv_url(
                db_type=db_type, url_root=url_root, file_prefix=file_prefix,
                file_suffix=file_suffix),
            uid_col_label=CSV_COL_UID,
            encoding=encoding))
  for db_type in ['confirmed', 'deaths']:
    counties = covid19[db_type]['counties']
    covid19[db_type]['states'] = Usafacts(
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
            FIPS	             Admin2 Province_State	Population
    0        1000 Statewide Unallocated	       Alabama           0
    1	     1001	     Autauga County	       Alabama       55869
    2	     1003	     Baldwin County        Alabama      223234
    3	     1005	     Barbour County        Alabama       24686
    4	     1007	        Bibb County	       Alabama       22394
    ...	...	...	...	...
    3190	56037	  Sweetwater County	       Wyoming	     42343
    3191	56039      	   Teton County	       Wyoming	     23464
    3192	56041	       Uinta County	       Wyoming	     20226
    3193	56043	    Washakie County	       Wyoming	      7805
    3194	56045	      Weston County	       Wyoming	      6927
    3195 rows × 4 columns
    >>> population['counties'][population['counties']['Province_State']=='NV']
             FIPS	               Admin2	Province_State	Population
    1776	32000	Statewide Unallocated	        Nevada	         0
    1777	32001	     Churchill County	        Nevada	     24909
    1778	32003	         Clark County	        Nevada	   2266715
    1779	32005	       Douglas County	        Nevada	     48905
    1780	32007	          Elko County	        Nevada	     52778
    1781	32009	     Esmeralda County	        Nevada	       873
    1782	32011	        Eureka County	        Nevada	      2029
    1783	32013	      Humboldt County	        Nevada	     16831
    1784	32015	        Lander County	        Nevada	      5532
    1785	32017      	   Lincoln County	        Nevada	      5183
    1786	32019	          Lyon County	        Nevada	     57510
    1787	32021	       Mineral County	        Nevada	      4505
    1788	32023	           Nye County	        Nevada	     46523
    1789	32027	      Pershing County	        Nevada	      6725
    1790	32029	        Storey County	        Nevada	      4123
    1791	32031	        Washoe County	        Nevada	    471519
    1792	32033	    White Pine County	        Nevada	      9580
    1793	32510	          Carson City	        Nevada	     55916
    >>> population['states'].nlargest(5, 'Population')
                Population  Province_State
    index
    California    39512223  California
    Texas         28995881  Texas
    Florida       21477737  Florida
    New York	  19453561  New York
    Pennsylvania  12801989  Pennsylvania

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
