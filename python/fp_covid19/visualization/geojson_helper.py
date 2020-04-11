# -*- coding: utf-8 -*-
"""Helper Library for GeoJSON"""
from typing import Dict
import urllib
import geojson

def us_geo_json(
    url_root='https://raw.githubusercontent.com/jjbenes/covid19/master/json',
    states='us-states.json',
    counties='us-counties.json') -> Dict:
  """Reads U.S. State and County GeoJSON files

  Args:
    url_root (str): URL root
    states (str): Appened to `url_root` to form the path to the states file
    counties (str): Appended to `url_root` to form the path to the counties file

  Returns:
    Dict[Dict[GeoJSON]]
    ::

    {'counties': GeoJSON, states': GeoJSON}
  """
  geo_json_files = {
      'states': {'US': f'{url_root}/{states}'},
      'counties': {'US': f'{url_root}/{counties}'}}
  geo_json = {'states': {'US': None}, 'counties': {'US': None}}
  for i in ['states', 'counties']:
    with urllib.request.urlopen(geo_json_files[i]['US']) as url:
      geo_json[i]['US'] = geojson.load(url)
  return geo_json
