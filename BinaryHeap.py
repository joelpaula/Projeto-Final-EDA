class BinaryHeap(object):
    class _Node(object):
        def __init__(self, key, element):
            self._element = element
            self._key = key
        def __str__(self):
            return self._key
        def __repr__(self):
                return str(self)


    def __init__(self):
        self._heap = []

    def __len__(self):
        return len(self._heap)
    
    @staticmethod
    def _parent(position):
        return (position - 1)//2

    @staticmethod
    def _left(position):
        return 2 * position + 1
    
    @staticmethod
    def _right(position):
        return 2 * position + 2
    
    def is_empty(self):
        return len(self._heap) == 0
    
    def inspect_first(self):
        if self.is_empty():
            return None
        return self._heap[0]._key, self._heap[0]._element

    def add(self, key, element):
        node = self._Node(key, element)
        self._heap.append(node)
        self._bubble_up(len(self._heap)-1)

    def first(self):
        k, v = self.inspect_first()
        last = self._heap.pop()
        if not self.is_empty():
            self._heap[0]     
            self._bubble_down(0)
        return k, v
    
    def _bubble_up(self, position):
        if position <= 0 :
            return
        parent_pos = self._parent(position)
        parent = self._heap[parent_pos]
        node = self._heap[position]
        if parent._key > node._key:
            self._swap(position, parent_pos)
            self._bubble_up(parent_pos)
    
    def _swap(self, a, b):
        o = self._heap[a]
        self._heap[a] = self._heap[b]
        self._heap[b] = o
    
    def _exists(self, position):
        return len(self._heap) > position

    def _bubble_down(self, position):
        left = self._left(position)
        right = self._right(position)
        # no left node = no right node = nothing to do here
        if not self._exists(left):
            return
        # print("Exists Right: ", self._exists(right), right)
        # print("Exists Left:", self._exists(left), left)
        if self._exists(right) and self._heap[left]._key > self._heap[right]._key:
            new_pos = right
        else:
            new_pos = left
        if self._heap[position]._key > self._heap[new_pos]._key:
            self._swap(position, new_pos)
            self._bubble_down(new_pos)
