from ..escape import str_escape_split, str_escape_custom
from .produce import DefaultProduce
from .filter import FilterSet
from .base.value import ProxyValue
from .base.storage import Storage
from .base.variables import Variables
from .instruction import get_instructions_cls


class InstructionSet:
    produce_cls = DefaultProduce
    filter_set_cls = FilterSet
    value_cls = ProxyValue
    storage_cls = Storage
    variables_cls = Variables
    instructions_cls = get_instructions_cls()

    def __init__(self):
        self.filter_set = self.filter_set_cls()
        self.record_list = []

    def find_by_head(self, key):
        for instruction_cls in self.instructions_cls:
            if instruction_cls.recognize(key):
                return instruction_cls

    def run(self, rules, variables=None, storage=None, derive=None):
        variables = variables or self.variables_cls()
        if derive is not None:
            variables = variables.derive_root(*derive)
        storage = storage or self.storage_cls()
        produces = []
        if isinstance(rules, dict):
            last_v = None
            for k, v in rules.items():
                if v is None:
                    v = last_v
                else:
                    last_v = v
                instruction_cls = self.find_by_head(k)
                instruction_ins = instruction_cls(self, k, v)
                r = instruction_ins.run(variables, storage)
                self.record_list.append(instruction_ins)
                if r is not None:
                    produces.extend(r)
        elif isinstance(rules, list):
            produces.append(self.produce_cls([self.eval_expression(None, rule, variables) for rule in rules]))
        elif isinstance(rules, str):
            produces.append(self.produce_cls(self.eval_expression(None, rules, variables)))
        else:
            produces.append(self.produce_cls(rules))
        return produces

    def eval_expression(self, key, expression, variables):
        if isinstance(expression, str):
            variables.add_item('__k', key)
            value, filters = self.split_expression(expression)
            value = self.calc_value(key, value, variables)
            return self.filter_set.eval(variables.flat(), value, filters)
        else:
            return expression

    def eval_expression_raw(self, expression, variables):
        return self.filter_set.raw_eval(expression, self.filter_set.context | variables.flat())

    @property
    def last_instruction(self):
        return self.record_list[-1] if self.record_list else None

    @staticmethod
    def split_expression(expression):
        vl = str_escape_split(expression, '|')
        vl = [str_escape_custom(x).strip() for x in vl]
        value = vl[0]
        filters = vl[1:]
        return value, filters

    def calc_value(self, key, value, variables):
        x = variables.as_constant(value)
        if x is not None:
            return x
        x = variables.as_eval(value)
        if x is not None:
            return self.eval_expression_raw(x, variables)
        vl = str_escape_split(value, '.')
        vl = [str_escape_custom(x) for x in vl]
        if not vl[0]:
            var = variables.last_key
            keys = vl[1:]
        elif variables.as_var(vl[0]) is not None:
            var = vl[0]
            keys = vl[1:]
        else:
            var = variables.var_root
            keys = vl
        if keys and not keys[-1] and key is not None:
            keys[-1] = key
        return self.value_cls(self.eval_expression_raw(var, variables)).get(*keys)
