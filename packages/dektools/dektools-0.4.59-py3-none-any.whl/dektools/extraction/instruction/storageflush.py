from .base import InstructionBase
from ..produce import DefaultProduce


class StorageFlushInstruction(InstructionBase):
    head = '$<'
    produce_cls = DefaultProduce

    def run(self, variables, storage):
        if self.value is None:
            reset = True
        else:
            reset = self.instruction_set.eval_expression(None, self.value, variables)
        return [storage.flush(self.produce_cls.wrapper(self.key), reset)]


class VarStorageFlushInstruction(InstructionBase):
    head = '$$<'
    produce_cls = DefaultProduce

    def run(self, variables, storage):
        if self.value is None:
            reset = True
        else:
            reset = self.instruction_set.eval_expression(None, self.value, variables)
        if self.key in storage.value:
            name = storage.value[self.key]
        else:
            name = self.instruction_set.eval_expression(None, self.key, variables)
        return [storage.flush(self.produce_cls.wrapper(name), reset)]
