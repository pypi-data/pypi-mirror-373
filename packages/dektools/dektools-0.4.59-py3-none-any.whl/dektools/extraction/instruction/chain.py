from .base import InstructionBase


class ChainInstruction(InstructionBase):
    head = '$+'

    def run(self, variables, storage):
        return self.instruction_set.run(self.value, variables, storage)
