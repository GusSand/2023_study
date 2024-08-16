""" You will be given a string of words separated by commas or spaces. 
our task is to split the string into words and return an array of the words. 

For example: 

words_string("Hi, my name is John") == ["Hi", "my", "name", "is", "John"] 
words_string("One, two, three, four, five, six") == ["One", "two", "three", "four", "five", "six"] """


import pytest
from problems.words_string import words_string

def test_1():
    s = "Hi, my name is John"
    assert words_string(s) == ["Hi", "my", "name", "is", "John"]

def test_2():
    s = "One, two, three, four, five, six"
    assert words_string(s) == ["One", "two", "three", "four", "five", "six"]

def test_3():
    assert words_string("Hi, my name") == ["Hi", "my", "name"] 

def test_4():
    assert words_string("One,, two, three, four, five, six,") == ["One", "two", "three", "four", "five", "six"] 

def test_5():
    assert words_string("") == [] 

def test_6():
    assert words_string("ahmed , gamal") == ["ahmed", "gamal"]

def test_7():
    assert words_string("the quick    brown fox") == ["the", "quick", "brown", "fox"] 
