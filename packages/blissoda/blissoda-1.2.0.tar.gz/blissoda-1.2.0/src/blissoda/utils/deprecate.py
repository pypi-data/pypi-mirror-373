import logging
from typing import Mapping
from typing import Optional

logger = logging.getLogger(__name__)


def _is_deprecated_attribute_name(obj, attr: str) -> bool:
    return (
        attr != "_DEPRECATED_CLASS_ATTRIBUTES"
        and attr in obj._DEPRECATED_CLASS_ATTRIBUTES
    )


def _get_new_attribute_name(obj, old_name: str) -> str:
    new_name = obj._DEPRECATED_CLASS_ATTRIBUTES[old_name]
    logger.warning(
        f"'{old_name}' is deprecated and will be removed in a future version. Use '{new_name}' instead."
    )
    return new_name


class _Meta(type):
    def __new__(
        meta,
        name,
        bases,
        attrs,
        deprecated_class_attributes: Optional[Mapping[str, str]] = None,
        **kw,
    ):
        newcls = super().__new__(meta, name, bases, attrs, **kw)

        deprecated_class_attributes = deprecated_class_attributes or dict()
        if hasattr(newcls, "_DEPRECATED_CLASS_ATTRIBUTES"):
            newcls._DEPRECATED_CLASS_ATTRIBUTES.update(deprecated_class_attributes)
        else:
            newcls._DEPRECATED_CLASS_ATTRIBUTES = deprecated_class_attributes
        return newcls

    def __setattr__(cls, attr: str, value):
        if _is_deprecated_attribute_name(cls, attr):
            attr = _get_new_attribute_name(cls, attr)
        return super().__setattr__(attr, value)

    def __getattr__(cls, attr: str):
        if _is_deprecated_attribute_name(cls, attr):
            attr = _get_new_attribute_name(cls, attr)
            return getattr(cls, attr)
        raise AttributeError(f"'{cls.__name__}' object has no attribute '{attr}'")


class WithDeprecatedClassAttributes(metaclass=_Meta):

    def __setattr__(self, attr: str, value):
        if _is_deprecated_attribute_name(self, attr):
            attr = _get_new_attribute_name(self, attr)
        return super().__setattr__(attr, value)

    def __getattr__(self, attr: str):
        if _is_deprecated_attribute_name(self, attr):
            attr = _get_new_attribute_name(self, attr)
            return getattr(self, attr)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{attr}'"
        )
