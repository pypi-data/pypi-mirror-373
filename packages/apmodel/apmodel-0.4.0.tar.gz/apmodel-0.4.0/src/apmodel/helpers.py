from typing import Dict, Any, List, Set

def has_match(data: Dict[str, Any], expected_keys: List[str]) -> bool:
    """
    Checks if all expected keys are present in the data dictionary.
    """
    return set(expected_keys).issubset(data.keys())