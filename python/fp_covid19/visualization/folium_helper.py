# -*- coding: utf-8 -*-
"""Helper Library for Folium"""
from time import strptime, mktime
import numpy as np
import folium
from branca.colormap import linear
from fp_covid19.data.bears import Bears

def folium_del_legend(choropleth: folium.Choropleth):
  """A hack to remove a choropleth legend

  The choropleth color-scaled legend sometimes is too crowded. Until there is an
  option to disable the legend, use this routine to remove any color map children
  from the choropleth.

  Args:
    choropleth: Choropleth objected created by `folium.Choropleth()`

  Returns:
    The same object `choropleth` with any child whose name starts with
    'color_map' removed.
  """
  del_list = []
  for child in choropleth._children: # pylint: disable=protected-access
    if child.startswith('color_map'):
      del_list.append(child)
  for del_item in del_list:
    choropleth._children.pop(del_item) # pylint: disable=protected-access
  return choropleth

# "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
# {"attribution": "Data by \u0026copy; \u003ca href=\"http://openstreetmap.org\"\u003eOpenStreetMap\u003c/a\u003e, under \u003ca href=\"http://www.openstreetmap.org/copyright\"\u003eODbL\u003c/a\u003e.", "detectRetina": false, "maxNativeZoom": 18, "maxZoom": 18, "minZoom": 0, "noWrap": false, "opacity": 1, "subdomains": "abc", "tms": false}

def folium_add_map_title(title: str, folium_map: folium.Map):
  """Adds a map title"""
  html = '''
     <div style=”position: fixed;
     bottom: 50px; left: 50px; width: 100px; height: 90px;
     border:2px solid grey; z-index:9999; font-size:10pt;
     “>{}</div>'''.format(title)
  folium_map.get_root().html.add_child(folium.Element(html))


def to_datetime(date_str, date_format="%m/%d/%y"):
  """Converts string to datetime to POSIX time"""
  timestamp = strptime(date_str, date_format)
  epoch = mktime(timestamp)
  return int(epoch)


def cmap_ranked_df(
    bears: Bears, cmap=linear.OrRd_09.scale(0, 1)): # pylint: disable=no-member
  """Computes color map for ranked data"""
  cmap_bears = bears.copy()
  # Normalize data daily
  col_min, col_max = (
      cmap_bears.df[cmap_bears.datetime_index].min(),
      cmap_bears.df[cmap_bears.datetime_index].max())
  cmap_bears.df.loc[:, cmap_bears.datetime_index] = (
      (cmap_bears.df[cmap_bears.datetime_index] - col_min)/(col_max - col_min))
  cmap_bears.df.loc[:, cmap_bears.datetime_index] = cmap_bears.df[
      cmap_bears.datetime_index].rank(method='min', pct=True, na_option='top')
  cmap_bears.df.loc[:, cmap_bears.datetime_index] = cmap_bears.df[
      cmap_bears.datetime_index].apply(np.vectorize(cmap))
  return cmap_bears
