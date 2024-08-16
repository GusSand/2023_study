import pytest 
from problems.remove_element import removeElement

def test_1():
    nums = [3,2,2,3]
    val = 3
    assert removeElement(nums, val) == 2

def test_2():
    nums = [0,1,2,2,3,0,4,2]
    val = 2
    assert removeElement(nums, val) == 5

def test_3():
    nums = [1,2,3,4,5]
    val = 6
    assert removeElement(nums, val) == 5

