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
    

def merge_kwetsbare_soorten(df, verbose=True):
    df_kwetsbare_soorten = pd.read_excel(configs.DIR_DATA_RAW / "kwetsbare_soorten_v1_1_1 (1).xlsx")

    # merge kwetsbare soorten info on naam_wet OR naam_ned
    df_kwetsbare_soorten = df_kwetsbare_soorten.rename(columns={
        'wetenschappelijke_naam': 'naam_wet',
        'nederlandse_naam': 'naam_ned',
        'reden': 'kwetsbare_soort_reden',
        'onderbouwing': 'kwetsbare_soort_onderbouwing'
    })
    
    # First merge on scientific name (naam_wet) case_insensitive
    df = df.merge(
        df_kwetsbare_soorten[['naam_wet', 'kwetsbare_soort_reden', 'kwetsbare_soort_onderbouwing']],
        on='naam_wet',
        how='left',
        suffixes=('', '_wet')
    )
    
    # Second merge on Dutch name (naam_ned) for records that didn't match in first merge
    df_temp = df_kwetsbare_soorten[['naam_ned', 'kwetsbare_soort_reden', 'kwetsbare_soort_onderbouwing']].rename(
        columns={
            'kwetsbare_soort_reden': 'kwetsbare_soort_reden_ned',
            'kwetsbare_soort_onderbouwing': 'kwetsbare_soort_onderbouwing_ned'
        }
    )
    df = df.merge(df_temp, on='naam_ned', how='left')

    if verbose:

        # print how many records matched on scientific name vs Dutch name
        matched_wet = df['kwetsbare_soort_reden'].notna().sum()
        matched_ned = df['kwetsbare_soort_reden_ned'].notna().sum()
        print(f"Matched {matched_wet} records on scientific name and {matched_ned} records on Dutch name.")

        # print number of matched species vs total number of species in original df
        total_species = df[['naam_wet', 'naam_ned']].drop_duplicates().shape[0]
        total_matched = df[(df['kwetsbare_soort_reden'].notna()) | (df['kwetsbare_soort_reden_ned'].notna())][['naam_wet', 'naam_ned']].drop_duplicates().shape[0]
        print(f"Total number of species in dataset: {total_species}, total number of matched protected species: {total_matched}")
        
        # print which records matched on one but not the other
        only_wet = df[(df['kwetsbare_soort_reden'].notna()) & (df['kwetsbare_soort_reden_ned'].isna())].drop_duplicates(subset=['naam_wet'])
        only_ned = df[(df['kwetsbare_soort_reden'].isna()) & (df['kwetsbare_soort_reden_ned'].notna())].drop_duplicates(subset=['naam_ned'])
        print (f"Total number of species matched only on scientific name: {len(only_wet)}")
        print(f"Total number of species matched only on Dutch name: {len(only_ned)}")
    
    # Combine results: use values from scientific name match, fall back to Dutch name match
    df['kwetsbare_soort_reden'] = df['kwetsbare_soort_reden'].fillna(df['kwetsbare_soort_reden_ned'])
    df['kwetsbare_soort_onderbouwing'] = df['kwetsbare_soort_onderbouwing'].fillna(df['kwetsbare_soort_onderbouwing_ned'])
    
    # Drop temporary columns
    df = df.drop(columns=['kwetsbare_soort_reden_ned', 'kwetsbare_soort_onderbouwing_ned'])
    

    # flag kwetsbare soort for reden or roofpiet or embargo. Check if data has these columns
    mask = df['kwetsbare_soort_reden'].notna()
    if 'embargo' in df.columns:
        mask = mask | df['embargo']
    if 'roofpiet' in df.columns:
        mask = mask | df['roofpiet']
    df['kwetsbare_soort'] = mask
    return df