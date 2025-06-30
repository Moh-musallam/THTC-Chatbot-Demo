# 🧠 THTC Chatbot Demo – Geospatial AI Assistant (2022–2025)

Welcome to the **THTC Chatbot Demo**, a powerful AI assistant that lets you query and explore Saudi Arabia's road network using natural language. It uses geospatial data from the years **2022 to 2025** and supports advanced insights, summaries, trends, and comparisons.

---

## 🚀 Features

✅ Ask questions like:

* "Show roads with speed > 100 km/h in Jan 2025"
* "Compare King Fahd Road between Jan 2025 and Jan 2023"
* "What is the average speed in 2023?"
* "Top 5 longest roads in 2022"

✅ Supports:

* Road filtering by name, distance, speed, year
* Year-to-year comparisons (table or summary)
* Trend visualizations over time
* Anomaly detection (high speed/distance)
* Conversational memory for follow-up questions

---

## 🗂️ Project Structure

```
├── app.py                  # Main Streamlit app
├── llm_agent.py           # LLM query parser (converts questions to structured commands)
├── geospatial_utils.py    # All logic to load, filter, and compare geospatial data
├── requirements.txt       # Python dependencies
└── data
    └── new
        ├── Jan 2022
        ├── Jan 2023
        ├── Jan 2024
        └── Jan 2025
```

Each folder under `data/new/` contains `.geojson` files for multiple roads.

---

## 💻 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Moh-musallam/THTC-Chatbot-Demo.git
cd THTC-Chatbot-Demo
```

### 2. Create and activate a virtual environment (optional but recommended)

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

---

## 📊 Data Requirements

* Each `.geojson` file must include:

  * `segmentId`, `newSegmentId`, `speedLimit`, `frc`, `streetName`, `distance`
  * The app ignores other columns if present.

---

## 🤖 Powered By

* Streamlit (frontend)
* GeoPandas (geospatial filtering)
* Matplotlib (visualizations)
* OpenAI-compatible LLM (query understanding)

---

## 📌 TODO (Future Ideas)

* Add a prediction model for predicting traffic or needed insights
* Integrate live traffic feed via API
* Export query results to Excel or PDF
* Add Time-Series model For Predictions 

---

## 📬 Contact

Made by [Mohammad Musallam](https://github.com/Moh-musallam)

---

> ⚠️ For demonstration only. Not connected to live data. All analysis is local and based on uploaded road data.
