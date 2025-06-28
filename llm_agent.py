# llm_agent.py
import subprocess
import json

def query_to_action(question, memory=None):
    """
    Uses Mistral via Ollama to convert a user's natural-language question into a structured query.
    Optionally uses `memory` (previous query) to support follow-up logic.
    """
    memory_instructions = ""

    if memory:
        memory_instructions = f"""
If the question is a follow-up like "compare that to Jan 2023",
use the previous month_year: "{memory.get("month_year", "")}" and road_name: "{memory.get("road_name", "")}".
"""

    prompt = f"""
You are an assistant converting natural language about Saudi road data (2022–2025) into JSON instructions.

Available query_type values:
- show_all_roads
- filter_by_road_name
- filter_by_speed
- filter_by_distance
- summary_stats
- detect_anomalies
- top_n
- near_location
- compare_years
- trend_analysis

Expected JSON structure:
{{
  "query_type": "...",
  "road_name": "...",         # if applicable
  "month_year": "...",        # e.g., "Jan 2025"
  "compare_year": "...",      # for compare_years
  "max_speed": ...,           # for speed filter
  "min_distance": ...,        # for distance filter
  "top_n": ...,               # for top queries
  "sort_by": "...",           # "speedLimit" or "distance"
  "location_name": "...",     # for location queries
  "radius_km": ...            # default 5
}}

### Examples:

Q: Show all roads in Jan 2024  
A:
{{ "query_type": "show_all_roads", "month_year": "Jan 2024" }}

Q: Show King Fahd Road in Jan 2025  
A:
{{ "query_type": "filter_by_road_name", "road_name": "King Fahd Road", "month_year": "Jan 2025" }}

Q: What are the top 5 longest roads in Jan 2023  
A:
{{ "query_type": "top_n", "top_n": 5, "sort_by": "distance", "month_year": "Jan 2023" }}

Q: Compare that to Jan 2023  
A:
{{ "query_type": "compare_years", "compare_year": "Jan 2023", "month_year": "Jan 2025", "road_name": "King Fahd Road" }}

Q: Show roads near King Fahd Hospital  
A:
{{ "query_type": "near_location", "location_name": "King Fahd Hospital", "radius_km": 5 }}

Q: What is the average speed in Jan 2024?  
A:
{{ "query_type": "summary_stats", "month_year": "Jan 2024" }}

Q: Show anomalies in Jan 2022  
A:
{{ "query_type": "detect_anomalies", "month_year": "Jan 2022" }}

Q: Show trend for Prince Mohammed Road  
A:
{{ "query_type": "trend_analysis", "road_name": "Prince Mohammed Road" }}

{memory_instructions}

Now answer this:
\"{question}\"
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=prompt.encode(),
            capture_output=True,
            timeout=20
        )
        output = result.stdout.decode("utf-8")

        # Attempt to extract a valid JSON object
        start = output.find("{")
        end = output.rfind("}") + 1
        return json.loads(output[start:end])

    except Exception as e:
        print("LLM Error:", e)
        return None
