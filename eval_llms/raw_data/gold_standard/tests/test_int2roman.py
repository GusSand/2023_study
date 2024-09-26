""" Given a positive integer, obtain its roman numeral equivalent as a string, and return it in lowercase. 
Restrictions: 1 <= num <= 1000 Examples: >>> int_to_mini_roman(19) == 'xix' >>> int_to_mini_roman(152) == 
'clii' >>> int_to_mini_roman(426) == 'cdxxvi' """

# write the tests
import pytest

from problems.int2roman import int_to_mini_roman

def test_1():
    assert int_to_mini_roman(19) == 'xix'

def test_2():
    assert int_to_mini_roman(152) == 'clii' 

def test_3():
    assert int_to_mini_roman(251) == 'ccli' 

def test_4():
    assert int_to_mini_roman(426) == 'cdxxvi' 
    
def test_5():
    assert int_to_mini_roman(500) == 'd' 

def test_6():
    assert int_to_mini_roman(1) == 'i' 
    
def test_7():
    assert int_to_mini_roman(4) == 'iv' 
    
def test_8():
    assert int_to_mini_roman(43) == 'xliii' 
    
def test_9():
    assert int_to_mini_roman(90) == 'xc' 

def test_10():    
    assert int_to_mini_roman(94) == 'xciv' 
    
def test_11():
    assert int_to_mini_roman(532) == 'dxxxii' 
    
def test_12():
    assert int_to_mini_roman(900) == 'cm' 
    
def test_13():
    assert int_to_mini_roman(994) == 'cmxciv' 
    
def test_14():
    assert int_to_mini_roman(1000) == 'm' # Check some edge cases that are easy to work out by hand. assert True