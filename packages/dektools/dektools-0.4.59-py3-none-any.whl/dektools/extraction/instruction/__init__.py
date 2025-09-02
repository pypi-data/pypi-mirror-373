from .chain import *
from .data import *
from .key import *
from .keyvar import *
from .list import *
from .storageflush import *
from .var import *
from .filter import *
from .iiff import *


def get_instructions_cls(*cls_list):
    array = [
        ChainInstruction,
        DataInstruction,
        KeyVarInstruction,
        ListInstruction,
        StorageFlushInstruction,
        VarStorageFlushInstruction,
        VarInstruction,
        FilterInstruction,
        IfInstruction, ElifInstruction, ElseInstruction,
        KeyInstruction,  # must be at last
    ]
    for cls in cls_list:
        for i in range(len(array)):
            if issubclass(cls, (array[i],)):
                array[i] = cls
                break
        else:
            array.insert(0, cls)
    return array
