import re
from ..core import tool

@tool
def test_regex_pattern(pattern: str, test_string: str):
    """
    Tests a regular expression pattern against a string to see if it matches.
    Returns all matches found. Use this to validate or debug a regex pattern.

    Args:
        pattern: The regular expression pattern to test.
        test_string: The string to search for matches within.
    """
    try:
        # Find all non-overlapping matches of the pattern in the string
        matches = re.findall(pattern, test_string)
        
        if not matches:
            return {
                "match_found": False,
                "match_count": 0,
                "matches": []
            }
        
        return {
            "match_found": True,
            "match_count": len(matches),
            "matches": matches
        }
        
    except re.error as e:
        # Catch errors from an invalid regex pattern
        return {"error": f"Invalid regex pattern: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

