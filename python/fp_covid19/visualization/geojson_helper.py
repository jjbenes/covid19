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

US_BALTIMORE_METRO_FIPS = [
    '24003', '24005', '24013', '24025', '24027', '24035', '24510']
"""U.S. Baltimore Metropolitan Area: [
   'Anne Arundel County, MD', 'Baltimore County, MD', 'Baltimore City, MD',
   'Carroll County, MD', 'Harford County, MD', 'Howard County, MD',
   "Queen Anne's County, MD"]
"""

US_CHARLOTTE_METRO_FIPS = [
    '37025', '37045', '37071', '37097', '37109', '37119', '37159', '37167',
    '37179', '45023', '45057', '45091']
"""U.S. Charlotte Metropolitan Area: [
   'Mecklenburg County, NC', 'York County, SC', 'Union County, NC',
   'Gaston County, NC', 'Cabarrus County, NC', 'Iredell County, NC',
   'Rowan County, NC', 'Lancaster County, SC', 'Cleveland County, NC',
   'Lincoln County, NC', 'Stanly County, NC', 'Chester County, SC']
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

US_DENVER_METRO_FIPS = [
    '8001', '8005', '8013', '8014', '8019', '8031', '8035', '8039', '8047',
    '8059', '8093', '8123']
"""U.S. Denver-Aurora: [
   'Denver County, CO', 'Arapahoe County, CO', 'Jefferson County, CO',
   'Adams County, CO', 'Douglas County, CO', 'Broomfield County and City, CO',
   'Elbert County, CO', 'Park County, CO', 'Clear Creek County, CO',
   'Gilpin County, CO', 'Boulder County, CO', 'Weld County, CO']
"""

US_DETROIT_METRO_FIPS = ['26087', '26093', '26099', '26125', '26147', '26163']
"""U.S. Detroit Metropolitan Area:
   ['Lapeer County, MI', 'Livingston County, MI', 'Macomb County, MI',
    'Oakland County, MI', 'St. Clair County, MI', 'Wayne County, MI']
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

US_INLAND_EMPIRE_FIPS = ['6065', '6071']
"""U.S. Inland Empire: ['Riverside County, CA', 'San Bernardino County, CA']
"""

US_MIAMI_METRO_FIPS = ['12011', '12086', '12099']
"""U.S. Miami Metropolitan Area: [
   'Miami-Dade County, FL', 'Broward County, FL', 'Palm Beach County, FL']
"""

US_PHOENIX_METRO_FIPS = ['4007', '4013', '4021']
"""U.S. Phoenix Metropolitan Area: [
    'Maricopa County, AZ', 'Pinal County, AZ', 'Gila County, AZ']
"""

US_GREATER_PORTLAND_FIPS = [
    '41005', '41009', '41051', '41067', '41071', '53059']
"""U.S. Portland-Vancouver-Hillsboro: Clackamas, Columbia, Multnomah,
   Washington, Yamhill, and Clark counties in Oregon; and Skamania County in
   Washington."""

US_GREATER_ST_LOUIS_FIPS = [
    '17005', '17013', '17027', '17083', '17117', '17119', '17133', '17163',
    '29071', '29099', '29113', '29183', '29189', '29219', '29510']
"""U.S. Greater St. Louis: [
   'Bond County, IL', 'Calhoun County, IL', 'Clinton County, IL',
   'Jersey County, IL', 'Macoupin County, IL', 'Madison County, IL',
   'Monroe County, IL', 'St. Clair County, IL', 'Franklin County, MO',
   'Jefferson County, MO', 'Lincoln County, MO', 'St. Charles County, MO',
   'City of St. Louis, MO', 'St. Louis County, MO', 'Warren County, MO']
"""

US_MINNEAPOLIS_SAINT_PAUL_FIPS = [
    '27003', '27019', '27025', '27037', '27053', '27059', '27079', '27095',
    '27123', '27139', '27141', '27143', '27163', '27171', '55093', '55109']
"""U.S. Minneapolis-Saint Paul: [
  'Hennepin County, MN', 'Ramsey County, MN', 'Dakota County, MN',
  'Anoka County, MN', 'Washington County, MN', 'Scott County, MN',
  'Wright County, MN', 'Carver County, MN', 'Sherburne County, MN',
  'St. Croix County, WI', 'Chisago County, MN', 'Pierce County, WI',
  'Isanti County, MN', 'Le Sueur County, MN', 'Mille Lacs County, MN',
  'Sibley County, MN']
"""

US_SAN_DIEGO_FIPS = ['6075']
"""U.S. San Diego County"""

US_SEATTLE_METRO_FIPS = ['53033', '53053', '53061']
"""U.S. Seattle Metropolitan Area: [
   ''King County, WA', 'Pierce County, WA', 'Snohomish County, WA']
"""

US_SF_BAY_AREA_FIPS = ['6001', '6013', '6041', '6055', '6075',
                       '6081', '6085', '6095', '6097']
"""U.S. San Francisco Bay Area: Alameda, Contra Costa, Marin, Napa,
   San Francisco, San Mateo, Santa Clara, Solano, and Sonoma"""

US_TAMPA_BAY_AREA_FIPS = ['12053', '12057', '12101', '12103']
"""U.S. Tampa Bay Area: [
   'Hillsborough County, FL', 'Pinellas County, FL', 'Hernado County, FL',
   'Pasco County, FL']
"""

US_NYC_FIPS = ['36005', '36047', '36061', '36081', '36085']
"""U.S. New York City FIPS: Bronx, Kings (Brooklyn), New York (Manhattan),
   Queens, and Richmond (Staten Island)"""

US_METROS = {
    'Atlanta Metropolitan Area, GA': US_ATLANTA_METRO_FIPS,
    'Baltimore Metropolitan Area, MD': US_BALTIMORE_METRO_FIPS,
    'Charlotte Metropolitan Area, NC, SC': US_CHARLOTTE_METRO_FIPS,
    'Chicago Metropolitan Area, IL, IN, WI': US_CHICAGO_METRO_FIPS,
    'Dallas-Fort Worth Metroplex, TX': US_DALLAS_FORT_WORTH_METRO_FIPS,
    'Denvor-Aurora, CO': US_DENVER_METRO_FIPS,
    'Detroit Metropolitan Area, MI': US_DETROIT_METRO_FIPS,
    'Greater Boston, MA, NH': US_GREATER_BOSTON_FIPS,
    'Greater Houston, TX': US_GREATER_HOUSTON_FIPS,
    'Greater Los Angeles, CA': US_GREATER_LA_FIPS,
    'Greater Philadelphia, DE, NJ, PA': US_GREATER_PHILADELPHIA_FIPS,
    'Greater Portland, OR, WA': US_GREATER_PORTLAND_FIPS,
    'Greater St. Louis, IL, MO': US_GREATER_ST_LOUIS_FIPS,
    'Inland Empire, CA': US_INLAND_EMPIRE_FIPS,
    'Miami Metropolitan Area, FL': US_MIAMI_METRO_FIPS,
    'Minneapolis-Saint Paul, MN': US_MINNEAPOLIS_SAINT_PAUL_FIPS,
    'Phoenix Metropolian Area, AZ': US_PHOENIX_METRO_FIPS,
    'New York City, NY': US_NYC_FIPS,
    'Tampa Bay Area, FL':US_TAMPA_BAY_AREA_FIPS,
    'San Diego, CA': US_SAN_DIEGO_FIPS,
    'San Francisco Bay Area, CA': US_SF_BAY_AREA_FIPS,
    'Seattle Metropolitan Area, WA': US_SEATTLE_METRO_FIPS,
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
