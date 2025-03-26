import json

# to convert json string response to python dictionary data type
def get_response_string(input: str):
    cleaned_string = input.strip("```json").strip("```").strip()
    response = json.loads(cleaned_string)
    return response