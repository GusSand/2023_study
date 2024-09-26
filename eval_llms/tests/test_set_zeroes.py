'''

Given an m x n integer matrix matrix, if an element is 0, set its entire row and column to 0's.

You must do it in place.

 

Example 1:


Input: matrix = [[1,1,1],[1,0,1],[1,1,1]]
Output: [[1,0,1],[0,0,0],[1,0,1]]
Example 2:


Input: matrix = [[0,1,2,0],[3,4,5,2],[1,3,1,5]]
Output: [[0,0,0,0],[0,4,5,0],[0,3,1,0]]
 

Constraints:

m == matrix.length
n == matrix[0].length
1 <= m, n <= 200
-231 <= matrix[i][j] <= 231 - 1

'''

# write the tests
import pytest

from problems.set_zeroes import setZeroes

def test_1():
    matrix = [[1,1,1],[1,0,1],[1,1,1]]
    assert setZeroes(matrix) == [[1,0,1],[0,0,0],[1,0,1]]

def test_2():
    matrix = [[0,1,2,0],[3,4,5,2],[1,3,1,5]]
    assert setZeroes(matrix) == [[0,0,0,0],[0,4,5,0],[0,3,1,0]]

def test_3():
    matrix = [[1,2,3],[4,5,6],[7,8,9]]
    assert setZeroes(matrix) == [[1,2,3],[4,5,6],[7,8,9]]
