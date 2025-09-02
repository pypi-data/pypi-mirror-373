from .self import ProxySelf


class ProxyTreeNode(ProxySelf):
    _children_type = None

    @property
    def parent(self) -> object:
        return object.__getattribute__(self, "me")('parent')

    @property
    def children(self) -> list[object]:
        return object.__getattribute__(self, "us")('children', object.__getattribute__(self, "_children_type"))

#
# class ProxyA(ProxyTreeNode):
#     _children_type = iter
#
#     @property
#     def i(self):
#         return 2
#
#
# class A:
#     i = 1
#     j = 2
#
#     def __init__(self, value):
#         self.value = value
#
#     def __str__(self):
#         return f"{self.__class__.__name__} {self.value}"
#
#     @property
#     def parent(self) -> 'A':
#         return self.__class__(self.value - 1)
#
#     @property
#     def children(self) -> list['A']:
#         return [self.__class__(self.value + 1) for i in range(2)]
#
#
# a = ProxyA.wrap_share(A(100), {})
# print(a.i)  # 2
# print(a.j)  # 2
# print(a)  # <__main__.ProxyA object at 0x0000029C60306080>
# print(a.value)  # 100
# print(a.parent)  # <__main__.ProxyA object at 0x0000029C60306080>
# print(a.parent.value)  # 99
# print(a.children)  # [<__main__.ProxyA object at 0x0000017DE59882E0>, <__main__.ProxyA object at 0x0000017DE59882B0>]
# print(isinstance(a, A))  # True
# print(isinstance(a, ProxyA))  # True
# print(isinstance(a.parent, A))  # True
# print(isinstance(a.parent, ProxyA))  # True
# print(type(a))  # <class '__main__.ProxyA'>
