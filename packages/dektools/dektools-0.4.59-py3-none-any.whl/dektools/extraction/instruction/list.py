from .base import InstructionBase


class ListInstruction(InstructionBase):
    head = '$['

    def run(self, variables, storage):
        produce = []
        payload_list = self.instruction_set.eval_expression(None, self.key, variables)
        for i, payload in enumerate(payload_list):
            produce.extend(self.instruction_set.run(self.value, variables, derive=[payload, {
                '___list': payload_list,
                '___index': i,
                '___count': len(payload_list),
                '___last': len(payload_list) - 1 == i,
            }]))
        return produce
