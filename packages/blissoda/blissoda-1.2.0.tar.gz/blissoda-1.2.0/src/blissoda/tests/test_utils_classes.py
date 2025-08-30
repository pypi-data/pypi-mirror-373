import functools

import pytest

from ..utils.classes import NoMethodAssignment


def test_assign_staticmethod():
    class Base(NoMethodAssignment):
        @staticmethod
        def base_method():
            return "base"

        @staticmethod
        def method():
            return "base"

    class Inherited(Base):
        @staticmethod
        def method():
            return "inherited"

        @staticmethod
        def new_method():
            return "inherited"

    base_instance = Base()
    with pytest.raises(AttributeError):
        base_instance.method = None
    assert base_instance.method() == "base"

    inherited_instance = Inherited()

    with pytest.raises(AttributeError):
        inherited_instance.base_method = None
    assert inherited_instance.base_method() == "base"

    with pytest.raises(AttributeError):
        inherited_instance.method = None
    assert inherited_instance.method() == "inherited"

    with pytest.raises(AttributeError):
        inherited_instance.new_method = None
    assert inherited_instance.new_method() == "inherited"


def no_decorator(func):
    """No-op function decorator"""
    return func


@pytest.mark.parametrize(
    "decorator",
    [no_decorator, classmethod, functools.lru_cache],
)
def test_assign_method(decorator):
    class Base(NoMethodAssignment):
        @decorator
        def base_method(self):
            return "base"

        @decorator
        def method(self):
            return "base"

    class Inherited(Base):
        @decorator
        def method(self):
            return "inherited"

        @decorator
        def new_method(self):
            return "inherited"

    base_instance = Base()
    with pytest.raises(AttributeError):
        base_instance.method = None
    assert base_instance.method() == "base"

    inherited_instance = Inherited()

    with pytest.raises(AttributeError):
        inherited_instance.base_method = None
    assert inherited_instance.base_method() == "base"

    with pytest.raises(AttributeError):
        inherited_instance.method = None
    assert inherited_instance.method() == "inherited"

    with pytest.raises(AttributeError):
        inherited_instance.new_method = None
    assert inherited_instance.new_method() == "inherited"


class Attribute(NoMethodAssignment):
    def __init__(self):
        self.value = 1

    def method(self):
        return "method"


class ClassAttribute(NoMethodAssignment):
    value = 1

    def method(self):
        return "method"


class Property(NoMethodAssignment):
    def __init__(self):
        self._value = 1

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def method(self):
        return "method"


@pytest.mark.parametrize(
    "cls",
    [Attribute, ClassAttribute, Property],
)
def test_assign(cls):
    instance = cls()

    instance.value = instance.method
    assert instance.value() == "method"

    class Other:
        def method(self):
            return "other"

    other_instance = Other()
    instance.value = other_instance.method
    assert instance.value() == "other"

    def func():
        return "func"

    instance.value = func
    assert instance.value is func

    instance.value = 2
    assert instance.value == 2
