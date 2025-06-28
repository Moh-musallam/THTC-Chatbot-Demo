# geospatial_utils.py
import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Optional: English to Arabic road name mapping (still useful)
ROAD_NAME_TRANSLATIONS = {
    "King Fahd Road": "طريق الملك فهد",
    "Prince Mohammed Ibn Salman Road": "طريق الأمير محمد بن سلمان",
    "King Abdul-Aziz Road": "طريق الملك عبدالعزيز",
    "Northern Ring Road": "طريق الدائري الشمالي",
    "Eastern Ring Road": "طريق الدائري الشرقي",
    "Abu Baker Road": "طريق ابو بكر الصديق",
    "Airport Road": "طريق المطار"
}

# Optional: Known landmark coordinates for "query by location"
KNOWN_LOCATIONS = {
    "King Fahd Hospital": (50.2001, 26.3023),
    "King Saud University": (46.7161, 24.7247),
    "Riyadh Airport": (46.6985, 24.9570)
}

# Load all .geojson files from Jan-year folders
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
                        all_data.append(gdf)
                    except Exception as e:
                        print(f"⚠️ Error reading {file}: {e}")
    return gpd.GeoDataFrame(pd.concat(all_data, ignore_index=True)) if all_data else gpd.GeoDataFrame()

# Main query execution
def run_query_roads(roads, params, previous_context=None):
    query_type = params.get("query_type")
    month_year = params.get("month_year")
    road_name = params.get("road_name")
    speed_limit = params.get("max_speed")
    min_distance = params.get("min_distance")
    top_n = params.get("top_n", 5)
    location_name = params.get("location_name")
    radius_km = params.get("radius_km", 5)
    compare_year = params.get("compare_year")

    # Filter by month
    if month_year:
        roads = roads[roads["month_year"] == month_year]

    # ========== QUERY TYPES ========== #

    if query_type == "show_all_roads":
        return roads, None, None

    elif query_type == "filter_by_road_name" and road_name:
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

    elif query_type == "summary_stats":
        stats = {
            "average_speed": round(roads["speedLimit"].mean(), 2),
            "max_speed": roads["speedLimit"].max(),
            "min_speed": roads["speedLimit"].min(),
            "avg_distance": round(roads["distance"].mean(), 2),
            "total_segments": len(roads)
        }
        return roads.iloc[0:0], None, stats

    elif query_type == "detect_anomalies":
        anomalies = roads[
            (roads["speedLimit"] > 150) | (roads["distance"] > 1000)
        ]
        return anomalies, None, None

    elif query_type == "top_n":
        sort_field = params.get("sort_by", "distance")
        sorted_roads = roads.sort_values(by=sort_field, ascending=False).head(top_n)
        return sorted_roads, None, None

    elif query_type == "near_location" and location_name:
        lon, lat = KNOWN_LOCATIONS.get(location_name, (None, None))
        if lat is None or lon is None:
            return gpd.GeoDataFrame(), None, None

        point = Point(lon, lat)
        search_gdf = gpd.GeoDataFrame(geometry=[point], crs="EPSG:4326")
        buffer = search_gdf.to_crs(epsg=3857).buffer(radius_km * 1000).to_crs(epsg=4326).iloc[0]

        nearby = roads[roads.geometry.within(buffer)]
        return nearby, buffer, point

    elif query_type == "compare_years" and compare_year and month_year:
        # Load base and compare datasets
        base = roads[roads["month_year"] == month_year]
        other = roads[roads["month_year"] == compare_year]

        merged = pd.merge(
            base,
            other,
            on="segmentId",
            suffixes=(f"_{month_year}", f"_{compare_year}")
        )
        return merged, None, None

    elif query_type == "trend_analysis" and road_name:
        road_filter = roads[roads["source_file"].str.contains(road_name, case=False, na=False)]
        summary = road_filter.groupby("month_year").agg({
            "speedLimit": "mean",
            "distance": "mean"
        }).reset_index()
        return road_filter.iloc[0:0], summary, None

    # ========== FALLBACK ========== #

    return gpd.GeoDataFrame(), None, None
