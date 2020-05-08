# -*- coding: utf-8 -*-
"""Helper Library for GeoJSON"""
from typing import Dict
import urllib
import geojson
import pandas as pd
import geopandas as gpd

STATES_JSON = ('https://raw.githubusercontent.com/jjbenes/covid19/master/json/'
               'us-states.json')
COUNTIES_JSON = ('https://first-principles.ai/geojson/us-counties.json')

US_ATLANTA_METRO_FIPS = [
    '13013', '13015', '13035', '13045', '13057', '13063', '13067', '13077',
    '13085', '13089', '13097', '13113', '13117', '13121', '13135', '13139',
    '13143', '13149', '13151', '13159', '13171', '13199', '13211', '13217',
    '13223', '13227', '13231', '13247', '13255', '13297']
"""U.S. Atlanta Metropolitan Area: [
   'Barrow County, GA', 'Bartow County, GA' , 'Butts County, GA',
   'Carroll County, GA', 'Cherokee County, GA', 'Clayton County, GA',
   'Cobb County, GA', 'Coweta County, GA', 'Dawson County, GA',
   'DeKalb County, GA', 'Douglas County, GA', 'Fayette County, GA',
   'Forsyth County, GA', 'Fulton County, GA', 'Gwinnett County, GA',
   'Hall County, GA', 'Haralson County, GA', 'Heard County, GA',
   'Henry County, GA', 'Jasper County, GA', 'Lamar County, GA',
   'Meriwether County, GA', 'Morgan County, GA', 'Newton County, GA',
   'Paulding County, GA', 'Pickens County, GA', 'Pike County, GA',
   'Rockdale County, GA', 'Spalding County, GA', 'Walton County, GA']
"""

US_CHICAGO_METRO_FIPS = [
    '17031', '17037', '17043', '17063', '17089', '17091', '17093', '17097',
    '17111', '17197', '18073', '18089', '18111', '18127', '55059']
""" U.S. Chicago Metropolitan Area:[
    'Cook County, IL', 'DeKalb County, IL', 'DuPage County, IL',
    'Grundy County, IL', 'Kankakee County, IL', 'Kane County, IL',
    'Kendall County, IL', 'McHenry County, IL', 'Will County, IL',
    'Jasper County, IN', 'Lake County, IN', 'Newton County, IN',
    'Porter County, IN', 'Lake County, IL', 'Kenosha County, WI']
"""

US_DALLAS_FORT_WORTH_METRO_FIPS = [
    '48085', '48113', '48121', '48139', '48231', '48251', '48257', '48367',
    '48397', '48439', '48497']
""" U.S. Dallas-Fort-Worth Metroplex: [
   'Collin County, TX', 'Dallas County, TX', 'Denton County, TX',
   'Ellis County, TX', 'Hunt County, TX', 'Kaufman County, TX',
   'Rockwall County, TX', 'Johnson County, TX', 'Parker County, TX',
   'Tarrant County, TX', 'Wise County, TX']
"""

US_GREATER_BOSTON_FIPS = [
    '25009', '25017', '25021', '25023', '25025', '33015', '33017']
"""U.S. Greater Boston: [
   'Norfolk County, MA', 'Plymouth County, MA', 'Suffolk County, MA',
   'Essex County, MA', 'Middlesex County, MA', 'Rockingham County, NH',
   'Strafford County, NH']
"""

US_GREATER_HOUSTON_FIPS = [
    '48015', '48039', '48071', '48157', '48167', '48201', '48291', '48339',
    '48473']
"""U.S. Greater Houston: [
   'Harris County, TX', 'Fort Bend County, TX', 'Montgomery County, TX',
   'Brazoria County, TX', 'Galveston County, TX', 'Liberty County, TX',
   'Waller County, TX', 'Chambers County, TX', 'Austin County, TX']
"""

US_GREATER_LA_FIPS = ['6037', '6059', '6065', '6071', '6111']
"""U.S. Greater Los Angeles: Los Angeles, Orange, Riverside, San Bernadino,
   Ventura
"""

