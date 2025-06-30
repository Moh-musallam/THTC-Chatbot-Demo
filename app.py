# app.py
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from geospatial_utils import run_query_roads, load_all_road_data
from llm_agent import query_to_action

st.set_page_config(layout="wide")
st.title("🚦 THTC Demo – AI Chatbot For Road Data (2022–2025)")

# ─── Load all roads once ──────────────────────────────────────────────────────
roads = load_all_road_data("data/new/")



# ─── Initialize memory for follow-up queries ─────────────────────────────────
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = {}

# ─── User input form ──────────────────────────────────────────────────────────
with st.form("question_form"):
    question = st.text_input(
        "Ask something about Saudi roads between Jan 2022 and Jan 2025:",
        placeholder="Enter your question here..."
    )
    submitted = st.form_submit_button("Submit")

# ─── Handle submission ────────────────────────────────────────────────────────
if submitted:
    # 1. Parse question via LLM (with memory for follow-ups)
    parsed = query_to_action(question, memory=st.session_state.chat_memory)

    # 2. Debug: show parsed JSON
    st.subheader("Parsed Query")
    st.code(parsed, language="json")

    # 3. Update memory if valid
    if parsed:
        st.session_state.chat_memory = parsed

    # 4. Error if parsing failed
    if parsed is None:
        st.error("❌ Could not understand the question.")
    else:
        # 5. Run the structured query
        result, meta_data, stats_or_point = run_query_roads(
            roads,
            parsed,
            previous_context=st.session_state.chat_memory
        )
        qt = parsed.get("query_type")

        # ─── Trend Analysis ────────────────────────────────────────────────────
        if qt == "trend_analysis" and isinstance(meta_data, pd.DataFrame):
            st.subheader("📈 Yearly Trend")
            st.line_chart(meta_data.set_index("month_year")[["speedLimit", "distance"]])

        # ─── Summary Statistics ─────────────────────────────────────────────────
        elif qt == "summary_stats" and isinstance(stats_or_point, dict):
            st.subheader("📊 Summary Statistics")
            st.json(stats_or_point)
            st.markdown(f"""🧠 **Summary**:
- Average speed: **{stats_or_point['average_speed']} km/h**  
- Average distance: **{stats_or_point['average_distance']} km**  
- Segment count: **{stats_or_point['total_segments']}**  
""")

        # ─── Year-to-Year Comparison ────────────────────────────────────────────
        elif qt == "compare_years":
            # If stats summary was returned (no overlapping IDs)
            if isinstance(stats_or_point, dict):
                st.subheader("📊 Comparison Summary")
                st.json(stats_or_point)
            # Otherwise, show merged segment-level table
            elif not result.empty:
                st.subheader("📊 Year-to-Year Comparison")
                st.dataframe(result)
            else:
                st.warning("⚠️ No comparable data found.")

        # ─── Regular Map & Table for other queries ──────────────────────────────
        elif not result.empty:
            st.success(f"✅ Found {len(result)} road segments.")
            st.dataframe(result.drop(columns=["geometry"]))

            fig, ax = plt.subplots(figsize=(10, 6))
            result.plot(ax=ax, column="speedLimit", cmap="viridis", legend=True)
            ax.set_title("Map of Results")
            ax.axis("off")
            st.pyplot(fig)

        # ─── No Results ──────────────────────────────────────────────────────────
        else:
            st.warning("⚠️ No results found.")
