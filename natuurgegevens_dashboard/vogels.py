import pandas as pd
import geopandas as gpd
import janitor

from natuurgegevens_dashboard import configs
from natuurgegevens_dashboard import utils


def read_vogels_data(file_path):
    df_vogels = pd.read_excel(file_path)
    return df_vogels

def preprocess_vogels_data(df_vogels):
    df = df_vogels.copy()

    # drop columns
    df = df.drop(columns=['LAT', 'LON', 'COUNT', 'NCOUNT'])

    # convert AX/AY to geometry
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["AX"], df["AY"]),
        crs="EPSG:28992" 
    )

    # extract lon/lat from geometry
    df = utils.extract_lat_lon_from_geometry(gdf)

    # convert column names to snake_case
    df = df.clean_names()

    # add kartering label
    df['kartering_jaren'] = df['jaar'].apply(utils.label_kartering)

    # rename column names
    df = df.rename(columns={
        'oid': 'id',
        'naam': 'naam_ned',
        'wetens': 'naam_wed' 
    })
    return df

if __name__ == "__main__":
    df_vogels_raw = read_vogels_data(configs.DIR_DATA_RAW / "vogels" / "data_natuurgegevens_vogels.xlsx")
    df_vogels = preprocess_vogels_data(df_vogels_raw)
    utils.write_processed_data(df_vogels, save_path=configs.DIR_DATA_PROCESSED / "vogels.csv")
    utils.write_processed_data(df_vogels, sample=10000, save_path=configs.DIR_DATA_PROCESSED / "vogels_sample_10000.csv")