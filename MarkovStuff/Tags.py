
class nullableDict(dict):
    def __init__(self,default):
        super().__init__()
        self.default = default
        
    def __getitem__(self,i):
        try:
            return super().__getitem__(i)
        except KeyError:
            return self.default
 

class TagIterator:
    def __init__(self,tagset):
        self.index = 0
        self.tagset = tagset

    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            result = self.tagset[self.index]
        except IndexError:
            raise StopIteration
        self.index += 1
        return result

class TagSet:
    def __repr__(self):
        return "<TagSet {}>".format(self.name)
    def __init__(self,name):
        self.labels = []
        self.name = name
    def __contains__(self,y):
        return y in self.labels

    def __iter__(self):
        return TagIterator(self)
    
    def __getitem__(self,i):
        return self.labels[i]

class Tag:
    def __init__(self,value=[]):
        self.value = tuple(value)
    def __eq__(self,o):
        i = len(self.value)
        if i != len(o.value):
            return False
        for x in range(i):
            if self.value[x] != o.value[x]:
                return False
        return True
    def __hash__(self):
        return hash(self.value)
