import ast
import json
from typing import Tuple, Union

def validate_json(test_json: Union[str, dict, list]) -> Tuple[bool, Union[dict, list, None]]:
    """
    Returns (True, data) if `test_json` is valid JSON (double-escaped or normal),
    or if it's already a dict/list. Otherwise (False, None).
    """
    # If it's already parsed, we're done
    if isinstance(test_json, (dict, list)):
        return True, test_json

    # Try to un-escape a Python string literal containing JSON
    try:
        unescaped = ast.literal_eval(test_json)
        if isinstance(unescaped, (dict, list)):
            return True, unescaped
        if isinstance(unescaped, str):
            parsed = json.loads(unescaped)
            if isinstance(parsed, (dict, list)):
                return True, parsed
    except (ValueError, SyntaxError, TypeError, json.JSONDecodeError):
        pass

    # Finally try raw JSON parsing
    try:
        parsed = json.loads(test_json)
        if isinstance(parsed, (dict, list)):
            return True, parsed
    except json.JSONDecodeError:
        pass

    return False, None
