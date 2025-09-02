from .base import InstructionBase


class KeyInstruction(InstructionBase):
    head = ''

    def run(self, variables, storage):
        storage.add_item(
            self.key,
            self.instruction_set.eval_expression(self.key, self.value, variables)
        )
