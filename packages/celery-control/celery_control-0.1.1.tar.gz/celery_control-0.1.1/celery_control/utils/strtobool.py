from typing import Any

_true_set = {'yes', 'true', 't', 'y', '1'}
_false_set = {'no', 'false', 'f', 'n', '0'}


def str2bool(value: Any, raise_exc: bool = False) -> bool | None:
    if isinstance(value, str):
        value = value.lower()
        if value in _true_set:
            return True
        if value in _false_set:
            return False

    if raise_exc:
        expected = '", "'.join(_true_set | _false_set)
        raise ValueError('Expected "{expected}"'.format(expected=expected))
    return None


def str2bool_exc(value: str) -> bool:
    return str2bool(value, raise_exc=True)  # type: ignore[return-value]
