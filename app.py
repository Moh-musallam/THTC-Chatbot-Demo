# app.py
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from geospatial_utils import run_query_roads, load_all_road_data
from llm_agent import query_to_action

st.set_page_config(layout="wide")
st.title("🚦 THTC Demo – AI Chatbot For Road Data (2022–2025)")

# Load all roads once
roads = load_all_road_data("data/new/")

# Initialize memory for follow-up questions
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = {}

# User input
with st.form("question_form"):
    question = st.text_input(
        "Ask something about Saudi roads between Jan 2022 and Jan 2025:",
        placeholder="Enter your question here..."
    )
    submitted = st.form_submit_button("Submit")

if submitted:
    # Send user question and memory to LLM
    parsed = query_to_action(question, memory=st.session_state.chat_memory)

    # Show parsed JSON (for debugging)
    st.subheader("Parsed Query")
    st.code(parsed, language="json")

    # Update memory (only if parsed is valid)
    if parsed:
        st.session_state.chat_memory = parsed

    if parsed is None:
        st.error("❌ Could not understand the question.")
    else:
        result, meta_data, stats_or_point = run_query_roads(roads, parsed, previous_context=st.session_state.chat_memory)
        query_type = parsed.get("query_type")

        # === Trend Plot ===
        if query_type == "trend_analysis" and isinstance(meta_data, pd.DataFrame):
            st.subheader("📈 Yearly Trend")
            st.line_chart(meta_data.set_index("month_year")[["speedLimit", "distance"]])

        # === Summary Stats ===
        elif query_type == "summary_stats" and isinstance(stats_or_point, dict):
            st.subheader("📊 Summary Statistics")
            st.json(stats_or_point)
            st.markdown(f"""🧠 **Summary**:
- Average speed: **{stats_or_point['average_speed']} km/h**
- Average distance: **{stats_or_point['avg_distance']} km**
- Segment count: **{stats_or_point['total_segments']}**
""")

        # === Compare Years ===
        elif query_type == "compare_years" and not result.empty:
            st.subheader("📊 Year-to-Year Comparison")
            st.dataframe(result)

        # === Regular map results ===
        elif not result.empty:
            st.success(f"✅ Found {len(result)} road segments.")

            # Show table
            st.dataframe(result.drop(columns=["geometry"]))

            # Show map
            fig, ax = plt.subplots(figsize=(10, 6))
            result.plot(ax=ax, column="speedLimit", cmap="viridis", legend=True)

            if meta_data is not None:
                # Draw search buffer if nearby query
                gpd.GeoSeries([meta_data]).boundary.plot(ax=ax, color="red", linestyle="--", label="Search Area")

            if stats_or_point is not None and hasattr(stats_or_point, 'geom_type'):
                gpd.GeoSeries([stats_or_point]).plot(ax=ax, color="red", markersize=50, label="Center")

            ax.set_title("Map of Results")
            ax.axis("off")
            st.pyplot(fig)

        else:
            st.warning("⚠️ No results found.")
