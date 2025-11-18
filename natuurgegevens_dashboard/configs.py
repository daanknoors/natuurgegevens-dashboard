from pathlib import Path

DIR_DATA = Path("~/data/natuurgegevens-dashboard").expanduser()
DIR_DATA_RAW = DIR_DATA / "raw"
DIR_DATA_PROCESSED = DIR_DATA / "processed"

DIR_DATA_PROCESSED_FLORA = DIR_DATA_PROCESSED / "flora.csv"
DIR_DATA_PROCESSED_VOGELS = DIR_DATA_PROCESSED / "vogels.csv"
DIR_DATA_PROCESSED_VEGETATIE = DIR_DATA_PROCESSED / "vegetatie.csv"
