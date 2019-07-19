import pandas as pd
import bs4
import requests
from geojson import Point, Feature, FeatureCollection, dump



request = requests.get('https://www.drv.gov.ua/ords/portal/!cm_core.cm_index?option=ext_dvk&prejim=3')

soup = bs4.BeautifulSoup(request.content, 'lxml')

numbers = [a['href'].split('&')[1].split('=')[1] for a in soup.select('table a')]

polygons = [];
for number in numbers:
    i = requests.get(f"https://www.drv.gov.ua/ords/portal/gis$core.Gis_Okrug_Poly?p_id100={number}&ts=0.235428758430836")
    polygons.append(i.json())
    

feat = []
for d in polygons:
    feat += d['features']


total_json = {'type': 'FeatureCollection',
 'features':feat,
     'id': '1',
   'distr': '000001',
   'geomtype': '15'}


with open('all_tvo.geojson', 'w') as f:
    dump(total_json, f, ensure_ascii=False)