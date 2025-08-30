import pytest
from cliify.splitHelper import splitWithEscapes

def test_splitWithEscapes():
    # Basic splitting with no maxsplit
    assert splitWithEscapes("a,b,c", ",") == ["a", "b", "c"]
    
    # Basic maxsplit tests
    assert splitWithEscapes("a,b,c,d,e", ",", maxsplit=2) == ["a", "b", "c,d,e"]
    assert splitWithEscapes("a,b,c,d,e", ",", maxsplit=1) == ["a", "b,c,d,e"]
    assert splitWithEscapes("a,b,c,d,e", ",", maxsplit=0) == ["a,b,c,d,e"]
    assert splitWithEscapes("a,b,c,d,e", ",", maxsplit=-1) == ["a", "b", "c", "d", "e"]
    
    # Escape pair tests with maxsplit
    assert splitWithEscapes("a,[b,c],d,e", ",", maxsplit=2) == ["a", "[b,c]", "d,e"]
    assert splitWithEscapes("a,{b,c},d,e", ",", maxsplit=1) == ["a", "{b,c},d,e"]
    assert splitWithEscapes('a,"b,c",d,e', ",", maxsplit=2) == ['a', '"b,c"', "d,e"]
    
    # Multiple nested escapes with maxsplit
    assert splitWithEscapes("a,[b,{c,d}],e,f", ",", maxsplit=2) == ["a", "[b,{c,d}]", "e,f"]
    
    # Empty string cases
    assert splitWithEscapes("", ",", maxsplit=1) == []
    #assert splitWithEscapes(",", ",", maxsplit=1) == ["", ""]
    #assert splitWithEscapes(",,", ",", maxsplit=1) == ["", ","]
    
    # Whitespace handling with strip=True/False
    assert splitWithEscapes(" a , b , c ", ",", strip=True, maxsplit=1) == ["a", "b , c"]
    assert splitWithEscapes(" a , b , c ", ",", strip=False, maxsplit=1) == [" a ", " b , c "]
    
    # Custom escape pairs
    custom_pairs = ["++", "**"]
    assert splitWithEscapes("a,+b,c+,d", ",", escape_pairs=custom_pairs, maxsplit=2) == ["a", "+b,c+", "d"]
    
    # Edge cases with escape pairs
    #assert splitWithEscapes("[[]], [,], foo", ",", maxsplit=1) == ["[[]], [,]", "foo"]
    assert splitWithEscapes('"""",foo,"', ",", maxsplit=1) == ['""""', 'foo,"']

# def test_splitWithEscapes_error_cases():
#     # Test unmatched escape pairs
#     with pytest.raises(Exception):  # You might want to define a specific exception type
#         splitWithEscapes("a,[b,c,d", ",")
    
#     # Test invalid maxsplit values
#     with pytest.raises(TypeError):
#         splitWithEscapes("a,b,c", ",", maxsplit="invalid")
    
#     # Test invalid delimiter
#     with pytest.raises(TypeError):
#         splitWithEscapes("a,b,c", None)

def test_splitWithEscapes_complex_nesting():
    # Test complex nesting scenarios with maxsplit
    input_str = "level0,[level1,{level2,[level3],level2},level1],level0"
    expected = ["level0", "[level1,{level2,[level3],level2},level1]", "level0"]
    assert splitWithEscapes(input_str, ",", maxsplit=2) == expected
    
    # Test with different maxsplit values on the same complex string
    assert len(splitWithEscapes(input_str, ",", maxsplit=1)) == 2
    assert len(splitWithEscapes(input_str, ",", maxsplit=0)) == 1
    assert splitWithEscapes(input_str, ",", maxsplit=-1) == expected

def test_splitWithEscapes_performance():
    # Test with a larger string to ensure performance is reasonable
    large_str = "a,[b,c]," * 1000 + "end"
    result = splitWithEscapes(large_str, ",", maxsplit=50)
    assert len(result) == 51
    assert result[-1].endswith("end")