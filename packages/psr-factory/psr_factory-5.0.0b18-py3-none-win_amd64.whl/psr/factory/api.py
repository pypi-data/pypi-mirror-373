# PSR Factory. Copyright (C) PSR, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import locale
from typing import Dict, List, Optional, Tuple, Union
from types import ModuleType
import copy
import ctypes
import datetime as dt
import enum
import numbers
import os
import sys
import threading
import pathlib
import warnings

from . import factorylib


# Check whether pandas' dataframe is available.
_HAS_PANDAS: Optional[bool] = None

# Check whether polars' dataframe is available.
_HAS_POLARS: Optional[bool] = None


pandas: Optional[ModuleType] = None
polars: Optional[ModuleType] = None
numpy: Optional[ModuleType] = None


def _has_pandas() -> bool:
    """Check if pandas is available."""
    global _HAS_PANDAS
    global pandas
    global numpy
    if _HAS_PANDAS is None:
        try:
            import pandas
            import pandas.api.interchange
            import pandas.api.types
            if numpy is not None:
                import numpy
            import numpy.ctypeslib
            _HAS_PANDAS = True
        except ImportError:
            _HAS_PANDAS = False
    return _HAS_PANDAS


def _has_polars() -> bool:
    """Check if polars is available."""
    global _HAS_POLARS
    global polars
    global numpy
    if _HAS_POLARS is None:
        try:
            import polars
            import polars.datatypes.classes
            if numpy is not None:
                import numpy
            import numpy.ctypeslib
            _HAS_POLARS = True
        except ImportError:
            _HAS_POLARS = False
    return _HAS_POLARS


# States whether the library is initialized.
# It should be to correctly load and build models.
_initialized = False
_initialized_lock = threading.Lock()

_loaded = False
_loaded_lock = threading.Lock()

# System encoding for interface with the library.
_preferred_encoding = locale.getpreferredencoding()

# Internal date epoch
# TODO: make it a library call.
_date_transform = 12622780800


def _check_initialized():
    """Checks if the module was initialized."""
    global _initialized
    if not _initialized:
        _initialize()
    return _initialized


def _check_loaded() -> bool:
    """Checks if the library was loaded."""
    global _loaded
    if not _loaded:
        _load_library()
    return _loaded


def _c_str(value: str) -> bytes:
    """Convert a Python object/string into a bytes/c-array."""
    return bytes(value, encoding=_preferred_encoding)


def _from_c_str(value: bytes) -> str:
    """Convert ASCII bytes back into utf-8 strings."""
    return value.decode(encoding=_preferred_encoding)


def _bytes(value: str) -> int:
    """Return the bytes' count of the equivalent C buffer to
    hold this string."""
    return len(value) + 1


class FactoryException(Exception):
    pass


