from pyproj import Transformer
import json
import urllib
import requests


def get_census_data(lat, lon):
    # Transform coordinates from WGS84 to ETRS89-LAEA (EPSG:3035)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)
    x, y = transformer.transform(lon, lat)

    # Create bounding box string (this must be URL-encoded)
    box_string = f"{x - 500},{y - 500},{x + 500},{y + 500}"

    # Define parameters
    params = {
        "f": "json",
        "returnFieldName": "true",
        "returnGeometry": "false",
        "returnUnformattedValues": "true",
        "returnZ": "false",
        "tolerance": "0",
        "imageDisplay": "1140,258,96",
        "geometry": json.dumps({"x": x, "y": y}),  # Just dump as JSON, let urlencode handle encoding
        "geometryType": "esriGeometryPoint",
        "sr": "3035",
        "mapExtent": box_string,
        "layers": "visible:19"
    }

    # Construct full URL
    base_url = "https://www.gis-idmz.nrw.de/arcgis/rest/services/stba/zensusatlas_2022/MapServer/identify"
    full_url = f"{base_url}?{urllib.parse.urlencode(params)}"

    # Fetch data
    response = requests.get(full_url)
    return response.json()

if __name__ == '__main__':
    lat = 50.750892882352936
    lon = 7.0888296764705885
    json_data = get_census_data(lat, lon)
    import pprint
    pprint.pprint(json_data)