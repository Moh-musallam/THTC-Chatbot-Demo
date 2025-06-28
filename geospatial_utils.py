# geospatial_utils.py
import os
import geopandas as gpd
import pandas as pd

# Dictionary mapping English road names (from LLM) to actual Arabic values in the data
ROAD_NAME_TRANSLATIONS = {
    "King Fahd Road": "طريق الملك فهد",
    "Prince Mohammed Ibn Salman Road": "طريق الأمير محمد بن سلمان",
    "Prince Mohammed Road": "طريق الأمير محمد بن سلمان",
    "Prince Mohammed salman Road": "طريق الأمير محمد بن سلمان",
    "King Abdul-Aziz Road": "طريق الملك عبدالعزيز",
    "King AbdulAziz Road": "طريق الملك عبدالعزيز",
    "Northern Ring Road": "طريق الدائري الشمالي",
    "ُEastern Ring Road": "طريق الدائري الشرقي",
    "ِAbu Baker Al-Siddiq Road": "طريق ابو بكر الصديق",
    
    "AirPort road": "طريق  المطار"
    
}


# Load all road GeoJSONs from nested folders like: data/new/Jan 2022/, Jan 2023/, etc.
def load_all_road_data(base_path="data/new/"):
    all_data = []
    
    for year_folder in os.listdir(base_path):
        full_path = os.path.join(base_path, year_folder)
        if os.path.isdir(full_path) and year_folder.startswith("Jan"):
            for file in os.listdir(full_path):
                if file.endswith(".geojson"):
                    try:
                        gdf = gpd.read_file(os.path.join(full_path, file))
                        gdf["month_year"] = year_folder
                        gdf["source_file"] = file
                        gdf = gdf[["segmentId", "newSegmentId", "speedLimit", "frc", "streetName", "distance", "geometry", "month_year", "source_file"]]
                        all_data.append(gdf)
                    except Exception as e:
                        print(f"⚠️ Error reading {file}: {e}")
    
    if all_data:
        return gpd.GeoDataFrame(pd.concat(all_data, ignore_index=True))
    return gpd.GeoDataFrame()

# Query logic for roads
def run_query_roads(roads, params):
    query_type = params.get("query_type")
    month_year = params.get("month_year")
    road_name = params.get("road_name")
    speed_limit = params.get("max_speed")
    min_distance = params.get("min_distance")

    if month_year:
        roads = roads[roads["month_year"] == month_year]

    if query_type == "show_all_roads":
        return roads, None, None
    
    elif query_type == "filter_by_road_name" and road_name:
    # Try to match in the source file name instead of the Arabic streetName
         filtered = roads[roads["source_file"]
             .fillna("")
             .str.lower()
             .str.contains(road_name.strip().lower(), na=False)
         ]
         return filtered, None, None





    elif query_type == "filter_by_speed" and speed_limit is not None:
        return roads[roads["speedLimit"] <= speed_limit], None, None

    elif query_type == "filter_by_distance" and min_distance is not None:
        return roads[roads["distance"] >= min_distance], None, None

    return gpd.GeoDataFrame(), None, None
