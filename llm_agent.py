# llm_agent.py
import subprocess
import json

def query_to_action(question, memory=None):
    """
    Uses Mistral via Ollama to convert a user's natural-language question
    into a structured JSON query. Optionally uses `memory` for follow-ups.
    """
    memory_instructions = ""
    if memory:
        memory_instructions = f"""
If this is a follow-up like "compare that to Jan 2023", reuse the previous:
  month_year: "{memory.get('month_year', '')}"
  road_name: "{memory.get('road_name', '')}"
"""

    prompt = f"""
You are an assistant converting natural-language questions about Saudi road data (2022–2025) into JSON instructions.

Available query_type values:
- show_all_roads
- filter_by_road_name
- filter_by_speed
- filter_by_distance
- summary_stats
- detect_anomalies
- top_n
- compare_years
- trend_analysis

Your JSON should include only the fields relevant to the query:
{{
  "query_type": "...",
  "road_name": "...",       # if filtering by name
  "month_year": "...",      # e.g. "Jan 2025"
  "compare_year": "...",    # for compare_years
  "max_speed": ...,         # for speed filters
  "min_distance": ...,      # for distance filters
  "top_n": ...,             # for top_n queries
  "sort_by": "speedLimit"   # or "distance"
}}

### Examples

Q: Show all roads in Jan 2024  
A:
{{ 
  "query_type": "show_all_roads", 
  "month_year": "Jan 2024" 
}}

Q: Show King Fahd Road in Jan 2025  
A:
{{ 
  "query_type": "filter_by_road_name", 
  "road_name": "King Fahd Road", 
  "month_year": "Jan 2025" 
}}

Q: Roads with speed limit under 60 in Jan 2023  
A:
{{ 
  "query_type": "filter_by_speed", 
  "max_speed": 60, 
  "month_year": "Jan 2023" 
}}

Q: Roads with distance over 1000 in Jan 2022  
A:
{{ 
  "query_type": "filter_by_distance", 
  "min_distance": 1000, 
  "month_year": "Jan 2022" 
}}

Q: What is the average speed in Jan 2025?  
A:
{{ 
  "query_type": "summary_stats", 
  "month_year": "Jan 2025" 
}}

Q: Show roads with unusual speeds in Jan 2024  
A:
{{ 
  "query_type": "detect_anomalies", 
  "month_year": "Jan 2024" 
}}

Q: What are the top 5 longest roads in Jan 2023?  
A:
{{ 
  "query_type": "top_n", 
  "top_n": 5, 
  "sort_by": "distance", 
  "month_year": "Jan 2023" 
}}

Q: Compare that to Jan 2022  
A:
{{ 
  "query_type": "compare_years", 
  "month_year": "Jan 2025", 
  "compare_year": "Jan 2022", 
  "road_name": "King Fahd Road" 
}}

Q: Show trend for Prince Mohammed Road  
A:
{{ 
  "query_type": "trend_analysis", 
  "road_name": "Prince Mohammed Road" 
}}

{memory_instructions}
Now answer this:
\"{question}\"
"""

    try:
        proc = subprocess.run(
            ["ollama", "run", "mistral"],
            input=prompt.encode(),
            capture_output=True,
            timeout=20
        )
        output = proc.stdout.decode("utf-8")
        # Extract the JSON object
        start = output.find("{")
        end = output.rfind("}") + 1
        return json.loads(output[start:end])
    except Exception as e:
        print("LLM Error:", e)
        return None
