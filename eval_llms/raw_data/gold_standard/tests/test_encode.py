""" Write a function that takes a message, and encodes in such a way that it swaps case of all letters, 
replaces all vowels in the message with the letter that appears 2 places ahead of that vowel in the english alphabet. 
Assume only letters. 

Examples: 
>>> encode('test') 'TGST' 
>>> encode('This is a message') 'tHKS KS C MGSSCGG' """

import pytest
from problems.encode import encode


def test_1():
    print (encode('test'))
    assert encode('test') == 'TGST'

def test_2():
    assert encode('Mudasir') == 'mWDCSKR'

def test_3():
    assert encode('YES') == 'ygs'

def test_4():
    assert encode('This is a message') == 'tHKS KS C MGSSCGG'

def test_5():
    assert encode("I DoNt KnOw WhAt tO WrItE") == 'k dQnT kNqW wHcT Tq wRkTg'