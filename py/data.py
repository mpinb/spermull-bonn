from isf_pandas_msgpack import read_msgpack
import os

wd = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(wd, "..", "data"))
DF_PATH = os.path.join(DATA_DIR, "geo_dates.msg")

def read_df():
    return read_msgpack(DF_PATH)

def get_lat_lon_from_date(
    date: str
    ):
    """Get geolocation from a datetime"""
    return read_df().xs(date, level='date')[['LAT', 'LON']].values