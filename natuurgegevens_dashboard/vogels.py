import pandas as pd
import geopandas as gpd
import janitor

from natuurgegevens_dashboard import configs
from natuurgegevens_dashboard import utils



def preprocess_vogels_data(df_vogels):
    df = df_vogels.copy()

    # select relevant columns
    df = df[['OID', 'NAAM', 'WETENS', 'AX', 'AY', 'JAAR', 'AANTAL', 'ROOFPIET', 'NPERHOK', 'HOKFREQ']]

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
    df.loc[:, 'kartering_jaren'] = df.loc[:, 'jaar'].apply(utils.label_kartering)

    # rename column names
    df = df.rename(columns={
        'oid': 'id',
        'naam': 'naam_ned',
        'wetens': 'naam_wet' 
    })

    # naam_ned and naam_wet combined in one column
    df.loc[:, 'naam_comb'] = df.apply(
        lambda row: f"{row['naam_ned']} / ({row['naam_wet']})", axis=1
    )

    # remove unwanted characters from naam_comb
    df.loc[:, 'naam_comb'] = df['naam_comb'].apply(utils.clean_string)

    # merge kwetsbare soorten info
    df = utils.merge_kwetsbare_soorten(df)
    return df

if __name__ == "__main__":
    print('Preprocessing vogels data...')
    df_vogels_raw = pd.read_excel(configs.DIR_DATA_RAW / "vogels" / "data_natuurgegevens_vogels.xlsx")
    df_vogels = preprocess_vogels_data(df_vogels_raw)
    utils.write_processed_data(df_vogels, save_path=configs.DIR_DATA_PROCESSED / "vogels.csv")
    utils.write_processed_data(df_vogels, sample=10000, save_path=configs.DIR_DATA_PROCESSED / "vogels_sample_10000.csv")

