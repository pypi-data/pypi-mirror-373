from .base import InstructionBase


class FilterInstruction(InstructionBase):
    head = '$|'

    def run(self, variables, storage):
        self.instruction_set.filter_set.update(self.value)
