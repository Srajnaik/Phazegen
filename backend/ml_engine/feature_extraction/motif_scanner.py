import re

def scan_crispr(sequence: str):
    """
    Heuristic: Looks for clustered regular interspaced short palindromic repeats.
    """
    # Simplified repeat pattern (e.g., GTTT...GTTT)
    repeat_pattern = r"(GTTT.{20,50}GTTT)" 
    matches = re.findall(repeat_pattern, sequence)
    
    return {
        "present": len(matches) > 0,
        "array_count": len(matches)
    }

def scan_markers(sequence: str, markers: dict):
    """
    Scans for specific genetic markers (AMR or Virulence).
    """
    found = []
    for name, pattern in markers.items():
        if pattern in sequence:
            found.append(name)
    return found