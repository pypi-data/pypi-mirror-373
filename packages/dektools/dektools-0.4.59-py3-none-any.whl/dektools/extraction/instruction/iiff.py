from .base import InstructionBase


class ConditionInstruction(InstructionBase):
    pass


class IfInstruction(ConditionInstruction):
    head = '$if'

    def run(self, variables, storage):
        ok = bool(self.instruction_set.eval_expression_raw(self.key, variables))
        variables.add_item('$if', ok)
        if ok:
            return self.instruction_set.run(self.value, variables)


class ElifInstruction(ConditionInstruction):
    head = '$elif'

    def run(self, variables, storage):
        if not isinstance(self.instruction_set.last_instruction, IfInstruction):
            raise SyntaxError('$elif must be at after of $if')
        if not variables.get_item('$if'):
            ok = self.instruction_set.eval_expression_raw(self.key, variables)
            if ok:
                variables.add_item('$if', ok)
                return self.instruction_set.run(self.value, variables)


class ElseInstruction(ConditionInstruction):
    head = '$else'

    def run(self, variables, storage):
        if not isinstance(self.instruction_set.last_instruction, (IfInstruction, ElifInstruction)):
            raise SyntaxError('$else must be at after of $if/$elif')
        if not variables.get_item('$if'):
            return self.instruction_set.run(self.value, variables)
