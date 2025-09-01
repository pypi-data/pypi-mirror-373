from smartutils.error.sys import LibraryError


class RequireAttrs(type):
    required_attrs = ()

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if not getattr(cls, "__abstractmethods__", None) and getattr(  # noqa
            cls, "required_attrs", ()
        ):
            for attr in cls.required_attrs:
                if not hasattr(cls, attr):
                    raise LibraryError(f"{name} must define class variable '{attr}'.")
        return cls
