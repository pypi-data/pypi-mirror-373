import re


def extract_id_from_ado_response(json_text, pattern):
    """Extract ID value from JSON in the response text"""
    match = re.search(pattern, json_text)
    if match:
        return match.group(1)
    return None
