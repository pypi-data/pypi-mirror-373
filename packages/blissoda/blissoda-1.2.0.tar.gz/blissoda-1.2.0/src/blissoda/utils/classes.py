import inspect


class NoMethodAssignment:
    """Class disabling assignments on methods.

    Inherit this class to prevent user's to assign a value to a method name.
    """

    def __setattr__(self, name: str, value):
        existing_attr = getattr(self, name, None)
        existing_class_attr = getattr(self.__class__, name, None)

        if inspect.ismethod(existing_attr) and callable(existing_class_attr):
            if existing_attr.__self__ is self:
                raise AttributeError(
                    f"Cannot set {name} (method): It can be called with ()"
                )
            if existing_attr.__self__ in self.__class__.__mro__:
                raise AttributeError(
                    f"Cannot set {name} (classmethod): It can be called with ()"
                )

        if inspect.isfunction(existing_class_attr):
            raise AttributeError(
                f"Cannot set {name} (staticmethod): It can be called with ()"
            )

        return super().__setattr__(name, value)
