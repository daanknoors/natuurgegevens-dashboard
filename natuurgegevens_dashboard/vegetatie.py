import pandas as pd
import geopandas as gpd
import janitor
from natuurgegevens_dashboard import configs
from natuurgegevens_dashboard import utils

def read_vegetatie_data(file_path):
    # geometry is invalid thus read file with ignore_geometry=True
    df_vegetatie = gpd.read_file(file_path, ignore_geometry=True) 
    return df_vegetatie

def preprocess_vegetatie_data(df_vegetatie):
    df = df_vegetatie.copy()

    # convert AX/AY to geometry
    gdf = gpd.GeoDataFrame(
        df_vegetatie,
        geometry=gpd.points_from_xy(df["AX"], df["AY"]),
        crs="EPSG:28992" 
    )
 
    # extract lon/lat from geometry
    df = utils.extract_lat_lon_from_geometry(gdf)


    # convert column names to snake_case
    df = df.clean_names()

    # load typologie
    df_typologie = pd.read_csv(configs.DIR_DATA_RAW / "flora_en_vegetatie/vegetatie_typologie.csv")
    df_typologie = df_typologie.rename(columns={'Code': 'limb1_lower', 'Beschrijving': 'naam_ned'})

    # strip last r of code column and lowercase
    df_typologie['limb1_lower'] = df_typologie['limb1_lower'].str.lower().str.rstrip('r')

    # merge with vegetatie data on lowercaed limb1 code after stripping 'r'
    df['limb1_lower'] = df['limb1'].str.lower().str.rstrip('r')
    df = df.merge(df_typologie, on='limb1_lower', how='left')

    # add kartering label
    df['kartering_jaren'] = df['jaar'].apply(utils.label_kartering)
    
    # rename column names
    df = df.rename(columns={
        'recordnum': 'id'
    })
    return df



if __name__ == "__main__":
    gdf_vegetatie_raw = read_vegetatie_data(configs.DIR_DATA_RAW / "flora_en_vegetatie/vegetatiekaart_vlakken_v20240224/vegetatiekaart_vlakken_v20240224.shp")
    df_vegetatie = preprocess_vegetatie_data(gdf_vegetatie_raw)
    utils.write_processed_data(df_vegetatie, save_path=configs.DIR_DATA_PROCESSED / "vegetatie.csv")
    utils.write_processed_data(df_vegetatie, sample=10000, save_path=configs.DIR_DATA_PROCESSED / "vegetatie_sample_10000.csv")