US_GREATER_PHILADELPHIA_FIPS = [
    '10003', '24015', '34005', '34007', '34015', '34033', '42017', '42029',
    '42045', '42091', '42101']
"""U.S. Greater Philadelphia: [
   'Burlington County, NJ', 'Camden County, NJ', 'Gloucester County, NJ',
   'Bucks County, PA', 'Chester County, PA', 'Montgomery County, PA',
   'Delaware County, PA', 'Philadelphia County, PA',
   'New Castle County, DE', 'Cecil County, MD', 'Salem County, NJ']
"""

US_MIAMI_METRO_FIPS = ['12011', '12086', '12099']
"""U.S. Miami Metropolitan Area: [
   'Miami-Dade County, FL', 'Broward County, FL', 'Palm Beach County, FL']
"""

US_SF_BAY_AREA_FIPS = ['6001', '6013', '6041', '6055', '6075',
                       '6081', '6085', '6095', '6097']
"""U.S. San Francisco Bay Area: Alameda, Contra Costa, Marin, Napa,
   San Francisco, San Mateo, Santa Clara, Solano, and Sonoma"""

US_NYC_FIPS = ['36005', '36047', '36061', '36081', '36085']
"""U.S. New York City FIPS: Bronx, Kings (Brooklyn), New York (Manhattan),
   Queens, and Richmond (Staten Island)"""

US_METROS = {
    'Atlanta Metropolian Area, GA': US_ATLANTA_METRO_FIPS,
    'Chicago Metropolitan Area, IL, IN, WI': US_CHICAGO_METRO_FIPS,
    'Dallas-Fort Worth Metroplex, TX': US_DALLAS_FORT_WORTH_METRO_FIPS,
    'Greater Boston, MA, NH': US_GREATER_BOSTON_FIPS,
    'Greater Houston, TX': US_GREATER_HOUSTON_FIPS,
    'Greater Los Angeles, CA': US_GREATER_LA_FIPS,
    'Greater Philadelphia, DE, NJ, PA': US_GREATER_PHILADELPHIA_FIPS,
    'Miami Metropolitan Area, FL': US_MIAMI_METRO_FIPS,
    'New York City, NY': US_NYC_FIPS,
    'San Francisco Bay Area, CA': US_SF_BAY_AREA_FIPS,
}

