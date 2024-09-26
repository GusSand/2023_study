'''
ou are given an array of k linked-lists lists, each linked-list is sorted in ascending order.

Merge all the linked-lists into one sorted linked-list and return it.

 

Example 1:

Input: lists = [[1,4,5],[1,3,4],[2,6]]
Output: [1,1,2,3,4,4,5,6]
Explanation: The linked-lists are:
[
  1->4->5,
  1->3->4,
  2->6
]
merging them into one sorted list:
1->1->2->3->4->4->5->6
Example 2:

Input: lists = []
Output: []
Example 3:

Input: lists = [[]]
Output: []
 

Constraints:

k == lists.length
0 <= k <= 104
0 <= lists[i].length <= 500
-104 <= lists[i][j] <= 104
lists[i] is sorted in ascending order.
The sum of lists[i].length will not exceed 104.
'''

def merge_lists(lists):

    merged = []
    for l in lists:
        merged.extend(l)
        
    # if you can't use the built-in sort function, you can use bubble sort
    # for i in range(len(merged)):
    #     for j in range(len(merged)-1):
    #         if merged[j] > merged[j+1]:
    #             merged[j], merged[j+1] = merged[j+1], merged[j]

    return sorted(merged)

# the complexity of this function is O(n^2) because of the bubble sort
# if you use the built-in sort function, the complexity is O(n log n) where n is the total number of elements in all the lists combined
# the space complexity is O(n) because of the merged list
# the space complexity can be reduced to O(1) if you sort the lists in place
# and then merge them into a single list
# this can be done by using a priority queue
# you can also use a heap to merge the lists
# the heap will have the first element of each list
# and you can pop the smallest element from the heap
# and append it to the merged list
# then you can push the next element from the list of the popped element to the heap
# you can continue this process until the heap is empty
# this way you can reduce the space complexity to O(k) where k is the number of lists
# and the time complexity will be O(n log k) where n is the total number of elements in all the lists combined
# this is because the heapify operation takes O(k) time
# and you have to push and pop elements from the heap n times
# so the total time complexity is O(n log k)
# you can also use a divide and conquer approach
# where you merge the lists in pairs
# then merge the merged lists in pairs
# and so on until you have a single merged list
# this approach has a time complexity of O(n log k)
# and a space complexity of O(1)
# because you are merging the lists in place

# let's implement the divide and conquer approach

def merge(self, lists):
    if not lists:
        return []
    if len(lists) == 1:
        return lists[0]
    mid = len(lists) // 2
    left = self.merge(lists[:mid])
    right = self.merge(lists[mid:])
    return self.merge_two_lists(left, right)

def merge_two_lists(self, l1, l2):
    if not l1:
        return l2
    if not l2:
        return l1
    if l1[0] < l2[0]:
        return [l1[0]] + self.merge_two_lists(l1[1:], l2)
    return [l2[0]] + self.merge_two_lists(l1, l2[1:])