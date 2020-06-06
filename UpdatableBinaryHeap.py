from BinaryHeap import BinaryHeap

class UpdatableBinaryHeap(BinaryHeap):
    def __init__(self):
        super().__init__()
        self.__locators = {}

    def add(self, key, element):
        self.__locators[element] = self._len__()
        return super().add(key, element)

    def first(self):
        key, element = super().first()
        del self.__locators[element]
        return key, element
    
    def _swap(self, a, b):
        self.__locators[self._heap[a]._element] = b
        self.__locators[self._heap[b]._element] = a
        return super()._swap(a, b)

    def update_or_add(self, key, element):
        if element not in self.__locators.keys():
            self.add(key, element)
        else:
            position = self.__locators[element]
            self._bubble(position)

    def get_key(self, element):
        if element not in self.__locators.keys():
            return None
        else:
            position = self.__locators[element]
            return self._heap[position]._key

    def _bubble(self, position):
        parent_pos = self._parent(position)
        parent = self._heap[parent_pos]
        if position > 0 and self._heap[position]._key < parent._key:
            self._bubble_up(position)
        else:
            self._bubble_down(position)