USPS_PUB28_DF = pd.DataFrame(
    [
        ['AL', 'Alabama', '1', '1000'],
        ['AK', 'Alaska', '2', '2000'],
        ['AZ', 'Arizona', '4', '4000'],
        ['AR', 'Arkansas', '5', '5000'],
        ['CA', 'California', '6', '6000'],
        ['CO', 'Colorado', '8', '8000'],
        ['CT', 'Connecticut', '9', '9000'],
        ['DC', 'District of Columbia', '10', '10000'],
        ['DE', 'Delaware', '11', '11000'],
        ['FL', 'Florida', '12', '12000'],
        ['GA', 'Georgia', '13', '13000'],
        ['HI', 'Hawaii', '15', '15000'],
        ['ID', 'Idaho', '16', '16000'],
        ['IL', 'Illinois', '17', '17000'],
        ['IN', 'Indiana', '18', '18000'],
        ['IA', 'Iowa', '19', '19000'],
        ['KS', 'Kansas', '20', '20000'],
        ['KY', 'Kentucky', '21', '21000'],
        ['LA', 'Louisiana', '22', '22000'],
        ['ME', 'Maine', '23', '23000'],
        ['MD', 'Maryland', '24', '24000'],
        ['MA', 'Massachusetts', '25', '25000'],
        ['MI', 'Michigan', '26', '26000'],
        ['MN', 'Minnesota', '27', '27000'],
        ['MS', 'Mississippi', '28', '28000'],
        ['MO', 'Missouri', '29', '29000'],
        ['MT', 'Montana', '30', '30000'],
        ['NE', 'Nebraska', '31', '31000'],
        ['NV', 'Nevada', '32', '32000'],
        ['NH', 'New Hampshire', '33', '33000'],
        ['NJ', 'New Jersey', '34', '34000'],
        ['NM', 'New Mexico', '35', '35000'],
        ['NY', 'New York', '36', '36000'],
        ['NC', 'North Carolina', '37', '37000'],
        ['ND', 'North Dakota', '38', '38000'],
        ['OH', 'Ohio', '39', '39000'],
        ['OK', 'Oklahoma', '40', '40000'],
        ['OR', 'Oregon', '41', '41000'],
        ['PA', 'Pennsylvania', '42', '42000'],
        ['RI', 'Rhode Island', '44', '44000'],
        ['SC', 'South Carolina', '45', '45000'],
        ['SD', 'South Dakota', '46', '46000'],
        ['TN', 'Tennessee', '47', '47000'],
        ['TX', 'Texas', '48', '48000'],
        ['UT', 'Utah', '49', '49000'],
        ['VT', 'Vermont', '50', '50000'],
        ['VA', 'Virginia', '51', '51000'],
        ['WA', 'Washington', '53', '53000'],
        ['WV', 'West Virginia', '54', '54000'],
        ['WI', 'Wisconsin', '55', '55000'],
        ['WY', 'Wyoming', '56', '56000'],
        ['AS', 'American Samoa', '60', '60000'],
        ['FM', 'Federatd States of Micronesia', '64', '64000'],
        ['GU', 'Guam', '66', '66000'],
        ['MH', 'Marshall Islands', '68', '68000'],
        ['MP', 'Commonwealth of the Northern Mariana Islands', '69', '69000'],
        ['PR', 'Puerto Rico', '72', '72000'],
        ['PW', 'Palau', '70', '70000'],
        ['VI', 'U.S. Virgin Islands', '78', '78000'],
        ['UM', 'U.S. Minor Outlying Islands', '74', '74000'],
    ],
    columns=['USPS', 'Province_State', 'stateFIPS', 'FIPS'])
"""Post code, state name, and FIPS code look-up table

   Postal codes for U.S. states, federal district, territories, insular areas,
   and freely associated states from Appendix B, Publication 28,
   Postal Addressing Standards: https://pe.usps.com/text/pub28/28apb.htm.
   Every cell is unique, so any column can serve as look-up table keys.
   'UM' is not listed in Pub 28 but is included here.
   See also
   https://www.census.gov/library/reference/code-lists/ansi.html#par_statelist_1.
   """


def _geo_json_files(states, counties):
  return {'states': f'{states}',
          'counties': f'{counties}'}


def read_geo_json(
    states=STATES_JSON,
    counties=COUNTIES_JSON) -> Dict:
  """Reads U.S. State and County `GeoJSON` files

  Args:
    states (str): States JSON URL
    counties (str): Counties JSON URL

  Returns:
    Dict[Dict[GeoJSON]]
    ::

    {'counties': GeoJSON, states': GeoJSON}
  """
  geo_json_files = _geo_json_files(states=states, counties=counties)
  geo_json = {}
  for i in ['states', 'counties']:
    with urllib.request.urlopen(geo_json_files[i]) as url:
      geo_json[i] = geojson.load(url)
  return geo_json


def read_geo_pandas(
    states=STATES_JSON,
    counties=COUNTIES_JSON) -> Dict:
  """Converts U.S. State and County `GeoJSON` files to `GeoPandas` objects

  Args:
    states (str): States JSON URL
    counties (str): Counties JSON URL

  Returns:
    Dict[Dict[gpd.GeoDataFrame]]
    ::

    {'counties': gpd.GeoDataFrame, states': gpd.GeoDataFrame}
  """
  geo_json_files = _geo_json_files(states=states, counties=counties)
  gdf = {}
  for i in ['states', 'counties']:
    gdf[i] = gpd.read_file(geo_json_files[i])
  return gdf
