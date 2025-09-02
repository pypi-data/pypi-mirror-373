from .base import InstructionBase


class VarInstruction(InstructionBase):
    head = '_'

    def run(self, variables, storage):
        if isinstance(self.value, str):
            value = self.instruction_set.eval_expression(self.key_raw, self.value, variables)
        else:
            value = [x.data for x in self.instruction_set.run(self.value, variables)]
        variables.set_item(self.key_raw, value)
