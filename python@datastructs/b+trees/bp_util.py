def bp_binary_search(arr: list[int], key: int) -> int:
    # used for indexing the children
    lower_bound: int = 0
    upper_bound: int = len(arr) - 1
    curIn: int = -1
    
    while(True):
        curIn = (lower_bound + upper_bound) // 2 # divider
        if lower_bound > upper_bound:
            return lower_bound # special return for where "to insert"
        else:
            if arr[curIn] < key:
                lower_bound = curIn + 1 # upper half
            else:
                upper_bound = curIn - 1 # lower half

def binary_search(arr: list[int], key: int) -> int:
    lower_bound: int = 0
    upper_bound: int = len(arr) - 1
    curIn: int = -1
    
    while(True):
        curIn = (lower_bound + upper_bound) // 2 # divider
        if arr[curIn] == key:
            return curIn
        if lower_bound > upper_bound:
            return -1 # for regular binary search, just return -1
        else:
            if arr[curIn] < key:
                lower_bound = curIn + 1 # upper half
            else:
                upper_bound = curIn - 1 # lower half
    
def insert_sorted(arr: list[int], item: int) -> int:
    # guard cases
    if(len(arr) == 0):
        arr.append(item)
        return
    
    for idx in range(len(arr)):
        if(arr[idx] > item):
            arr.insert(idx, item)
            return idx
    # its the largest value
    arr.append(item)
    return len(arr)-1


# https://stackoverflow.com/questions/14822184/is-there-a-ceiling-equivalent-of-operator-in-python
def ceildiv(a, b):
    return -(a // -b)
        
        
    
    