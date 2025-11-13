import pandas as pd
import geopandas as gpd
import janitor
from natuurgegevens_dashboard import configs

def extract_lat_lon_from_geometry(gdf):
    # set the known CRS and convert to WGS84
    gdf = gdf.set_crs(epsg=28992, allow_override=True)   
    gdf = gdf.to_crs(epsg=4326)
    
    # extract lon/lat from geometry
    gdf['lon'] = gdf.geometry.x
    gdf['lat'] = gdf.geometry.y

    # drop geometry column and return as DataFrame
    df = pd.DataFrame(gdf.drop(columns='geometry'))
    return df



def write_processed_data(df, sample=None, save_path=None):
    if sample:
        df = df.sample(n=sample)

    df.to_csv(save_path, index=False)
    print(f"Data written to {save_path}")


def label_kartering(jaar):
    if 1990 <=int(jaar) <= 1997:
        return 'Kartering 1990-1997'
    elif 1998 <=int(jaar) <= 2011:
        return 'Kartering 1998-2011'
    elif 2012 <=int(jaar) <= 2023:
        return 'Kartering 2012-2023'
    else:
        return 'Overige jaren'