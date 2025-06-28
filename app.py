# app.py
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
from geospatial_utils import run_query_roads, load_all_road_data
from llm_agent import query_to_action

st.set_page_config(layout="wide")
st.title("🚦 THTC Demo – AI Chatbot For Data(2022–2025)")

# Load all roads from 'data/new/' containing Jan folders
roads = load_all_road_data("data/new/")

# Create a form that submits on Enter
with st.form("question_form"):
    question = st.text_input(
        "Ask something about Saudi roads between Jan 2022 and Jan 2025:",
        placeholder="Enter your question here..."
    )
    submitted = st.form_submit_button("Submit")

if submitted:
    with st.spinner("Thinking..."):
        parsed = query_to_action(question)
        st.subheader("Parsed Query")
        st.code(parsed, language="json")


        if parsed is None:
            st.error("❌ Could not understand the question. Try rephrasing.")
        else:
            result, _, _ = run_query_roads(roads, parsed)

            if result.empty:
                st.warning("⚠️ No results found for this question.")
            else:
                st.success(f"✅ Found {len(result)} matching data.")
                st.dataframe(result.drop(columns=["geometry"]))

                fig, ax = plt.subplots(figsize=(10, 6))
                result.plot(ax=ax, column="speedLimit", cmap="viridis", legend=True)
                ax.set_title("Road Segments")
                ax.axis("off")
                st.pyplot(fig)
