from .base import InstructionBase


class KeyVarInstruction(InstructionBase):
    head = '$='

    def run(self, variables, storage):
        storage.add_item(
            self.instruction_set.eval_expression(None, self.key, variables),
            self.instruction_set.eval_expression(None, self.value, variables)
        )
