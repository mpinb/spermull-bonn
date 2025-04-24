import pandas as pd
import get_census_data
from tqdm.auto import tqdm
tqdm.pandas()

def get_cols(res, cols):
    dict_ = {}
    for col in cols:
        dict_[col] = res['results'][0]['attributes'][col]
    return dict_


def parse_row(row):
   lat = row['LAT']
   long = row['LON']
   try:
      res = get_census_data.get_census_data(lat, long)
      results =  get_cols(res, ['Einwohner', 'durchschnMieteQM', 'durchschnFlaechejeWohn'])
      results.update({'LAT': lat, 'LON': long})
   except Exception as e:
      print(e)
      results = {'LAT': lat, 'LON': long, 'Einwohner': None, 'durchschnMieteQM': None, 'durchschnFlaechejeWohn': None}
   return results

if __name__ == '__main__':
   
   dicts = []

   addr = pd.read_csv('geocoded_addr.csv')
   parsed_df = addr.progress_apply(lambda row: parse_row(row), axis=1, result_type='expand')
   addr = pd.concat([addr, parsed_df], axis=1)
   addr.to_csv('geocoded_addr_zensus2022.csv', index=False)