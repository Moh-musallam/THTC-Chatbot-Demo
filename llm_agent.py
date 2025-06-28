def query_to_action(question):
    prompt = f"""
You are a helpful assistant that converts questions about Saudi road segment data into structured JSON.

Available query types:
- show_all_roads
- filter_by_road_name
- filter_by_speed
- filter_by_distance

Each query can include:
- road_name: a street name if mentioned
- max_speed: a speed limit threshold if mentioned
- min_distance: a minimum distance (in kilometers)
- month_year: one of ["Jan 2022", "Jan 2023", "Jan 2024", "Jan 2025"]

Examples:

Q: Show all roads in Jan 2024
A:
{{
  "query_type": "show_all_roads",
  "month_year": "Jan 2024"
}}

Q: Show roads with speed limit under 60 in Jan 2023
A:
{{
  "query_type": "filter_by_speed",
  "max_speed": 60,
  "month_year": "Jan 2023"
}}

Q: Show King Fahd Road in Jan 2025
A:
{{
  "query_type": "filter_by_road_name",
  "road_name": "King Fahd Road",
  "month_year": "Jan 2025"
}}

Q: Show roads with distance more than 130km in Jan 2022
A:
{{
  "query_type": "filter_by_distance",
  "min_distance": 130,
  "month_year": "Jan 2022"
}}
{{
  "query_type": "filter_by_road_name",
  "road_name": "Prince Mohammed Ibn Salman Road",
  "month_year": "Jan 2025"
}}


Now answer this:
\"{question}\"
"""
    import subprocess
    import json

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=prompt.encode(),
            capture_output=True,
            timeout=20
        )
        output = result.stdout.decode("utf-8")

        start = output.find("{")
        end = output.rfind("}") + 1
        return json.loads(output[start:end])

    except Exception as e:
        print("LLM Error:", e)
        return None