class LogLevel(enum.Enum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class ValueType(enum.Enum):
    INT32 = 0
    INT64 = 1
    FLOAT32 = 2
    FLOAT64 = 3
    BOOL = 4
    STRING = 5
    DATE = 6
    OBJECT = 7
    LIST = 8
    DICT = 9
    NULL = 10


def _version_long() -> str:
    _check_loaded()
    size = 200
    buffer = ctypes.create_string_buffer(size)
    status = factorylib.lib.psrd_version_long(buffer, size)
    if status == 0:
        return _from_c_str(buffer.value)
    return ""


def _version_short() -> str:
    _check_loaded()
    size = 200
    buffer = ctypes.create_string_buffer(size)
    status = factorylib.lib.psrd_version_short(buffer, size)
    if status == 0:
        return _from_c_str(buffer.value)
    return ""


def version() -> str:
    """Returns module version."""
    return _version_long()


def build_version() -> str:
    """Returns short library version."""
    return _version_short()


def get_log_level() -> LogLevel:
    """Get log level."""
    _check_loaded()
    log_level = ctypes.c_int()
    code = factorylib.lib.psrd_get_log_level(ctypes.byref(log_level))
    if code != 0:
        raise FactoryException("Error getting log level")
    return LogLevel(log_level.value)


def set_log_level(log_level: LogLevel):
    """Set log level."""
    if not isinstance(log_level, LogLevel):
        raise TypeError("log_level must be an instance of LogLevel")
    _check_loaded()
    as_int = log_level.value
    code = factorylib.lib.psrd_set_log_level(as_int)
    if code != 0:
        raise FactoryException("Error setting log level")


def get_log_file_path() -> str:
    """Get log file path."""
    _check_loaded()
    error = Error()
    size = 1000
    buffer = ctypes.create_string_buffer(size)
    code = factorylib.lib.psrd_get_log_file_path(buffer, size, error.handler())
    if code != 0:
        raise FactoryException("Error getting log file path")
    return _from_c_str(buffer.value)


def set_debug_mode(value: Union[bool, int]):
    warnings.warn(DeprecationWarning("set_debug_mode is deprecated, use set_diagnostics_mode instead."))
    set_diagnostics_mode(value)


def set_diagnostics_mode(value: Union[bool, int]):
    """Set debug mode."""
    _check_loaded()
    if isinstance(value, bool):
        value = 1 if value else 0
    code = factorylib.lib.psrd_set_diagnostics_mode(value)
    if code != 0:
        raise FactoryException("Error setting diagnostics mode")


def diagnostics() -> str:
    global _initialized
    global _initialized_lock
    with _initialized_lock:
        """Get diagnostics information."""
        py_diagnostics = f"Python version: {sys.version}\n" \
                            f"Python encoding: {sys.getdefaultencoding()}\n" \
                            f"Python locale: {locale.getlocale()}\n" \
                            f"Operating system: {sys.platform}\n" \
                            f"Operating system encoding: {locale.getpreferredencoding()}\n" \
                            f"Module path: {os.path.abspath(os.path.dirname(__file__))}\n" \
                            f"Working directory: {os.getcwd()}\n"

        _check_loaded()
        error = Error()
        size = 10000
        buffer = ctypes.create_string_buffer(size)
        module_path = os.path.dirname(__file__)
        factorylib.lib.psrd_diagnostics(_c_str(module_path), _bytes(module_path),
                                        buffer, size, error.handler())
        if error.code != 0:
            raise FactoryException(error.what)
        _initialized = True
        return py_diagnostics + _from_c_str(buffer.value)


def get_setting(key: str) -> Union[str, int, float, bool]:
    global _initialized
    global _initialized_lock
    with _initialized_lock:
        _check_loaded()
        error = Error()
        value = Value()
        factorylib.lib.psrd_get_global_setting(_c_str(key),
                                               _bytes(key),
                                               value.handler(),
                                               error.handler())
        if error.code != 0:
            raise FactoryException(error.what)
        return value.get()


def set_setting(key: str, value: Union[str, int, float, bool]):
    global _initialized
    global _initialized_lock
    with _initialized_lock:
        _check_loaded()
        error = Error()
        _value = Value()
        _value.set(value)
        factorylib.lib.psrd_set_global_setting(_c_str(key),
                                               _bytes(key),
                                               _value.handler(),
                                               error.handler())
        if error.code != 0:
            raise FactoryException(error.what)



def _get_context(models_or_context: Union[str, list, dict, "Context", None],
                 blocks: Optional[int] = None) -> "Value":
    value = Value()
    if isinstance(models_or_context, (Context, dict)):
        context = models_or_context
    elif isinstance(models_or_context, (str, list)) or models_or_context is None:
        context = dict()
        if isinstance(models_or_context, list):
            context["Models"] = models_or_context
        elif isinstance(models_or_context, str):
            context["Models"] = [models_or_context, ]
    else:
        raise TypeError("Unexpected type for profile_or_context argument.")
    if blocks is not None and isinstance(blocks, int):
        if isinstance(blocks, Context):
            context.set("Blocks", blocks)
        else:
            context["Blocks"] = blocks
    value.set(context)
    return value

def _get_arg_object(arg: Union[dict, "Value", "DataObject", None]) -> "Value":
    if isinstance(arg, dict):
        value = Value()
        value.set(arg)
        return value
    elif isinstance(arg, Value):
        return arg
    elif isinstance(arg, DataObject):
        value = Value()
        value.set(arg)
        return value
    elif arg is None:
        return Value()
    else:
        raise TypeError("Unexpected type for argument.")



class _BaseObject:
    def __init__(self):
        self._hdr = None

    def handler(self):
        return self._hdr

    def __hash__(self):
        return self._hdr


class Error(_BaseObject):
    def __init__(self):
        super().__init__()
        self._hdr = factorylib.lib.psrd_new_error()

    @property
    def code(self) -> int:
        return factorylib.lib.psrd_error_code(self._hdr)

    @code.setter
    def code(self, value):
        raise AttributeError("do not set code")

    @code.deleter
    def code(self):
        raise AttributeError("do not delete code")

    @property
    def what(self) -> str:
        size = factorylib.lib.psrd_error_message(self._hdr, None, 0)
        if size <= 0:
            size = 800
        buffer = ctypes.create_string_buffer(size)
        status = factorylib.lib.psrd_error_message(self._hdr,
                                                   buffer, size)
        if status == 0:
            return _from_c_str(buffer.value)
        return ""

    @what.deleter
    def what(self):
        raise AttributeError("do not delete what")

    @what.setter
    def what(self, value):
        raise AttributeError("do not set what")

    def __del__(self):
        if self._hdr is not None:
            factorylib.lib.psrd_free_error(self._hdr)

    def __repr__(self):
        return f"Error object with code \"{self.code}\" and message:\n" \
               f"{self.what}"

    def __str__(self):
        return self.what


class _TableColumn:
    def __init__(self):
        self.name = ""
        # values: a pure Python list or a ctypes array
        self.values: Union[list, ctypes.c_int, ctypes.c_long, ctypes.c_float, ctypes.c_double] = []

    def __len__(self):
        return len(self.values)


class ValueList(_BaseObject):
    def __init__(self, initialized=True):
        super().__init__()
        self._hdr = factorylib.lib.psrd_new_list() if initialized else None

    def __del__(self):
        if self._hdr is not None:
            factorylib.lib.psrd_free_list(self._hdr)

    @staticmethod
    def from_list(value: Union[List, Tuple]):
        _err = Error()
        list_obj = ValueList()
        for obj in value:
            val_obj = Value()
            val_obj.set(obj)
            factorylib.lib.psrd_list_append(list_obj.handler(),
                                            val_obj.handler(),
                                            _err.handler())
            if _err.code != 0:
                FactoryException(_err.what)
        return list_obj

    def to_list(self) -> list:
        _err = Error()
        count_value = ctypes.c_long()
        factorylib.lib.psrd_list_count(self._hdr,
                                       ctypes.byref(count_value),
                                       _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        values_count = int(count_value.value)

        list_of_values = []
        _value = Value()
        for i_value in range(values_count):
            factorylib.lib.psrd_list_get(self._hdr, i_value,
                                         _value.handler(), _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)
            list_of_values.append(_value.get())
        return list_of_values


class ValueDict(_BaseObject):
    def __init__(self, initialized=True):
        super().__init__()
        self._hdr = factorylib.lib.psrd_new_dict() if initialized else None

    def __del__(self):
        if self._hdr is not None:
            factorylib.lib.psrd_free_dict(self._hdr)

    def __getitem__(self, key: Union["Value", bool, int, float, dt.datetime, str, "DataObject", list, dict, None]) -> Union["Value", bool, int, float, dt.datetime, str, "DataObject", list, dict, None]:
        if not isinstance(key, Value):
            old_key = key
            key = Value()
            key.set(old_key)
        error = Error()
        value = Value()
        factorylib.lib.psrd_dict_get_by_key(self._hdr,
                                            key.handler(),
                                            value.handler(),
                                            error.handler())
        if error.code != 0:
            raise FactoryException(error.what)
        return value.get()

    def __contains__(self, key: Union["Value", bool, int, float, dt.datetime, str, "DataObject", list, dict, None]) -> bool:
        if not isinstance(key, Value):
            old_key = key
            key = Value()
            key.set(old_key)
        error = Error()
        value = Value()
        factorylib.lib.psrd_dict_get_by_key(self._hdr,
                                            key.handler(),
                                            value.handler(),
                                            error.handler())
        return error.code == 0

    def __len__(self) -> int:
        error = Error()
        count_value = ctypes.c_long()
        factorylib.lib.psrd_dict_count(self._hdr,
                                       ctypes.byref(count_value),
                                       error.handler())
        if error.code != 0:
            raise FactoryException(error.what)
        return int(count_value.value)

    class KeyIterator:
        def __init__(self, dict_obj: "ValueDict"):
            self.dict_obj = dict_obj
            self.error = Error()
            self.key = Value()
            self.index = 0

        def __iter__(self):
            return self

        def __next__(self) -> "Value":
            if self.index >= self.dict_obj.__len__():
                raise StopIteration
            factorylib.lib.psrd_dict_get_key_by_index(self.dict_obj._hdr, self.index,
                                                      self.key.handler(),
                                                      self.error.handler())
            if self.error.code != 0:
                raise FactoryException(self.error.what)
            self.index += 1
            return self.key.get()

    def keys(self) -> KeyIterator:
        return self.KeyIterator(self)

    class ValueIterator:
        def __init__(self, dict_obj: "ValueDict"):
            self.dict_obj = dict_obj
            self.error = Error()
            self.value = Value()
            self.index = 0

        def __iter__(self):
            return self

        def __next__(self) -> "Value":
            if self.index >= self.dict_obj.__len__():
                raise StopIteration
            factorylib.lib.psrd_dict_get_value_by_index(self.dict_obj._hdr, self.index,
                                                        self.value.handler(),
                                                        self.error.handler())
            if self.error.code != 0:
                raise FactoryException(self.error.what)
            self.index += 1
            return self.value.get()

    def values(self) -> ValueIterator:
        return self.ValueIterator(self)

    class ItemIterator:
        def __init__(self, dict_obj: "ValueDict"):
            self.dict_obj = dict_obj
            self.error = Error()
            self.key = Value()
            self.value = Value()
            self.index = 0

        def __iter__(self):
            return self

        def __next__(self) -> Tuple["Value", "Value"]:
            if self.index >= self.dict_obj.__len__():
                raise StopIteration
            factorylib.lib.psrd_dict_get_by_index(self.dict_obj._hdr, self.index,
                                         self.key.handler(),
                                         self.value.handler(),
                                         self.error.handler())
            if self.error.code != 0:
                raise FactoryException(self.error.what)
            self.index += 1
            return self.key.get(), self.value.get()

    def items(self) -> ItemIterator:
        return self.ItemIterator(self)

    def clear(self):
        error = Error()
        factorylib.lib.psrd_dict_clear(self._hdr, error.handler())
        if error.code != 0:
            raise FactoryException(error.what)


    @staticmethod
    def from_dict(dict_value: dict):
        error = Error()
        dict_obj = ValueDict()
        key_obj = Value()
        val_obj = Value()
        for key, value in dict_value.items():
            key_obj.set(key)
            val_obj.set(value)
            factorylib.lib.psrd_dict_set(dict_obj.handler(),
                                         key_obj.handler(),
                                         val_obj.handler(),
                                         error.handler())
            if error.code != 0:
                FactoryException(error.what)
        return dict_obj

    def to_dict(self) -> dict:
        """Converts Factory dictionary to Python's"""
        error = Error()
        count_value: Union[ctypes.c_long, int] = ctypes.c_long()
        factorylib.lib.psrd_dict_count(self._hdr,
                                       ctypes.byref(count_value),
                                       error.handler())
        if error.code != 0:
            raise FactoryException(error.what)
        count_value = int(count_value.value)

        read_dict = dict()
        key = Value()
        value = Value()
        for i_value in range(count_value):
            factorylib.lib.psrd_dict_get_by_index(self._hdr, i_value,
                                                  key.handler(),
                                                  value.handler(),
                                                  error.handler())
            if error.code != 0:
                raise FactoryException(error.what)
            read_dict[key.get()] = value.get()
        return read_dict


class Value(_BaseObject):
    def __init__(self):
        super().__init__()
        _check_loaded()
        self._hdr = factorylib.lib.psrd_new_value()

    def __del__(self):
        if self._hdr is not None:
            factorylib.lib.psrd_free_value(self._hdr)

    def get(self) -> Union[bool, int, float, dt.datetime, str, "DataObject", list, dict, None]:
        _err = Error()
        uint_value = ctypes.c_long()
        factorylib.lib.psrd_value_get_type(self._hdr,
                                           ctypes.byref(uint_value),
                                           _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        var_type = int(uint_value.value)
        if var_type == ValueType.INT32.value:
            int_value = ctypes.c_int()
            factorylib.lib.psrd_value_get_int32(self._hdr,
                                                ctypes.byref(int_value),
                                                _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)
            return int(int_value.value)
        elif var_type == ValueType.INT64.value:
            long_value = ctypes.c_long()
            factorylib.lib.psrd_value_get_int64(self._hdr,
                                                ctypes.byref(long_value),
                                                _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)
            return int(int_value.value)
        elif var_type == ValueType.FLOAT32.value:
            float_value = ctypes.c_float()
            factorylib.lib.psrd_value_get_float32(self._hdr,
                                                  ctypes.byref(float_value),
                                                  _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)
            return float(float_value.value)
        elif var_type == ValueType.FLOAT64.value:
            float_value = ctypes.c_double()
            factorylib.lib.psrd_value_get_float64(self._hdr,
                                                  ctypes.byref(float_value),
                                                  _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)
            return float(float_value.value)
        elif var_type == ValueType.STRING.value:
            size = factorylib.lib.psrd_value_get_string(self._hdr, None, 0,
                                                        _err.handler())
            buffer = ctypes.create_string_buffer(size)
            factorylib.lib.psrd_value_get_string(self._hdr, buffer, size,
                                                 _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)
            return _from_c_str(buffer.value)
        elif var_type == ValueType.DATE.value:
            date_value = ctypes.c_longlong()
            factorylib.lib.psrd_value_get_date(self._hdr,
                                               ctypes.byref(date_value),
                                               _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)

            return dt.datetime.fromtimestamp(date_value.value - _date_transform, dt.timezone.utc)

        elif var_type == ValueType.BOOL.value:
            # read bool as int first
            bool_value = ctypes.c_bool()
            factorylib.lib.psrd_value_get_bool(self._hdr,
                                              ctypes.byref(bool_value),
                                              _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)
            return bool(bool_value.value)
        elif var_type == ValueType.NULL.value:
            # Null type
            return None
        elif var_type == ValueType.OBJECT.value:
            obj = DataObject()
            ref = factorylib.lib.psrd_value_get_object(self._hdr,
                                                       _err.handler())
            if _err.code != 0 or ref is None:
                raise FactoryException(_err.what)
            obj._hdr = ref
            return obj
        elif var_type == ValueType.LIST.value:
            dict_obj = ValueList()
            ref = factorylib.lib.psrd_value_get_list(self._hdr,
                                                     _err.handler())
            if _err.code != 0 or ref is None:
                raise FactoryException(_err.what)
            dict_obj._hdr = ref
            return dict_obj.to_list()
        elif var_type == ValueType.DICT.value:
            dict_obj = ValueDict()
            ref = factorylib.lib.psrd_value_get_dict(self._hdr,
                                                     _err.handler())
            if _err.code != 0 or ref is None:
                raise FactoryException(_err.what)
            dict_obj._hdr = ref
            return dict_obj.to_dict()
        else:
            raise NotImplementedError()

    def set(self, value: Union[bool, int, float, dt.datetime, str, "DataObject", list, dict, None]):
        _err = Error()
        if isinstance(value, bool):
            factorylib.lib.psrd_value_set_bool(self._hdr, value,
                                               _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)
        elif isinstance(value, dt.datetime):
            value.replace(tzinfo=dt.timezone.utc)
            date_epoch = int(value.timestamp()) + _date_transform
            factorylib.lib.psrd_value_set_date(self._hdr, date_epoch,
                                               _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)
        # TODO: individual test for int32 and int64
        elif isinstance(value, numbers.Integral):
            factorylib.lib.psrd_value_set_int32(self._hdr, value,
                                                _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)

        # TODO: individual test for float32 and float64
        elif isinstance(value, numbers.Real):
            factorylib.lib.psrd_value_set_float64(self._hdr, value,
                                                  _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)

        elif isinstance(value, str):
            factorylib.lib.psrd_value_set_string(self._hdr,
                                                 _c_str(value),
                                                 _bytes(value),
                                                 _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)

        elif isinstance(value, DataObject):
            factorylib.lib.psrd_value_set_object(self._hdr,
                                                 value.handler(),
                                                 _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)

        elif isinstance(value, (list, tuple, ValueList)):
            if isinstance(value, (list, tuple)):
                dict_obj = ValueList.from_list(value)
            else:
                dict_obj = value
            factorylib.lib.psrd_value_set_list(self._hdr,
                                               dict_obj.handler(),
                                               _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)

        elif isinstance(value, dict):
            dict_obj = ValueDict.from_dict(value)
            factorylib.lib.psrd_value_set_dict(self._hdr,
                                               dict_obj.handler(),
                                               _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)

        elif isinstance(value, Study):
            raise FactoryException("Study object cannot be set as value.")

        elif value is None:
            factorylib.lib.psrd_value_set_null(self._hdr,
                                               _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)

        else:
            raise FactoryException(f"Unsupported type \"{type(value).name}\" for value.")


class PropertyDescription(_BaseObject):
    def __init__(self):
        super().__init__()
        self._hdr = None

    def __del__(self):
        if self._hdr is not None:
            factorylib.lib.psrd_free_property_description(self._hdr)

    @property
    def name(self) -> str:
        _err = Error()
        # TODO: determine size automatically
        size = 300
        buffer = ctypes.create_string_buffer(size)
        factorylib.lib.psrd_property_description_get_name(self._hdr, buffer, size,
                                                          _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return _from_c_str(buffer.value)

    @name.setter
    def name(self, value):
        raise AttributeError("do not set name")

    @name.deleter
    def name(self):
        raise AttributeError("do not delete name")

    @property
    def alt_name(self) -> str:
        _err = Error()
        # TODO: determine size automatically
        size = 300
        buffer = ctypes.create_string_buffer(size)
        factorylib.lib.psrd_property_description_get_alternative_name(
            self._hdr, buffer, size, _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return _from_c_str(buffer.value)

    @alt_name.setter
    def alt_name(self, value):
        raise AttributeError("do not set alt_name")

    @alt_name.deleter
    def alt_name(self):
        raise AttributeError("do not delete alt_name")

    def is_dynamic(self) -> bool:
        _err = Error()
        value = ctypes.c_bool()
        factorylib.lib.psrd_property_description_is_dynamic(self._hdr,
                                                            ctypes.byref(value),
                                                            _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return bool(value.value)

    def is_indexed(self) -> bool:
        _err = Error()
        value = ctypes.c_bool()
        factorylib.lib.psrd_property_description_is_indexed(self._hdr,
                                                            ctypes.byref(value),
                                                            _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return bool(value.value)

    def is_grouped(self) -> bool:
        _err = Error()
        value = ctypes.c_bool()
        factorylib.lib.psrd_property_description_is_grouped(self._hdr,
                                                            ctypes.byref(value),
                                                            _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return bool(value.value)

    def grouped_with(self) -> List[str]:
        _err = Error()
        _list_obj = ValueList()
        ref = factorylib.lib.psrd_property_description_grouped_with(self._hdr,
                                                                    _err.handler())
        if _err.code != 0 or ref is None:
            raise FactoryException(_err.what)
        _list_obj._hdr = ref
        return _list_obj.to_list()

    def dimensions(self) -> Dict[str, int]:
        _err = Error()
        dimensions = {}
        value = ctypes.c_long()
        factorylib.lib.psrd_property_description_dimensions_count(self._hdr,
                                                                  ctypes.byref(value),
                                                                  _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        dimensions_count = int(value.value)

        for i_dim in range(dimensions_count):
            # TODO: get size automatically
            size = 100
            buffer = ctypes.create_string_buffer(size)
            factorylib.lib.psrd_property_description_get_dimension_name(self._hdr,
                                                                        i_dim, buffer,
                                                                        size,
                                                                        _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)
            name = _from_c_str(buffer.value)

            factorylib.lib.psrd_property_description_get_dimension_size(self._hdr,
                                                                        i_dim,
                                                                        ctypes.byref(value),
                                                                        _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)
            size = int(value.value)

            dimensions[name] = size
        return dimensions

    def type(self) -> ValueType:
        _err = Error()
        value = ctypes.c_long()
        factorylib.lib.psrd_property_description_get_type(self._hdr,
                                                          ctypes.byref(value),
                                                          _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return ValueType(value.value)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        dimensions = self.dimensions()
        if len(dimensions) == 0:
            return f"Property {self.name}"
        else:
            return f"Property {self.name} with dimensions {self.dimensions()}"



class DataObject(_BaseObject):
    def __init__(self):
        super().__init__()
        self._hdr = None

    def __del__(self):
        if self._hdr is not None:
            factorylib.lib.psrd_free_object(self._hdr)

    def __eq__(self, other):
        if not isinstance(other, DataObject):
            return False
        _err = Error()
        value = ctypes.c_bool()
        if self._hdr == other.handler():
            return True
        factorylib.lib.psrd_object_is_equals_to(self._hdr,
                                                other.handler(),
                                                ctypes.byref(value),
                                                _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return bool(value.value)

    def __hash__(self):
        _err = Error()
        handler = factorylib.lib.psrd_object_get_handler(self._hdr, _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return handler

    def __copy__(self):
        dest = DataObject()
        _err = Error()
        ref = factorylib.lib.psrd_object_clone(self.handler(),
                                               _err.handler())
        if _err.code != 0 or ref is None:
            raise FactoryException(_err.what)
        dest._hdr = ref
        return dest

    def __deepcopy__(self, memodict=None):
        raise NotImplementedError()

    def __repr__(self):
        identifiers = []
        if self.code != 0:
            identifiers.append(f"code={self.code}")
        if self.id != "":
            identifiers.append(f"id={self.id.strip()}")
        if self.name != "":
            identifiers.append(f"name={self.name.strip()}")
        return f"psr.factory.DataObject({self.type}, {', '.join(identifiers)})"

    def help(self) -> str:
        return help(self.type)

    def clone(self) -> "DataObject":
        return copy.copy(self)

    @property
    def context(self) -> "Context":
        _check_initialized()
        obj = Context()
        _err = Error()
        ref = factorylib.lib.psrd_object_context(self._hdr,
                                                 _err.handler())
        if _err.code != 0 or ref is None:
            raise FactoryException(_err.what)
        obj._hdr = ref
        return obj

    def properties(self) -> Dict[str, PropertyDescription]:
        _err = Error()
        value = ctypes.c_long()
        factorylib.lib.psrd_object_property_description_count(self._hdr,
                                                              ctypes.byref(value),
                                                              _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        var_count = int(value.value)
        properties = {}
        for i_var in range(var_count):
            var = PropertyDescription()
            ref = factorylib.lib.psrd_object_get_property_description(self._hdr,
                                                                      i_var,
                                                                      _err.handler())
            if _err.code != 0 or ref is None:
                raise FactoryException(_err.what)
            var._hdr = ref
            properties[var.name] = var
        return properties

    def get(self, expression: str) -> Union[int, float, dt.datetime, str, "DataObject", list, None]:
        value = Value()
        _err = Error()
        factorylib.lib.psrd_object_get_value(self._hdr,
                                             _c_str(expression),
                                             value.handler(),
                                             _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return value.get()

    def get_at(self, expression: str, range_expr: Union[str, dt.datetime]) -> Union[int, float, dt.datetime, str, "DataObject", list, None]:
        if not isinstance(range_expr, (str, dt.datetime)):
            raise FactoryException("range_expr must be a string or datetime object.")
        _value = Value()
        _err = Error()
        _range = Value()
        _range.set(range_expr)
        factorylib.lib.psrd_object_get_value_at(self._hdr,
                                                _c_str(expression),
                                                _range.handler(),
                                                _value.handler(),
                                                _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return _value.get()

    def as_dict(self) -> Dict[str, any]:
        value_dict = ValueDict()
        error = Error()
        handler = factorylib.lib.psrd_object_get_as_dict(self._hdr,
                                                         error.handler())
        if error.code != 0 or handler is None:
            raise FactoryException(error.what)
        value_dict._hdr = handler
        return value_dict.to_dict()

    def from_dict(self, input_dict: Dict[str, any]):
        value_dict = ValueDict.from_dict(input_dict)
        error = Error()
        factorylib.lib.psrd_object_set_from_dict(self._hdr, value_dict.handler(),
                                                 error.handler())
        if error.code != 0:
            raise FactoryException(error.what)

    def get_df(self, expression: str) -> "pandas.DataFrame":
        _err = Error()
        _df = DataFrame()
        factorylib.lib.psrd_object_get_table(self._hdr, _df.handler(),
                                             _c_str(expression),
                                             _bytes(expression),
                                             _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        df_builder = _DataFrameBuilder()
        df_builder.build_dataframe(_df)
        return df_builder.build_pandas_dataframe()

    def set(self, expression: str, value):
        _err = Error()
        _val = Value()
        _val.set(value)
        factorylib.lib.psrd_object_set_value(self._hdr, _c_str(expression),
                                             _bytes(expression),
                                             _val.handler(),
                                             _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)

    def set_at(self, expression: str, range_expr: Union[str, dt.datetime], value):
        if not isinstance(range_expr, (str, dt.datetime)):
            raise FactoryException("range_expr must be a string or datetime object.")
        _err = Error()
        _value = Value()
        _value.set(value)
        _range = Value()
        _range.set(range_expr)
        factorylib.lib.psrd_object_set_value_at(self._hdr,
                                                _c_str(expression),
                                                _bytes(expression),
                                                _range.handler(),
                                                _value.handler(),
                                                _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)

    def set_df(self, dataframe_like):
        if not _has_pandas():
            raise ModuleNotFoundError("pandas required.")
        dataframe_like = pandas.api.interchange.from_dataframe(dataframe_like)
        df_builder = _DataFrameBuilder()
        _df = df_builder.build_from_pandas(dataframe_like)
        _err = Error()
        factorylib.lib.psrd_object_set_table(self._hdr, _df.handler(),
                                             _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)


    def clear_values(self, expression: str):
        _err = Error()
        factorylib.lib.psrd_object_clear_values(self._hdr,
                                                _c_str(expression),
                                                _bytes(expression),
                                                _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)

    def parent(self) -> Optional["Study"]:
        study_ptr = Study()
        _err = Error()
        ref = factorylib.lib.psrd_object_get_parent(self._hdr,
                                                    _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        if ref is None:
            return None
        study_ptr._hdr = ref
        return study_ptr

    def referenced_by(self) -> List["DataObject"]:
        object_list = ValueList(False)
        _err = Error()
        ref = factorylib.lib.psrd_object_referenced_by(self._hdr,
                                                       _err.handler())
        if _err.code != 0 or ref is None:
            raise FactoryException(_err.what)
        object_list._hdr = ref
        return object_list.to_list()

    @property
    def code(self) -> int:
        _err = Error()
        value = ctypes.c_int()
        factorylib.lib.psrd_object_get_code(self._hdr,
                                            ctypes.byref(value),
                                            _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return value.value

    @code.setter
    def code(self, value: int):
        _err = Error()
        factorylib.lib.psrd_object_set_code(self._hdr, value,
                                            _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)

    @code.deleter
    def code(self):
        raise AttributeError("do not delete code")

    @property
    def type(self) -> str:
        err = Error()
        size = factorylib.lib.psrd_object_get_type(self._hdr, None,
                                                   0, err.handler())
        if err.code != 0:
            raise FactoryException(err.what)
        buffer = ctypes.create_string_buffer(size)
        factorylib.lib.psrd_object_get_type(self._hdr, buffer,
                                            size, err.handler())
        if err.code != 0:
            raise FactoryException(err.what)
        return _from_c_str(buffer.value)

    @type.setter
    def type(self, value: str):
        raise AttributeError("do not set type")

    @type.deleter
    def type(self):
        raise AttributeError("do not delete type")

    @property
    def name(self) -> str:
        err = Error()
        size = factorylib.lib.psrd_object_get_name(self._hdr, None,
                                                   0, err.handler())
        if err.code != 0:
            raise FactoryException(err.what)
        buffer = ctypes.create_string_buffer(size)
        factorylib.lib.psrd_object_get_name(self._hdr, buffer,
                                            size, err.handler())
        if err.code == 0:
            return _from_c_str(buffer.value)
        raise FactoryException(err.what)

    @name.setter
    def name(self, value: str):
        err = Error()
        factorylib.lib.psrd_object_set_name(self._hdr,
                                            _c_str(value),
                                            _bytes(value),
                                            err.handler())
        if err.code != 0:
            raise FactoryException(err.what)

    @name.deleter
    def name(self):
        raise AttributeError("do not delete name")

    @property
    def id(self) -> str:
        err = Error()
        size = factorylib.lib.psrd_object_get_id(self._hdr, None,
                                                 0, err.handler())
        if err.code != 0:
            raise FactoryException(err.what)
        buffer = ctypes.create_string_buffer(size)
        factorylib.lib.psrd_object_get_id(self._hdr, buffer,
                                          size, err.handler())
        if err.code == 0:
            return _from_c_str(buffer.value)
        raise FactoryException(err.what)

    @id.setter
    def id(self, value: str):
        _err = Error()
        factorylib.lib.psrd_object_set_id(self._hdr,
                                          _c_str(value),
                                          _bytes(value),
                                          _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)

    @id.deleter
    def id(self):
        raise AttributeError("do not delete id")


class Context(DataObject):
    @staticmethod
    def default_context() -> "Context":
        _check_initialized()
        context = Context()
        err = Error()
        ref = factorylib.lib.psrd_get_default_context(err.handler())
        if err.code != 0 or ref is None:
            raise FactoryException(err.what)
        context._hdr = ref
        return context

    @staticmethod
    def create() -> "Context":
        context_obj = create("Context", None)
        context = Context()
        context._hdr = context_obj._hdr
        context_obj._hdr = None
        return context

    def __repr__(self):
        properties = self.as_dict()
        props_str = ', '.join(f"{key}={repr(value)}" for key, value in properties.items())
        return f"psr.factory.Context({props_str})"


class Study(_BaseObject):
    def __init__(self):
        super().__init__()

    def __del__(self):
        if self._hdr is not None:
            factorylib.lib.psrd_free_study(self._hdr)

    def __hash__(self):
        return factorylib.lib.psrd_study_get_handler(self._hdr)

    def __eq__(self, other: "Study"):
        _err = Error()
        value = ctypes.c_bool()
        if self._hdr == other.handler():
            return True
        factorylib.lib.psrd_study_is_equals_to(self._hdr,
                                               other.handler(),
                                               ctypes.byref(value),
                                               _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return bool(value.value)

    def __copy__(self):
        raise NotImplementedError()

    def __deepcopy__(self, memodict=None):
        dest = Study()
        _err = Error()
        ref = factorylib.lib.psrd_study_clone(self.handler(),
                                              _err.handler())
        if _err.code != 0 or ref is None:
            raise FactoryException(_err.what)
        dest._hdr = ref
        return dest

    def create(self, object_type: str) -> DataObject:
        _check_initialized()
        return create(object_type, self.context)


    @staticmethod
    def help():
        return help("Study")

    def clone(self) -> "Study":
        return copy.deepcopy(self)

    @staticmethod
    def create_object(profile_or_context: Union[str, Context, dict, None],
                      blocks: Optional[int] = None):
        _check_initialized()
        err = Error()
        context = _get_context(profile_or_context, blocks)
        study = Study()
        study._hdr = factorylib.lib.psrd_study_create(context.handler(),
                                                      err.handler())
        if err.code != 0:
            raise FactoryException(err.what)
        return study

    @staticmethod
    def load(study_path: Union[str, pathlib.Path], profile_or_context: Union[str, Context, None],
             settings_only: bool = False,
             options: Optional[Union[dict, "Value", "DataObject"]] = None):
        if not isinstance(options, (DataObject, type(None))):
            raise TypeError("options must be a DataObject or None.")
        _check_initialized()
        study_path = str(study_path)
        context = _get_context(profile_or_context, None)
        err = Error()
        options_value = _get_arg_object(options)
        study = Study()
        if not settings_only:
            load_fn = factorylib.lib.psrd_study_load
        else:
            load_fn = factorylib.lib.psrd_study_load_settings
        study._hdr = load_fn(_c_str(study_path), _bytes(study_path),
                             options_value.handler(), context.handler(),
                             err.handler())
        if err.code != 0:
            raise FactoryException(err.what)
        return study

    def save(self, output_path: Union[str, pathlib.Path],
             options: Optional[Union[dict, Value, DataObject]] = None):
        output_path = str(output_path)
        _err = Error()
        options_value = _get_arg_object(options)
        factorylib.lib.psrd_study_save(self._hdr,
                                       _c_str(output_path), _bytes(output_path),
                                       options_value.handler(),
                                       _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)

    def save_settings(self, output_path: Union[str, pathlib.Path],
             options: Optional[Union[dict, Value, DataObject]] = None):
        output_path = str(output_path)
        _err = Error()
        options_value = _get_arg_object(options)
        factorylib.lib.psrd_study_save_settings(self._hdr, _c_str(output_path),
                                                _bytes(output_path),
                                                options_value.handler(),
                                                _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)

    @property
    def context(self) -> "Context":
        _check_initialized()
        obj = Context()
        _err = Error()
        ref = factorylib.lib.psrd_study_context(self._hdr,
                                                _err.handler())
        if _err.code != 0 or ref is None:
            raise FactoryException(_err.what)
        obj._hdr = ref
        return obj

    def get(self, expression: str) -> Union[int, float, dt.datetime, str, "DataObject", list, None]:
        value = Value()
        _err = Error()
        factorylib.lib.psrd_study_get_value(self._hdr,
                                            _c_str(expression),
                                            value.handler(),
                                            _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return value.get()

    def get_at(self, expression: str, range_expr: Union[str, dt.datetime]) -> Union[int, float, dt.datetime, str, "DataObject", list, None]:
        if not isinstance(range_expr, str):
            raise FactoryException("range_expr must be a string or datetime object.")
        _value = Value()
        _err = Error()
        _range = Value()
        _range.set(range_expr)
        factorylib.lib.psrd_study_get_value_at(self._hdr,
                                               _c_str(expression),
                                               _range.handler(),
                                               _value.handler(),
                                               _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return _value.get()

    def as_dict(self) -> Dict[str, any]:
        value_dict = ValueDict()
        error = Error()
        handler = factorylib.lib.psrd_study_get_as_dict(self._hdr,
                                                        error.handler())
        if error.code != 0 or handler is None:
            raise FactoryException(error.what)
        value_dict._hdr = handler
        return value_dict.to_dict()

    def from_dict(self, input_dict: Dict[str, any]):
        value_dict = ValueDict.from_dict(input_dict)
        error = Error()
        factorylib.lib.psrd_study_set_from_dict(self._hdr, value_dict.handler(),
                                                error.handler())
        if error.code != 0:
            raise FactoryException(error.what)

    def add(self, obj: DataObject):
        if not isinstance(obj, DataObject):
            raise TypeError("obj must be a DataObject.")
        _err = Error()
        factorylib.lib.psrd_study_add(self._hdr,
                                      obj.handler(),
                                      _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)

    def remove(self, obj: DataObject):
        if not isinstance(obj, DataObject):
            raise TypeError("obj must be a DataObject.")
        _err = Error()
        factorylib.lib.psrd_study_remove(self._hdr,
                                         obj.handler(),
                                         _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)

    def get_all_objects(self) -> List[DataObject]:
        object_list = ValueList(False)
        error = Error()
        ref = factorylib.lib.psrd_study_get_all_objects(self._hdr,
                                                        error.handler())
        if error.code != 0 or ref is None:
            raise FactoryException(error.what)
        object_list._hdr = ref
        return object_list.to_list()

    def find(self, expression: str) -> List[DataObject]:
        object_list = ValueList(False)
        _err = Error()
        ref = factorylib.lib.psrd_study_find(self._hdr,
                                             _c_str(expression),
                                             _err.handler())
        if _err.code != 0 or ref is None:
            raise FactoryException(_err.what)
        object_list._hdr = ref
        return object_list.to_list()

    def find_by_name(self, type_name: str, name: Optional[str] = None) -> List[DataObject]:
        if name is None:
            warnings.warn(DeprecationWarning("Starting from Factory 4.0.28 "
                                             "the second argument 'name' must be provided.\n"
                                             "Use find_by_name(type_name, name)"))

        type_name, name_str = type_name.split(".", 1)
        name = name_str
        object_list = ValueList(False)
        _err = Error()
        if name.strip() == "":
            name = "*"
        expression = f"{type_name}.{name}"
        ref = factorylib.lib.psrd_study_find(self._hdr,
                                             _c_str(expression),
                                             _err.handler())
        if _err.code != 0 or ref is None:
            raise FactoryException(_err.what)
        object_list._hdr = ref
        return object_list.to_list()

    def find_by_code(self, type_name: str, code: Optional[int] = None) -> List[DataObject]:
        if code is None:
            warnings.warn(DeprecationWarning("Starting from Factory 4.0.9 "
                                             "the second argument 'code' must be provided.\n"
                                             "Use find_by_code(type_name, code)"))

            type_name, code_str = type_name.split(".", 1)
            code = int(code_str)

        object_list = ValueList(False)
        _err = Error()
        ref = factorylib.lib.psrd_study_find_by_code(self._hdr,
                                                     _c_str(type_name),
                                                     code,
                                                     _err.handler())
        if _err.code != 0 or ref is None:
            raise FactoryException(_err.what)
        object_list._hdr = ref
        return object_list.to_list()

    def find_by_id(self, expression: str) -> List[DataObject]:
        object_list = ValueList(False)
        _err = Error()
        ref = factorylib.lib.psrd_study_find_by_id(self._hdr,
                                                   _c_str(expression),
                                                   _err.handler())
        if _err.code != 0 or ref is None:
            raise FactoryException(_err.what)
        object_list._hdr = ref
        return object_list.to_list()

    def set(self, expression: str, value):
        _err = Error()
        _val = Value()
        _val.set(value)
        factorylib.lib.psrd_study_set_value(self._hdr,
                                            _c_str(expression),
                                            _bytes(expression),
                                            _val.handler(),
                                            _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)

    def set_at(self, expression: str, range_expr: Union[str, dt.datetime], value):
        if not isinstance(range_expr, (str, dt.datetime)):
            raise FactoryException("range_expr must be a string or datetime object.")
        _err = Error()
        _value = Value()
        _value.set(value)
        _range = Value()
        _range.set(range_expr)
        factorylib.lib.psrd_study_set_value_at(self._hdr,
                                               _c_str(expression),
                                               _bytes(expression),
                                               _range.handler(),
                                               _value.handler(),
                                               _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)

    def get_df(self, expression: str) -> "pandas.DataFrame":
        _err = Error()
        _df = DataFrame()
        factorylib.lib.psrd_study_get_table(self._hdr, _df.handler(),
                                            _c_str(expression),
                                            _bytes(expression),
                                            _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        df_builder = _DataFrameBuilder()
        df_builder.build_dataframe(_df)
        return df_builder.build_pandas_dataframe()

    def get_objects_values(self, object_type: str, columns: List[str]) -> "pandas.DataFrame":
        _err = Error()
        _table = DataFrame()
        columns_list = Value()
        columns_list.set(columns)
        factorylib.lib.psrd_study_get_objects_values(self._hdr, _table.handler(),
                                                     _c_str(object_type),
                                                     columns_list.handler(),
                                                     _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        df_builder = _DataFrameBuilder()
        df_builder.build_dataframe(_table)
        return df_builder.build_pandas_dataframe()

    def get_objects_values_at(self, object_type: str, columns: List[str], range: Union[str, dt.datetime]) -> "pandas.DataFrame":
        _err = Error()
        _df = DataFrame()
        _range = Value()
        _range.set(range)
        columns_list = Value()
        columns_list.set(columns)
        factorylib.lib.psrd_study_get_objects_values_at(self._hdr, _df.handler(),
                                                        _c_str(object_type),
                                                        columns_list.handler(),
                                                        _range.handler(),
                                                        _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        df_builder = _DataFrameBuilder()
        df_builder.build_dataframe(_df)
        return df_builder.build_pandas_dataframe()

    def properties(self) -> Dict[str, PropertyDescription]:
        _err = Error()
        value = ctypes.c_long()
        factorylib.lib.psrd_study_property_description_count(self._hdr,
                                                             ctypes.byref(value),
                                                             _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        var_count = int(value.value)
        properties = {}
        for i_var in range(var_count):
            var = PropertyDescription()
            ref = factorylib.lib.psrd_study_get_property_description(self._hdr,
                                                                     i_var,
                                                                     _err.handler())
            if _err.code != 0 or ref is None:
                raise FactoryException(_err.what)
            var._hdr = ref
            properties[var.name] = var
        return properties

    def set_df(self, dataframe_like):
        if not _has_pandas():
            raise ModuleNotFoundError("pandas required.")
        dataframe_like = pandas.api.interchange.from_dataframe(dataframe_like)
        df_builder = _DataFrameBuilder()
        _df = df_builder.build_from_pandas(dataframe_like)
        _err = Error()
        factorylib.lib.psrd_study_set_table(self._hdr, _df.handler(),
                                            _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)

    def clear_values(self, expression: str):
        _err = Error()
        factorylib.lib.psrd_study_clear_values(self._hdr,
                                               _c_str(expression),
                                               _bytes(expression),
                                               _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)


def _is_int64(value):
    return isinstance(value, int) or isinstance(value, numpy.int64) or (isinstance(value, numpy.ndarray) and value.dtype == numpy.int64)

def _is_float32(value):
    return isinstance(value, (numpy.float32,)) or (isinstance(value, numpy.ndarray) and value.dtype == numpy.float32)

def _is_float64(value):
    return isinstance(value, (numpy.float64, float)) or (isinstance(value, numpy.ndarray) and value.dtype == numpy.float64)


class _DataFrameBuilder:
    def __init__(self):
        self.indices: List[Optional[_TableColumn]] = []
        self.columns: List[Optional[_TableColumn]] = []
        self.column_names: List[str] = []
        self.index_names: List[str] = []
        self.column_types: List[int] = []
        self.index_types: List[int] = []
        self._not_built = True
        self._value: Optional[Value] = None
        self._err: Optional[Error] = None

    def _pandas_dtype_to_column_type(self, dtype: str) -> int:
        if dtype == "object":
            return 0
        elif dtype == "int32":
            return 1
        elif dtype == "int64":
            return 2
        elif dtype == "float32":
            return 3
        elif dtype == "float64":
            return 4
        elif dtype == "string":
            return 5
        elif dtype == "datetime64[ns]":
            return 6
        else:
            raise FactoryException(f"Unsupported pandas dtype \"{dtype}\".")

    def _polars_dtype_to_column_type(self, dtype: "polars.datatypes.classes.DataTypeClass") -> int:
        if dtype == polars.Int32:
            return 1
        if dtype == polars.Int64:
            return 2
        if dtype == polars.Float64:
            return 3
        if dtype == polars.Float64:
            return 4
        if dtype == polars.String:
            return 5
        else:
            raise FactoryException(f"Unsupported polars dtype \"{dtype}\".")


    def build_dataframe(self, df: "DataFrame"):
        self._err = Error()
        name_buffer_length = 200
        _columns_count = ctypes.c_long()
        factorylib.lib.psrd_table_columns_count(df.handler(),
                                                ctypes.byref(_columns_count),
                                                self._err.handler())
        if self._err.code != 0:
            raise FactoryException(self._err.what)
        columns_count = _columns_count.value

        _rows_count = ctypes.c_long()
        factorylib.lib.psrd_table_rows_count(df.handler(),
                                             ctypes.byref(_rows_count),
                                             self._err.handler())
        if self._err.code != 0:
            raise FactoryException(self._err.what)
        rows_count = _rows_count.value

        _indices_count = ctypes.c_long()
        factorylib.lib.psrd_table_index_count(df.handler(),
                                              ctypes.byref(_indices_count),
                                              self._err.handler())
        if self._err.code != 0:
            raise FactoryException(self._err.what)
        indices_count = _indices_count.value

        value = Value()
        buffer = ctypes.create_string_buffer(name_buffer_length)

        self.indices = [_TableColumn() for _ in range(indices_count)]
        for index in range(indices_count):
            factorylib.lib.psrd_table_index_get_name(df.handler(), index,
                                                     buffer, name_buffer_length,
                                                     self._err.handler())
            if self._err.code != 0:
                raise FactoryException(self._err.what)
            self.indices[index].name = _from_c_str(buffer.value)

            self.indices[index].values = [None] * rows_count
            for i_row in range(0, rows_count):
                factorylib.lib.psrd_table_index_get_value(df.handler(), index,
                                                          i_row, value.handler(),
                                                          self._err.handler())
                if self._err.code != 0:
                    raise FactoryException(self._err.what)
                self.indices[index].values[i_row] = value.get()

        self.columns = [_TableColumn() for _ in range(columns_count)]
        for column in range(columns_count):
            factorylib.lib.psrd_table_column_get_name(df.handler(), column,
                                                      buffer, name_buffer_length,
                                                      self._err.handler())
            if self._err.code != 0:
                raise FactoryException(self._err.what)
            self.columns[column].name = _from_c_str(buffer.value)

            self.columns[column].values = [None] * rows_count
            for row in range(rows_count):
                factorylib.lib.psrd_table_column_get_value(df.handler(),
                                                           column, row,
                                                           value.handler(),
                                                           self._err.handler())
                if self._err.code != 0:
                    raise FactoryException(self._err.what)
                self.columns[column].values[row] = value.get()
        self._not_built = False

    def build_dataframe_of_integral_types(self, df: "DataFrame"):
        self._err = Error()
        name_buffer_length = 200
        _columns_count = ctypes.c_long()
        factorylib.lib.psrd_table_columns_count(df.handler(),
                                                ctypes.byref(_columns_count),
                                                self._err.handler())
        if self._err.code != 0:
            raise FactoryException(self._err.what)
        columns_count = _columns_count.value

        _rows_count = ctypes.c_long()
        factorylib.lib.psrd_table_rows_count(df.handler(),
                                             ctypes.byref(_rows_count),
                                             self._err.handler())
        if self._err.code != 0:
            raise FactoryException(self._err.what)
        rows_count = _rows_count.value

        _indices_count = ctypes.c_long()
        factorylib.lib.psrd_table_index_count(df.handler(),
                                              ctypes.byref(_indices_count),
                                              self._err.handler())
        if self._err.code != 0:
            raise FactoryException(self._err.what)
        indices_count = _indices_count.value

        buffer = ctypes.create_string_buffer(name_buffer_length)

        self.indices = [_TableColumn() for _ in range(indices_count)]
        for index in range(indices_count):
            factorylib.lib.psrd_table_index_get_name(df.handler(), index,
                                                     buffer, name_buffer_length,
                                                     self._err.handler())
            if self._err.code != 0:
                raise FactoryException(self._err.what)
            index_name = _from_c_str(buffer.value)
            self.indices[index].name = index_name
            self.indices[index].values = [None] * rows_count
            if index_name in ("date", "datetime"):
                array_values = (ctypes.c_longlong * rows_count)()
                factorylib.lib.psrd_table_index_get_date_values(df.handler(),
                                                                index,
                                                                array_values,
                                                                self._err.handler())
                if self._err.code != 0:
                    raise FactoryException(self._err.what)
                # convert array values to python datetime
                self.indices[index].values = [dt.datetime.fromtimestamp(value - _date_transform, dt.UTC) for value in array_values]
            else:
                array_values = (ctypes.c_int * rows_count)()
                factorylib.lib.psrd_table_index_get_int32_values(df.handler(),
                                                                 index,
                                                                 array_values,
                                                                 self._err.handler())
                if self._err.code != 0:
                    raise FactoryException(self._err.what)
                self.indices[index].values = array_values

        self.columns = [_TableColumn() for _ in range(columns_count)]
        for column in range(columns_count):
            factorylib.lib.psrd_table_column_get_name(df.handler(), column,
                                                      buffer, name_buffer_length,
                                                      self._err.handler())
            if self._err.code != 0:
                raise FactoryException(self._err.what)
            self.columns[column].name = _from_c_str(buffer.value)

            array_values = (ctypes.c_double * rows_count)()
            factorylib.lib.psrd_table_column_get_float64_values(df.handler(),
                                                                column,
                                                                array_values,
                                                                self._err.handler())
            if self._err.code != 0:
                raise FactoryException(self._err.what)
            self.columns[column].values = array_values
        self._not_built = False

    def build_pandas_dataframe(self, **kwargs) -> "pandas.DataFrame":
        use_object_dtype = kwargs.get("use_object_dtype", True)
        if not _has_pandas():
            raise ModuleNotFoundError("pandas required.")
        def convert_column_values(values):
            if isinstance(values, list):
                return values
            # Looks like ctype array, smells like ctype array
            if hasattr(values, "_length_") and hasattr(values, "_type_"):
                return numpy.ctypeslib.as_array(values)
            return values

        data = {column.name: convert_column_values(column.values)
                for column in self.columns}
        if len(self.indices) > 1:
            # TODO: store index as rows of tuples
            index = pandas.MultiIndex.from_tuples(
                [tuple(self.indices[i].values[row] for i in range(len(self.indices))) for row in range(len(self.indices[0].values))],
                names=[index.name for index in self.indices])
        elif len(self.indices) == 1:
            index_value_type = type(self.indices[0].values[0]) if len(self.indices[0].values) > 0 else object
            if index_value_type == dt.datetime:
                index = pandas.DatetimeIndex(self.indices[0].values, name=self.indices[0].name)
            else:
                if index_value_type == DataObject:
                    index_value_type = object
                index = pandas.Index(tuple(self.indices[0].values), dtype=index_value_type, name=self.indices[0].name)
        else:
            index = None
        if use_object_dtype:
            return pandas.DataFrame(data=data, index=index, dtype=object)
        else:
            return pandas.DataFrame(data=data, index=index)

    def build_from_pandas(self, table_data: "pandas.DataFrame") -> "DataFrame":
        # check if the table has indices and if its multi-index or common index
        if isinstance(table_data.index, pandas.MultiIndex):
            table_data_indices = table_data.index.levels
        elif isinstance(table_data.index, pandas.Index) and not table_data.index.empty:
            table_data_indices = [table_data.index]
        else:
            table_data_indices = []

        self.column_names = table_data.columns
        self.index_names = [index.name for index in table_data_indices]
        self.column_types = [self._pandas_dtype_to_column_type(dtype) for dtype in table_data.dtypes]
        self.index_types = [self._pandas_dtype_to_column_type(index.dtype) for index in table_data_indices]
        replaced_name = False
        for i, name in enumerate(self.index_names):
            if name is None:
                self.index_names[i] = 'date'
                replaced_name = True
        rows = len(table_data.index)
        _df = self._pre_build_generic(rows, self.index_types, self.column_types)

        test_conversion_types = {
            pandas.api.types.is_integer_dtype: numpy.int32,
            _is_int64: numpy.int64,
            _is_float32: numpy.float32,
            _is_float64: numpy.float64,
            pandas.api.types.is_datetime64_any_dtype: numpy.datetime64,
        }
        convert_to_ctype = {
            numpy.int32: ctypes.c_int32,
            numpy.int64: ctypes.c_int64,
            numpy.float32: ctypes.c_float,
            numpy.float64: ctypes.c_double,
            numpy.datetime64: ctypes.c_longlong,

        }

        # Check column value types - if they support, call efficient set methods
        column_convert_to = {}
        column_fast_set = {}
        for i_column, column_name in enumerate(table_data.columns):
            column_values = table_data[column_name]
            column_fast_set[column_name] = False
            for test_func, convert_to_type in test_conversion_types.items():
                if test_func(column_values):
                    column_convert_to[column_name] = convert_to_type
                    column_fast_set[column_name] = True
                    break

        if replaced_name:
            for i, name in enumerate(self.index_names):
                if name == "date":
                    self.index_names[i] = None
        # check index value types
        index_convert_to = {}
        index_fast_set = {}
        for i_index, index_name in enumerate(self.index_names):
            index_fast_set[index_name] = False
            index_values = table_data.index.get_level_values(index_name)
            for test_func, convert_to_type in test_conversion_types.items():
                if test_func(index_values):
                    index_convert_to[index_name] = convert_to_type
                    index_fast_set[index_name] = True
                    break

        # replace None as index name with "date", the default index type.
        for i_index, index_name in enumerate(self.index_names):
            if index_name is None:
                self.index_names[i_index] = "date"

        for i_index, index_name in enumerate(self.index_names):
            if index_name in index_convert_to.keys():
                convert_to_type = index_convert_to[index_name]
            else:
                convert_to_type = None
            if isinstance(table_data.index, pandas.MultiIndex):
                index_values = table_data.index.get_level_values(index_name).to_numpy(dtype=convert_to_type)
            else:
                index_values = table_data.index.to_numpy(dtype=convert_to_type)
            if index_name in index_fast_set.keys() and index_fast_set[index_name]:
                if convert_to_type == numpy.datetime64:
                    # convert index_values to utc timezone and then to timestamp
                    # TODO: check if original dataframe values is unaltered
                    index_values = index_values.astype('datetime64[s]').astype(dt.datetime)
                    # for each value, convert to timestamp
                    for ix, x in enumerate(index_values):
                        index_values[ix] = int(x.replace(tzinfo=dt.timezone.utc).timestamp() + _date_transform)
                    # convert to int64
                    index_values = index_values.astype(numpy.int64)
                    ptr = index_values.ctypes.data_as(ctypes.POINTER(convert_to_ctype[convert_to_type]))
                    factorylib.lib.psrd_table_index_set_date_values(_df.handler(),
                                                                    i_index,
                                                                    ptr,
                                                                    self._err.handler())
                    if self._err.code != 0:
                        raise FactoryException(self._err.what)
                elif convert_to_type == numpy.int32:
                    ptr = index_values.ctypes.data_as(ctypes.POINTER(convert_to_ctype[convert_to_type]))
                    factorylib.lib.psrd_table_index_set_int32_values(_df.handler(),
                                                                     i_index,
                                                                     ptr,
                                                                     self._err.handler())
                    if self._err.code != 0:
                        raise FactoryException(self._err.what)
                elif convert_to_type == numpy.int64:
                    ptr = index_values.ctypes.data_as(ctypes.POINTER(convert_to_ctype[convert_to_type]))
                    factorylib.lib.psrd_table_index_set_int64_values(_df.handler(),
                                                                     i_index,
                                                                     ptr,
                                                                     self._err.handler())
                    if self._err.code != 0:
                        raise FactoryException(self._err.what)
                elif convert_to_type == numpy.float32:
                    ptr = index_values.ctypes.data_as(ctypes.POINTER(convert_to_ctype[convert_to_type]))
                    factorylib.lib.psrd_table_index_set_float32_values(_df.handler(),
                                                                        i_index,
                                                                        ptr,
                                                                        self._err.handler())
                    if self._err.code != 0:
                        raise FactoryException(self._err.what)
                elif convert_to_type == numpy.float64:
                    ptr = index_values.ctypes.data_as(ctypes.POINTER(convert_to_ctype[convert_to_type]))
                    factorylib.lib.psrd_table_index_set_float64_values(_df.handler(),
                                                                       i_index,
                                                                       ptr,
                                                                       self._err.handler())
                    if self._err.code != 0:
                        raise FactoryException(self._err.what)
                else:
                    raise FactoryException("Unsupported index type: " + str(convert_to_type))
            else:
                for i_row, column_value in enumerate(index_values):
                    self._value.set(column_value)
                    factorylib.lib.psrd_table_index_set_value(_df.handler(),
                                                              i_index,
                                                              i_row,
                                                              self._value.handler(),
                                                              self._err.handler())
                    if self._err.code != 0:
                        raise FactoryException(self._err.what)

        for i_column, column_name in enumerate(self.column_names):
            if column_name in column_convert_to.keys():
                convert_to_type = column_convert_to[column_name]
            else:
                convert_to_type = None
            column_values = table_data[column_name].to_numpy(dtype=convert_to_type)
            if column_name in column_fast_set.keys() and column_fast_set[column_name]:
                if convert_to_type == numpy.float32:
                    ptr = column_values.ctypes.data_as(ctypes.POINTER(convert_to_ctype[convert_to_type]))
                    factorylib.lib.psrd_table_column_set_float32_values(_df.handler(),
                                                                        i_column,
                                                                        ptr,
                                                                        self._err.handler())
                    if self._err.code != 0:
                        raise FactoryException(self._err.code)
                if convert_to_type == numpy.float64:
                    ptr = column_values.ctypes.data_as(ctypes.POINTER(convert_to_ctype[convert_to_type]))
                    factorylib.lib.psrd_table_column_set_float64_values(_df.handler(),
                                                                        i_column,
                                                                        ptr,
                                                                        self._err.handler())
                    if self._err.code != 0:
                        raise FactoryException(self._err.what)
                elif convert_to_type == numpy.int32:
                    ptr = column_values.ctypes.data_as(ctypes.POINTER(convert_to_ctype[convert_to_type]))
                    factorylib.lib.psrd_table_column_set_int32_values(_df.handler(),
                                                                      i_column,
                                                                      ptr,
                                                                      self._err.handler())
                    if self._err.code != 0:
                        raise FactoryException(self._err.what)
                elif convert_to_type == numpy.int64:
                    ptr = column_values.ctypes.data_as(ctypes.POINTER(convert_to_ctype[convert_to_type]))
                    factorylib.lib.psrd_table_column_set_int64_values(_df.handler(),
                                                                      i_column,
                                                                      ptr,
                                                                      self._err.handler())
                    if self._err.code != 0:
                        raise FactoryException(self._err.what)
            else:
                column_values = table_data[column_name]
                for i_row, column_value in enumerate(column_values):
                    self._value.set(column_value)
                    factorylib.lib.psrd_table_column_set_value(_df.handler(),
                                                               i_column,
                                                               i_row,
                                                               self._value.handler(),
                                                               self._err.handler())
                    if self._err.code != 0:
                        raise FactoryException(self._err.what)
        return _df


    def build_polars_dataframe(self, **kwargs) -> "polars.DataFrame":
        use_object_dtype = kwargs.get("use_object_dtype", True)
        if not _has_polars():
            raise ModuleNotFoundError("polars required.")
        def convert_column_values(column_name:str, values):
            if isinstance(values, list):
                return values
            # Looks like ctype array, smells like ctype array
            if hasattr(values, "_length_") and hasattr(values, "_type_"):
                return polars.Series(column_name, numpy.ctypeslib.as_array(values))
            return values

        data = {column.name: convert_column_values(column.name, column.values)
                for column in self.indices + self.columns}
        if use_object_dtype:
            return polars.DataFrame(data=data, dtype=object)
        else:
            return polars.DataFrame(data=data)

    def build_from_polars(self, table_data: "polars.DataFrame") -> "DataFrame":
        # check if the table has indices and if its multi-index or common index
        _index_names = ("year", "week", "month", "hour", "scenario", "block", "stage")
        column_index = 0
        data_columns = table_data.columns[:]
        index_columns = []
        while column_index < len(data_columns):
            if data_columns[column_index] in _index_names:
                index_columns.append(data_columns.pop(column_index))
                continue
            column_index += 1
        self.column_types = [self._polars_dtype_to_column_type(table_data[column_name].dtype) for column_name in data_columns]
        self.index_types = [self._polars_dtype_to_column_type(table_data[index_name].dtype) for index_name in index_columns]

        self.column_names = data_columns
        self.index_names = index_columns
        rows = table_data.height
        _df = self._pre_build_generic(rows, self.index_types, self.column_types)

        for i_row, all_row_values in enumerate(table_data.iter_rows()):
            index = all_row_values[:len(index_columns)]
            row_values = all_row_values[len(index_columns):]
            self._set_row_values(_df, i_row, index, row_values)
        return _df

    def _pre_build_generic(self, rows: int, index_types: List[int], column_types: List[int]) -> "DataFrame":
        _df = DataFrame()
        self._err = Error()
        self._value = Value()

        factorylib.lib.psrd_table_resize(_df.handler(), rows,
                                         self._err.handler())
        if self._err.code != 0:
            raise FactoryException(self._err.what)

        for i_index, index_type in enumerate(index_types):
            factorylib.lib.psrd_table_configure_index(_df.handler(),
                                                      i_index,
                                                      index_type,
                                                      self._err.handler())
            if self._err.code != 0:
                raise FactoryException(self._err.what)
        for i_column, column_type in enumerate(column_types):
            factorylib.lib.psrd_table_configure_column(_df.handler(),
                                                       i_column,
                                                       column_type,
                                                       self._err.handler())
            if self._err.code != 0:
                raise FactoryException(self._err.what)

        # Set column names
        for i_column, column_name in enumerate(self.column_names):
            factorylib.lib.psrd_table_column_set_name(_df.handler(),
                                                      i_column,
                                                      _c_str(column_name),
                                                      _bytes(column_name),
                                                      self._err.handler())
            if self._err.code != 0:
                raise FactoryException(self._err.what)

        # Set index names
        for i_index, index_name in enumerate(self.index_names):
            factorylib.lib.psrd_table_index_set_name(_df.handler(),
                                                     i_index,
                                                     _c_str(index_name),
                                                     _bytes(index_name),
                                                     self._err.handler())
            if self._err.code != 0:
                raise FactoryException(self._err.what)

        return _df

    def _set_row_values(self, df: "DataFrame", i_row: int, index_values: List[Union[int, float, str]], column_values: List[Union[int, float, str]]):
        self._value = Value()
        for i_index, index_value in enumerate(index_values):
            self._value.set(index_value)
            factorylib.lib.psrd_table_index_set_value(df.handler(),
                                                      i_index,
                                                      i_row,
                                                      self._value.handler(),
                                                      self._err.handler())
            if self._err.code != 0:
                raise FactoryException(self._err.what)

        for i_column, column_value in enumerate(column_values):
            self._value.set(column_value)
            factorylib.lib.psrd_table_column_set_value(df.handler(),
                                                       i_column,
                                                       i_row,
                                                       self._value.handler(),
                                                       self._err.handler())
            if self._err.code != 0:
                raise FactoryException(self._err.what)


class DataFrame(_BaseObject):
    def __init__(self):
        super().__init__()
        self._hdr = factorylib.lib.psrd_new_table()
        self._not_built = True

    def __del__(self):
        if self._hdr is not None:
            factorylib.lib.psrd_free_table(self._hdr)

    @staticmethod
    def load_from_file(input_file: Union[str, pathlib.Path], options: Optional[Union[dict, Value, DataObject]] = None) -> "DataFrame":
        input_file = str(input_file)
        _check_initialized()
        _err = Error()
        table = DataFrame()
        options_value = _get_arg_object(options)
        factorylib.lib.psrd_table_load(table.handler(),
                                       _c_str(input_file),
                                       _bytes(input_file),
                                       options_value.handler(),
                                       _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return table

    @staticmethod
    def from_dataframe(df: Union["pandas.DataFrame", "polars.DataFrame"], **kwargs) -> "DataFrame":
        _check_initialized()
        df_builder = _DataFrameBuilder()
        if _has_pandas() and isinstance(df, pandas.DataFrame):
            dataframe_like = pandas.api.interchange.from_dataframe(df)
            return df_builder.build_from_pandas(dataframe_like)
        if _has_polars() and isinstance(df, polars.DataFrame):
            dataframe_like = polars.from_dataframe(df)
            # FIXME: needs auto tests.
            return df_builder.build_from_polars(dataframe_like)
        raise ImportError("Pandas or polars is not available. Please install pandas to use this feature.")

    def save(self, output_file: Union[str, pathlib.Path], options: Optional[Union[dict, Value, DataObject]] = None):
        output_file = str(output_file)
        _err = Error()
        options_value = _get_arg_object(options)
        factorylib.lib.psrd_table_save(self._hdr, _c_str(output_file),
                                       _bytes(output_file),
                                       options_value.handler(),
                                       _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)

    def to_pandas(self) -> "pandas.DataFrame":
        df_builder = _DataFrameBuilder()
        df_builder.build_dataframe_of_integral_types(self)
        return df_builder.build_pandas_dataframe(use_object_dtype=False)

    def to_polars(self) -> "polars.DataFrame":
        df_builder = _DataFrameBuilder()
        df_builder.build_dataframe_of_integral_types(self)
        return df_builder.build_polars_dataframe(use_object_dtype=False)


    def get(self, expression: str) -> Union[int, float, dt.datetime, str, "DataObject", list, None]:
        value = Value()
        _err = Error()
        factorylib.lib.psrd_table_get_property(self._hdr,
                                               _c_str(expression),
                                               value.handler(),
                                               _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        return value.get()

    def set(self, expression: str, value):
        _err = Error()
        _val = Value()
        _val.set(value)
        factorylib.lib.psrd_table_set_property(self._hdr, _c_str(expression),
                                               _bytes(expression),
                                               _val.handler(),
                                               _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)


def load_dataframe(input_file: Union[str, pathlib.Path], **kwargs) -> DataFrame:
    options = kwargs.get("options", None)
    return DataFrame.load_from_file(input_file, options)


def create_dataframe(data: "pandas.DataFrame", **kwargs) -> DataFrame:
    return DataFrame.from_dataframe(data, **kwargs)


def _load_library():
    global _loaded
    global _loaded_lock
    with _loaded_lock:
        factorylib.initialize()
        _loaded = True
    return _loaded



def _initialize():
    global _initialized
    global _initialized_lock
    with _initialized_lock:
        _check_loaded()
        _err = Error()

        # Set binding info
        map_prop_values = {
            "NULL_TYPE": "None",
            "LIST_TYPE": "list",
            "INDEX_STARTS_AT_ZERO": True,
            "NAME": "Python",
            "VERSION": f"{sys.version}",
            "EXE": f"{sys.executable}",
            "LIB": f"{factorylib.get_lib_path()}",
            "BASE_PREFIX": f"{sys.base_prefix}",
            "REAL_PREFIX": f"{sys.prefix}",
        }
        for prop, value in map_prop_values.items():
            _value = Value()
            _value.set(value)
            factorylib.lib.psrd_set_binding_property(_c_str(prop),
                                                     _bytes(prop),
                                                     _value.handler(),
                                                     _err.handler())
            if _err.code != 0:
                raise FactoryException(_err.what)

        # Where to look for pmd and pmk files
        module_path = os.path.dirname(__file__)
        factorylib.lib.psrd_initialize(_c_str(module_path),
                                       _bytes(module_path),
                                       _err.handler())
        if _err.code != 0:
            raise FactoryException(_err.what)
        _initialized = True


def _unload():
    _err = Error()
    factorylib.lib.psrd_unload(_err.handler())
    if _err.code != 0:
        raise FactoryException(_err.what)


def help(context: str = "") -> str:
    _err = Error()
    size = factorylib.lib.psrd_help(_c_str(context), _bytes(context),
                                    None, 0, _err.handler())
    if _err.code != 0:
        raise FactoryException(_err.what)
    buffer = ctypes.create_string_buffer(size)
    factorylib.lib.psrd_help(_c_str(context), _bytes(context),
                             buffer, size, _err.handler())
    if _err.code != 0:
        raise FactoryException(_err.what)
    return _from_c_str(buffer.value)


def create_study(*args, **kwargs) -> Study:
    blocks = kwargs.get("blocks", None)
    models = kwargs.get("models", None)
    context = kwargs.get("context", None) if len(args) == 0 else args[0]
    profile = kwargs.get("profile", None)
    if models is None and profile is not None and len(profile) > 0:
        models = [profile, ]
    profile_or_context = models if models is not None and len(models) > 0 \
        else context
    return Study.create_object(profile_or_context, blocks)


def load_study(study_path: Union[str, pathlib.Path],
               profile_or_context: Union[str, Context, None] = None,
               options: Optional[DataObject] = None) -> Study:
    settings_only = False
    return Study.load(study_path, profile_or_context, settings_only, options)


def load_study_settings(study_path: Union[str, pathlib.Path],
               profile_or_context: Union[str, Context, None] = None,
               options: Optional[DataObject] = None) -> Study:
    settings_only = True
    return Study.load(study_path, profile_or_context, settings_only, options)


def create(class_name: str,
           profile_or_context: Union[str, Context, None] = None) -> Optional[DataObject]:
    _check_initialized()
    obj = DataObject()
    _err = Error()
    context = _get_context(profile_or_context, None) \
        if class_name != "Context" else None
    context_hdr = context.handler() if context is not None else None
    ref = factorylib.lib.psrd_create(_c_str(class_name),
                                     context_hdr,
                                     _err.handler())
    if _err.code != 0 or ref is None:
        raise FactoryException(_err.what)
    obj._hdr = ref
    return obj


def get_default_context() -> "Context":
    _check_initialized()
    return Context.default_context()


def get_new_context() -> "Context":
    _check_initialized()
    return Context.create()


def get_default_encoding() -> str:
    return _preferred_encoding


def set_default_encoding(encoding: str):
    global _preferred_encoding
    _preferred_encoding = encoding
