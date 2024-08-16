""" Input to this function is a string represented multiple groups for nested parentheses separated by spaces. 
For each of the group, output the deepest level of nesting of parentheses. 
E.g. 
    (()()) has maximum two levels of nesting 
    ((())) has three. 
    
    >>> parse_nested_parens('(()()) ((())) () ((())()())') [2, 3, 1, 3] 
    
"""

from typing import List 

def parse_nested_parens(paren_string: str) -> List[int]:
    # split the string by space
    paren_list = paren_string.split(' ')
    # initialize a list to store the result
    result = []
    # iterate through the list
    for paren in paren_list:
        # initialize a counter to store the maximum level of nesting
        max_level = 0
        # initialize a counter to store the current level of nesting
        level = 0
        # iterate through the string
        for char in paren:
            # if the character is an open parenthesis, increase the level
            if char == '(':
                level += 1
                # if the current level is greater than the max level, update the max level
                if level > max_level:
                    max_level = level
            # if the character is a close parenthesis, decrease the level
            elif char == ')':
                level -= 1
        # append the max level to the result list
        result.append(max_level)
    return result