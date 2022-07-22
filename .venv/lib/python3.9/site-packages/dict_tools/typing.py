from typing import Type
from typing import Union


class _SpecialForm:
    __slots__ = ("_name", "__doc__", "_getitem")

    def __init__(self, getitem):
        self._getitem = getitem
        self._name = getitem.__name__
        self.__doc__ = getitem.__doc__

    def __getitem__(self, parameters):
        return self._getitem(self, parameters)


# Types for type-hinting, they cannot be used in casting
@_SpecialForm
def Computed(self, type_: Type):
    return Union[type_, type(None)]


@_SpecialForm
def Sensitive(self, type_: Type):
    return Union[type_, type(None)]
