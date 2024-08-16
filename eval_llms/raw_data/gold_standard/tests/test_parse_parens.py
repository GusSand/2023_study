""" Input to this function is a string represented multiple groups for nested parentheses separated by spaces. 
For each of the group, output the deepest level of nesting of parentheses. 
E.g. 
    (()()) has maximum two levels of nesting 
    ((())) has three. 
    
    >>> parse_nested_parens('(()()) ((())) () ((())()())') [2, 3, 1, 3] 
    
"""

from problems.parse_parens import parse_nested_parens
import pytest

def test_parse_nested_parens():
    assert parse_nested_parens('(()()) ((())) () ((())()())') == [2, 3, 1, 3]
    assert parse_nested_parens('() (()) ((())) (((())))') == [1, 2, 3, 4]
    assert parse_nested_parens('(()(())((())))') == [4]
    assert parse_nested_parens('()') == [1]