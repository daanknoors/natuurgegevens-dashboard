import geopandas as gpd
import janitor
from natuurgegevens_dashboard import configs
from natuurgegevens_dashboard import utils


def read_flora_data(file_path):
    gdf_flora = gpd.read_file(file_path)
    return gdf_flora


def preprocess_flora_data(gdf_flora):
    gdf = gdf_flora.copy()

    # extract lon/lat from geometry
    df = utils.extract_lat_lon_from_geometry(gdf)

    # convert column names to snake_case
    df = df.clean_names()

    # match kwetsbare soorten info
    df = utils.merge_kwetsbare_soorten(df)

    # add kartering label
    df['kartering_jaren'] = df['jaar'].apply(utils.label_kartering)

    # rename column names
    df = df.rename(columns={
        'plant_id': 'id'
    })
    return df


if __name__ == "__main__":
    gdf_flora_raw = read_flora_data(configs.DIR_DATA_RAW / "flora_en_vegetatie/florakaart_2025_02_12" / "florakaart_2025_02_12.shp")
    df_flora = preprocess_flora_data(gdf_flora_raw)
    utils.write_processed_data(df_flora, save_path=configs.DIR_DATA_PROCESSED / "flora.csv")
    utils.write_processed_data(df_flora, sample=10000, save_path=configs.DIR_DATA_PROCESSED / "flora_sample_10000.csv")

