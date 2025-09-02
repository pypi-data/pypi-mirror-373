class Fluent_List(list):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, args[0])

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def contains(self, item):
        return item in self

    def index(self, index):
        if index < self.size():
            return self[index]

    def first(self):
        if self.size() > 0:
            return self[0]

    def last(self):
        if self.size() > 0:
            return self[self.size() -1]

    def pop(self):
        """
        normal pop() function with the only variation being that empty lists will return None instead of raising an exception
        """
        if self.size() > 0:
            return super().pop()

    def push(self, value):
        self.append(value)
        return self

    def size(self):
        return len(self)

    def sorted(self):
        return sorted(self)

    def type(self):                         # todo: find a way to add this kind of methods to all Fluent Classes
        return type(self)


Fluent_List.sort = Fluent_List.sorted