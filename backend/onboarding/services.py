from rapidfuzz import process
from alumni.models import Person

def find_match(name, year):
    """Fuzzy match alumni by name and graduation year"""
    candidates = Person.objects.filter(graduation_year=year)
    
    if not candidates:
        return None
    
    names = [p.full_name for p in candidates]
    match = process.extractOne(name, names)
    
    if match and match[1] > 80:  # 80% similarity threshold
        return candidates[names.index(match[0])]
    
    return None