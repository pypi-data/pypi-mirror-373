'''
Created on 31 oct. 2017

@author: Jarrige_Pi
'''
import operator
import heapq

#****g* ganessa.sort/About
# PURPOSE
#   The module ganessa.sort provides sorting functions and classes used by the Ganessa tools.
#****
#****g* ganessa.sort/sClasses
#****

#****o* sClasses/HeapSort, HeapSortFunc, HeapSortRank
# SYNTAX
#   hs = HeapSortRank([index_key]): creates the heap structure.
#   "optional" arg rank must be provided to the methods.
#
#   hs = HeapSortFunc(rank_func [, index_key]): creates the heap structure.
#   "optional" arg rank is computed as rank_func(item), it must not be provided to the methods.
#
#   hs = HeapSort([key=None] [, index_key]): function that returns HeapSortFunc(key, index_key)
#   if key is present, otherwise returns HeapSortRank(index_key).
#
#   Instances provide the following methods:
#   * rank = hs.remove(item): removes item - raise KeyError if not found
#   * item, rank = hs.pop(): removes and returns the item of lowest rank.
#   * hs.push(item [, rank]): inserts or replace item with given rank.
#     If the item is already present, its rank and position are updated.
#   * hs.modify(item, offset): modify item rank by offset (HeapSortRank only).
#   * hs.update(item [, rank]): same as push but does nothing if rank unchanged.
#   * hs.update_if_lower(item [, rank]): same as push but does nothing if new rank
#     is higher or equal than the actual rank.
#   * hs.update_if_higher(item [, rank]): same as push but does nothing if new rank
#     is lower or equal than the actual rank.
#   * count = len(hs): returns the item count in the heap structure.
#
# ARGUMENTS
#   * optional function index_key: function extracting from item the key to be used for entries,
#     as index_key(item).
#   * function rank_func: function computing rank of item being inserted (HeapSortFunc),
#     as rank_func(item).
#   * function key: used to select between HeapSortFunc(key, index_key) or HeapSortRank(index_key).
#   * item: item to be pushed / popped. 
#   * number rank: defines the ordering of items. Mandatory with HeapSortRank methods.
#     Forbidden with HeapSortFunc methods.
# RESULT
#   * hs: HeapSortxxxx class member
#   * number rank: rank of removed element
#   * int count: remaining item count in the heap structure.
# REMARKS
#   * 'index_key' allow to use composite items such as tuple where e.g. the first element
#     is meaningful for the search, other elements being additional attributes to be kept together.
#     In such a case, index_key=itemgetter(0) tells that first element is the true key.
#   * HeapSortFunc can be used when rank is a subelement of composite items. In case of tuples
#     (item_id, item_rank, ...) the expected instanciation is HeapSortFunc(itemgetter(1), itemgetter(0)).
#   * HeapSort function is provided for compatibility with previous version of the HeapSort class.
# HISTORY
#   * Introduced in 1.8.2 (171031)
#   * 2.3.4 (221110): added rank and modify methods; remove returns rank
#   * 2.5.1 (250306): added index_key optional argument; implement key=func option
#     as a subclass HeapSortFunc of HeapSortRank in order to improve performance; define
#     HeapSort as a function, for compatibility.
#****
class HeapSortRank:
    '''Heap sort for a list of objects; makes use of heapq
    hs.push (new or existing item), hs.pop, hs.remove
    hs.update (do not change if equal)
    hs.update_if_higher, hs.update_if_lower
    hs.modify'''
    REMOVED = '_<removed-item>_'    # placeholder for a removed item
    extractor = lambda x: x

    def __init__(self, index_key=None):
        self.heap = []              # list of entries arranged in a heap
        self.entry_finder = {}      # mapping of items to entries
        self.counter = 0            # unique sequence count
        self.extractor = __class__.extractor if index_key is None else index_key

    def __len__(self):
        return len(self.entry_finder)

    def __bool__(self):
        return len(self.entry_finder) > 0

    def remove(self, item):
        'Mark an existing item as REMOVED. Raise KeyError if not found.'
        entry = self.entry_finder.pop(self.extractor(item))
        entry[-1] = self.REMOVED
        return entry[0]

    def pop(self):
        'Remove and return the lowest rank item. Raise KeyError if empty.'
        while self.heap:
            rank, _count, item = heapq.heappop(self.heap)
            if item is not self.REMOVED:
                del self.entry_finder[self.extractor(item)]
                return item, rank
        raise KeyError('pop from an empty queue')

    def push(self, item, rank):
        'Add a new item or update the rank and position of an existing item'
        if self.extractor(item) in self.entry_finder:
            self.remove(item)
        self._add(item, rank)

    def update(self, item, rank):
        'Add a new item or update the rank if different'
        self._conditional_update(item, rank, operator.__ne__)

    def update_if_lower(self, item, rank):
        self._conditional_update(item, rank, operator.__lt__)

    def update_if_higher(self, item, rank):
        self._conditional_update(item, rank, operator.__gt__)

    def _conditional_update(self, item, rank, cond):
        'Add a new item or update the rank of an existing item'
        if (ekey := self.extractor(item)) in self.entry_finder:
            entry = self.entry_finder[ekey]
            # do nothing if rank is the same
            if not cond(rank, entry[0]):
                return
            self.remove(item)
        self._add(item, rank)

    def _add(self, item, rank):
        '''Add a non-existing item'''
        self.counter += 1
        entry = [rank, self.counter, item]
        self.entry_finder[self.extractor(item)] = entry
        heapq.heappush(self.heap, entry)

    def rank(self, item):
        '''Returns the rank of an item. Raise KeyError if not found.'''
        return self.entry_finder[self.extractor(item)][0]

    def modify(self, item, offset):
        '''Modify item rank by adding offset - non functional rank only'''
        if offset == 0:
            return
        rank = self.remove(item)
        self._add(item, rank + offset)

class HeapSortFunc(HeapSortRank):
    """HeapSort subclass where rank is not provided as a arg
    but is computed as a function of the item"""
    def __init__(self, key, index_key=None):
        if key is None:
            raise ValueError("key function must be defined")
        if index_key is None and key.__class__ == operator.itemgetter:
            print("HeapSortFuncRank: index_key forced to 'itemgetter(0)'")
            index_key = operator.itemgetter(0)
        HeapSortRank.__init__(self, index_key=index_key)
        self.fun = key

    def push(self, item):
        rank = self.fun(item)
        HeapSortRank.push(self, item, rank)

    def update(self, item):
        'Add a new item or update the rank if different'
        rank = self.fun(item)
        self._conditional_update(item, rank, operator.__ne__)

    def update_if_lower(self, item):
        rank = self.fun(item)
        self._conditional_update(item, rank, operator.__lt__)

    def update_if_higher(self, item):
        rank = self.fun(item)
        self._conditional_update(item, rank, operator.__gt__)

    def modify(self, item, offset):
        '''Modify item rank by adding offset - non functional rank only'''
        if offset == 0:
            return
        raise ValueError

def HeapSort(key=None, index_key=None):
    """HeapSort class with optional key=arg for compatibility"""
    if key is None:
        return HeapSortRank(index_key=index_key)
    else:
        return HeapSortFunc(key, index_key=index_key)
