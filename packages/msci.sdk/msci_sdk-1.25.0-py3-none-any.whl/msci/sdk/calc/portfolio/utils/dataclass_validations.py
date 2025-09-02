import typing
import sys
from typing import Any
from typing import Optional
from typing import Dict

GlobalNS_T = Dict[str, Any]


class TypeValidationError(Exception):
    """Exception raised on type validation errors.
    """
    pass

class BaseDataClassValidator:


    def dataclass_type_validator(self):
        """Dataclass decorator to automatically add validation to a dataclass.

        So you don't have to add a __post_init__ method, or if you have one, you don't have
        to remember to add the dataclass_type_validator(self) call to it; just decorate your
        dataclass with this instead.

        """
        globalns = sys.modules[self.__module__].__dict__.copy()

        errors = {}
        for field_name, field_def in self.__dataclass_fields__.items():
            expected_type = field_def.type
            value = getattr(self, field_name)

            err = self._validate_types(expected_type=expected_type, value=value, globalns=globalns)
            if err is not None:
                errors[self.__class__.__name__] = {}
                errors[self.__class__.__name__][field_name] = err

        if len(errors) > 0:
            raise TypeValidationError(f"Dataclass Type Validation Errors : {errors}")

    def _validate_type(self, expected_type: type, value: Any, type_iter=None) -> Optional[str]:
        if not isinstance(value, expected_type):
            if type_iter:
                return f'must be an instance of {type_iter}[{expected_type}], but received {type_iter}[{type(value)}]'
            return f'must be an instance of {expected_type}, but received {type(value)}'

    def _validate_iterable_items(self, expected_type: type, value: Any, globalns: GlobalNS_T, type_iter = None) -> Optional[str]:
        expected_item_type = expected_type.__args__[0]
        errors = [self._validate_types(expected_type=expected_item_type, value=v, globalns=globalns, type_iter=type_iter)
                  for v in value]
        errors = [x for x in errors if x]
        if len(errors) > 0:
            return f'{errors}'

    def _validate_typing_list(self, expected_type: type, value: Any, globalns: GlobalNS_T) -> Optional[str]:
        if not isinstance(value, list):
            return f'must be an instance of list, but received {type(value)}'
        return self._validate_iterable_items(expected_type, value, globalns, type_iter='List')


    def _validate_typing_tuple(self, expected_type: type, value: Any, globalns: GlobalNS_T) -> Optional[str]:
        if not isinstance(value, tuple):
            return f'must be an instance of tuple, but received {type(value)}'
        return self._validate_iterable_items(expected_type, value, globalns, type_iter='Tuple')


    def _validate_typing_dict(self, expected_type: type, value: Any, globalns: GlobalNS_T) -> Optional[str]:
        if not isinstance(value, dict):
            return f'must be an instance of dict, but received {type(value)}'

        expected_key_type = expected_type.__args__[0]
        expected_value_type = expected_type.__args__[1]

        key_errors = [self._validate_types(expected_type=expected_key_type, value=k, globalns=globalns)
                      for k in value.keys()]
        key_errors = [k for k in key_errors if k]

        val_errors = [self._validate_types(expected_type=expected_value_type, value=v, globalns=globalns)
                      for v in value.values()]
        val_errors = [v for v in val_errors if v]

        if len(key_errors) > 0 and len(val_errors) > 0:
            return f'must be an instance of {expected_type}, but there are some errors in keys and values. key errors: {key_errors}, value errors: {val_errors}'
        elif len(key_errors) > 0:
            return f'must be an instance of {expected_type}, but there are some errors in keys: {key_errors}'
        elif len(val_errors) > 0:
            return f'must be an instance of {expected_type}, but there are some errors in values: {val_errors}'

    def _validate_typing_callable(self, expected_type: type, value: Any, globalns: GlobalNS_T) -> Optional[str]:
        if not isinstance(value, type(lambda a: a)):
            return f'must be an instance of {expected_type._name}, but received {type(value)}'

    def _validate_typing_literal(self, expected_type: type, value: Any,) -> Optional[str]:
        if value not in expected_type.__args__:
            return f'must be one of [{", ".join(expected_type.__args__)}] but received {value}'

    def _evaluate_forward_reference(self, ref_type: typing.ForwardRef, globalns: GlobalNS_T):
        """ Support evaluating ForwardRef types on both Python 3.8 and 3.9. """
        if sys.version_info < (3, 9):
            return ref_type._evaluate(globalns, None)
        return ref_type._evaluate(globalns, None, set())

    validate_typing_mappings = {
        'List': _validate_typing_list,
        'Tuple': _validate_typing_tuple,
        'Dict': _validate_typing_dict,
        'Callable': _validate_typing_callable,
    }


    def _validate_sequential_types(self, expected_type: type, value: Any, globalns: GlobalNS_T) -> Optional[str]:
        validate_func = self.validate_typing_mappings.get(expected_type._name)
        if validate_func is not None:
            return validate_func(self, expected_type, value, globalns)

        if str(expected_type).startswith('typing.Literal'):
            return self._validate_typing_literal(expected_type, value)

        if str(expected_type).startswith('typing.Union') or str(expected_type).startswith('typing.Optional'):
            is_valid = any(self._validate_types(expected_type=t, value=value,  globalns=globalns) is None
                           for t in expected_type.__args__)
            if not is_valid:
                return f'must be an instance of {expected_type}, but received {type(value)}'
            return


    def _validate_types(self, expected_type: type, value: Any, globalns: GlobalNS_T, type_iter=None) -> Optional[str]:
        if isinstance(expected_type, type):
            return self._validate_type(expected_type=expected_type, value=value, type_iter=type_iter)

        if isinstance(expected_type, typing._GenericAlias):
            return self._validate_sequential_types(expected_type=expected_type, value=value,
                                              globalns=globalns)

        if isinstance(expected_type, typing.ForwardRef):
            referenced_type = self._evaluate_forward_reference(expected_type, globalns)
            return self._validate_type(expected_type=referenced_type, value=value)


    def __post_init__(self):
        self.dataclass_type_validator()


