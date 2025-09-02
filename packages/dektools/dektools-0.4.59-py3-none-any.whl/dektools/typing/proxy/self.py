from . import Proxy, T


# Only for static trees
class ProxySelf(Proxy):
    def __new__(cls, _cls_, target: T, share: dict) -> T:
        return super().__new__(cls, target, share)

    def __init__(self, cls, target: T, share: dict) -> None:
        super().__init__(cls, target)
        self.share = share

    @classmethod
    def wrap_share(cls, target: T, share: dict) -> T:
        result = cls(cls, target, share)
        share[id(target)] = result
        return result  # type: ignore

    def me(self, name: str) -> object:
        share = object.__getattribute__(self, "share")
        target = object.__getattribute__(self, "target")
        x = getattr(target, name)
        if isinstance(x, target.__class__):
            return share[id(x)] if id(x) in share else object.__getattribute__(self, "wrap_share")(x, share)
        return x

    def us(self, name: str, typed=None) -> object:
        share = object.__getattribute__(self, "share")
        r = (
            share[id(x)] if id(x) in share else object.__getattribute__(self, "wrap_share")(x, share)
            for x in getattr(object.__getattribute__(self, "target"), name)
        )
        return r if typed is None else typed(r)
