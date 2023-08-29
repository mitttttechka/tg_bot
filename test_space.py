class A:
    def __init__(self):
        self.a = 3

    def increase(self):
        self.a += 1
        return None


class B:
    def __init__(self, d):
        self.a = d


d = A()
c = B(d)
print(c.a.a)
print(d.a)
d.increase()
print(c.a.a)
print(d.a)


