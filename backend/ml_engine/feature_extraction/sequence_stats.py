from collections import Counter

def get_basic_stats(sequence: str):
    length = len(sequence)
    if length == 0:
        return {"length": 0, "gc_content": 0, "counts": {}, "skew": 0}

    counts = Counter(sequence)
    gc_count = counts.get("G", 0) + counts.get("C", 0)
    
    gc_content = (gc_count / length) * 100 if length > 0 else 0
    
    # AT GC Skew: (G - C) / (G + C)
    skew = 0.0
    if gc_count > 0:
        skew = (counts.get("G", 0) - counts.get("C", 0)) / gc_count

    return {
        "length": length,
        "gc_content": round(gc_content, 2),
        "counts": dict(counts),
        "at_gc_skew": round(skew, 4)
    }