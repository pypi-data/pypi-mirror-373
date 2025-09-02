from ...dict import MapChain


class Variables(MapChain):
    var_prefix = '_'
    var_root = var_prefix + '_'
    var_constant = "/"
    var_eval = '='

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_key = self.var_root

    def set_item(self, key, value):
        self.add_item(key, value)
        self.last_key = key

    def derive_root(self, payload, var=None):
        data = {self.var_root: payload}
        if var:
            data.update(var)
        return self.derive(data=data)

    @classmethod
    def as_var(cls, key):
        if key.startswith(cls.var_prefix):
            return key

    @classmethod
    def as_constant(cls, value):
        if value.startswith(cls.var_constant):
            return value[len(cls.var_constant):]

    @classmethod
    def as_eval(cls, value):
        if value.startswith(cls.var_eval):
            return value[len(cls.var_eval):]

    @property
    def payload(self):
        return self.get_item(self.var_root)
