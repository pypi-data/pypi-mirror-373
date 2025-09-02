from .base import InstructionBase
from ..produce import DefaultProduce


class DataInstruction(InstructionBase):
    head = '$>'
    produce_cls = DefaultProduce

    def run(self, variables, storage):
        produce = self.instruction_set.run(self.value, variables)
        if len(produce) > 1:
            value = [x.data for x in produce]
        elif len(produce) == 1:
            value = produce[0].data
        else:
            value = None
        return [self.produce_cls.wrapper(self.key)(value)]
