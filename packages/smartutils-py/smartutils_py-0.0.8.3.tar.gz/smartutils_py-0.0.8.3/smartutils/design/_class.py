class classproperty:
    """
    兼容类和实例访问的 classproperty。
    可通过 MyClass.foo 和 MyClass().foo 访问，效果一致。
    """

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, instance, owner):
        return self.fget(owner)


class MyBase:
    @classproperty
    def name(cls):
        return f"[{cls.__name__}]"  # type: ignore

    @classproperty
    def full_name(cls):
        # 限定名，含作用域
        return f"[{cls.__module__}.{cls.__qualname__}]"
