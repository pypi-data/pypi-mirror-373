import pytest
from collections import Counter
from rara_linker.tools.normalizers import PersonNormalizer, KeywordNormalizer


def test_generating_person_variations():
    expected_output = [
        "Karl Ristikivi", 
        "Карл Ристикиви", 
        "Ристикиви, Карл", 
        "Ristikivi, Karl"
    ]
    pn_1 = PersonNormalizer("Карл Ристикиви")
    var_1 = pn_1.variations
   
    pn_2 = PersonNormalizer("Ристикиви, Карл")
    var_2 = pn_2.variations
    
    assert Counter(var_1) == Counter(expected_output)
    assert Counter(var_2) == Counter(expected_output)
    
    
def test_generating_keyword_variations():
    expected_output = [
        "agendad (religioon)", 
        "agenda", 
        "agendad", 
        "agenda ( religioon )"
    ]
    kn_1 = KeywordNormalizer("agendad (religioon)")
    var_1 = kn_1.variations
    assert Counter(var_1) == Counter(expected_output)
    
