from pathlib import Path
import geopandas
from importlib.resources import files

def get_netherlands_shapefile():
    """
    Read in the shapefile from resrources/netherlands_shapefile, and convert to RD New.
    Assumes the code being run is in modules/plotting
    """
    my_resources = files("pygridsio") / "resources" / "netherlands_shapefile"
    data = (my_resources / "2019_provinciegrenzen_kustlijn.shp")
    df = geopandas.read_file(data, engine="pyogrio")
    shapefile_df = df.to_crs(28992)
    return shapefile_df
