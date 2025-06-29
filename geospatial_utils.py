# geospatial_utils.py
import os
import re
import geopandas as gpd
import pandas as pd

def load_all_road_data(base_path="data/new/"):
    """
    Load all GeoJSONs from data/new/Jan YYYY folders into one GeoDataFrame,
    tagging each record with month_year and source_file.
    """
    all_data = []
    for year_folder in os.listdir(base_path):
        year_path = os.path.join(base_path, year_folder)
        if os.path.isdir(year_path) and year_folder.startswith("Jan"):
            for fname in os.listdir(year_path):
                if fname.endswith(".geojson"):
                    try:
                        gdf = gpd.read_file(os.path.join(year_path, fname))
                        gdf["month_year"]  = year_folder
                        gdf["source_file"] = fname
                        all_data.append(gdf)
                    except Exception as e:
                        print(f"⚠️ Error reading {fname}: {e}")
    return gpd.GeoDataFrame(pd.concat(all_data, ignore_index=True)) if all_data else gpd.GeoDataFrame()

def run_query_roads(roads, params, previous_context=None):
    """
    Execute structured queries on the combined roads GeoDataFrame.
    Returns: (result_df, chart_df_or_None, summary_dict_or_None)
    """
    qt        = params.get("query_type")
    year1_raw = params.get("month_year", "")
    year2_raw = params.get("compare_year", "")
    road_name = params.get("road_name", "").strip().lower()
    max_spd   = params.get("max_speed")
    min_dist  = params.get("min_distance")
    top_n     = params.get("top_n", 5)

    # Keep full copy for cross-year logic
    full_df = roads.copy()

    # Normalize year1 filter: exact month or full-year
    if year1_raw:
        # If it contains a month (e.g. "Jan"), match exact
        if "Jan" in year1_raw:
            roads = full_df[full_df["month_year"] == year1_raw]
        else:
            # Extract 4-digit year and match any month ending
            m = re.search(r"(20\d{2})", year1_raw)
            if m:
                yr = m.group(1)
                roads = full_df[full_df["month_year"].str.endswith(yr)]
            else:
                # If cannot parse, default to full dataset
                roads = full_df

    # === 1. show_all_roads ===
    if qt == "show_all_roads":
        return roads, None, None

    # === 2. filter_by_road_name ===
    if qt == "filter_by_road_name" and road_name:
        df = roads
        filtered = df[df["source_file"]
            .str.lower()
            .str.contains(road_name, na=False)
        ]
        return filtered, None, None

    # === 3. filter_by_speed ===
    if qt == "filter_by_speed" and max_spd is not None:
        return roads[roads["speedLimit"] <= max_spd], None, None

    # === 4. filter_by_distance ===
    if qt == "filter_by_distance" and min_dist is not None:
        return roads[roads["distance"] >= min_dist], None, None

    # === 5. summary_stats ===
    if qt == "summary_stats":
        stats = {
            "average_speed":    round(roads["speedLimit"].mean(), 2),
            "max_speed":        roads["speedLimit"].max(),
            "min_speed":        roads["speedLimit"].min(),
            "average_distance": round(roads["distance"].mean(), 2),
            "total_segments":   len(roads)
        }
        return roads.iloc[0:0], None, stats

    # === 6. detect_anomalies ===
    if qt == "detect_anomalies":
        anomalies = roads[
            (roads["speedLimit"] > 150) |
            (roads["distance"] > 1000)
        ]
        return anomalies, None, None

    # === 7. top_n ===
    if qt == "top_n":
        sort_field = params.get("sort_by", "distance")
        top_df = roads.sort_values(by=sort_field, ascending=False).head(top_n)
        return top_df, None, None

    # === 8. compare_years ===
    if qt == "compare_years" and year1_raw and year2_raw:
        # Filter full_df by name if needed
        df = full_df
        if road_name:
            df = df[df["source_file"]
                .str.lower()
                .str.contains(road_name, na=False)
            ]
        # Build year1 & year2 subsets using same normalization
        def subset_by(raw):
            if "Jan" in raw:
                return df[df["month_year"] == raw]
            m2 = re.search(r"(20\d{2})", raw)
            if m2:
                yr2 = m2.group(1)
                return df[df["month_year"].str.endswith(yr2)]
            return df

        df1 = subset_by(year1_raw)
        df2 = subset_by(year2_raw)

        # 8a) Try segment-level merge
        merged = pd.merge(df1, df2, on="segmentId",
            suffixes=(f"_{year1_raw}", f"_{year2_raw}")
        )
        if not merged.empty:
            # add diff columns
            merged["speed_diff"]    = merged[f"speedLimit_{year2_raw}"] - merged[f"speedLimit_{year1_raw}"]
            merged["distance_diff"] = merged[f"distance_{year2_raw}"]   - merged[f"distance_{year1_raw}"]
            cols = [
                "segmentId",
                f"speedLimit_{year1_raw}", f"speedLimit_{year2_raw}", "speed_diff",
                f"distance_{year1_raw}",   f"distance_{year2_raw}",   "distance_diff"
            ]
            return merged[cols], None, None

        # 8b) Fallback two-row summary
        def summarize(df_sub, label):
            return {
                f"avg_speed_{label}":    round(df_sub["speedLimit"].mean(), 2),
                f"avg_distance_{label}": round(df_sub["distance"].mean(), 2),
                f"count_{label}":        len(df_sub)
            }

        s1 = summarize(df1, year1_raw)
        s2 = summarize(df2, year2_raw)
        cmp_df = pd.DataFrame([s1, s2], index=[year1_raw, year2_raw])\
                   .reset_index()\
                   .rename(columns={"index":"year"})
        return cmp_df, None, None

    # === 9. trend_analysis ===
    if qt == "trend_analysis" and road_name:
        trend_df = full_df[ full_df["source_file"]
            .str.lower()
            .str.contains(road_name, na=False)
        ]
        trend = trend_df.groupby("month_year").agg({
            "speedLimit": "mean",
            "distance":   "mean"
        }).reset_index()
        return trend_df.iloc[0:0], trend, None

    # === Fallback ===
    return gpd.GeoDataFrame(), None, None
