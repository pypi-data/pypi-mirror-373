#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    A remote procedure call (RPC) framework based on JSON-RPC, extended to
#    support alternative data formats and structures such as CSV, XML,
#    binary and python calls.
#    Copyright (C) 2025  JsonRpcExtended

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
A remote procedure call (RPC) framework based on JSON-RPC, extended to
support alternative data formats and structures such as CSV, XML,
binary and python calls.
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
A remote procedure call (RPC) framework based on JSON-RPC, extended to
support alternative data formats and structures such as CSV, XML,
binary and python calls.
"""
__url__ = "https://github.com/mauricelambert/JsonRpcExtended"

# __all__ = []

__license__ = "GPL-3.0 License"
__copyright__ = """
JsonRpcExtended  Copyright (C) 2025  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
copyright = __copyright__
license = __license__

print(copyright)

from json import dumps
from enum import IntEnum
from struct import pack, unpack
from io import StringIO, BytesIO
from csv import writer, QUOTE_ALL
from dataclasses import dataclass
from datetime import datetime, timedelta
from PegParser import get_json, csv_parse, csv_files_parse
from asyncio import start_server, StreamReader, StreamWriter
from typing import (
    Union,
    Tuple,
    List,
    Dict,
    Callable,
    Any,
    TypeVar,
    Iterator,
    Iterable,
)

NoneType = type(None)
RequestHeaders = TypeVar("RequestHeaders")
ResponseHeaders = TypeVar("ResponseHeaders")
BinaryJsonRpcRequestFormat = TypeVar("BinaryJsonRpcRequestFormat")
BinaryJsonRpcResponseFormat = TypeVar("BinaryJsonRpcResponseFormat")
Json = TypeVar("Json", Dict, List, str, int, float, NoneType)

windows_epoch = datetime(1601, 1, 1)
unix_epoch = datetime(1970, 1, 1)
epoch_difference = (unix_epoch - windows_epoch).total_seconds()


@dataclass
class Request:
    """
    This dataclass implements the JSON RPC request.
    """

    jsonrpc: str
    method: str
    id: Union[str, int, None] = None
    params: Union[List[Json], Dict[str, Json]] = None

    def checks(self) -> None:
        """
        This method checks data type.

        >>> Request("2.0", "test", "test", []).checks()
        >>> Request(0, "test", "test", []).checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid jsonrpc type
        >>> Request("", 0, "test", []).checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid method type
        >>> Request("", "", [], []).checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid id type
        >>> Request("", "", "", 0).checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid params type
        >>> Request("", "", "", None).checks()
        >>> Request("", "", "", {}).checks()
        >>> Request("", "", 0, {}).checks()
        >>> Request("", "", None, {}).checks()
        >>>
        """

        if not isinstance(self.jsonrpc, str):
            raise TypeError("Invalid jsonrpc type")

        if not isinstance(self.method, str):
            raise TypeError("Invalid method type")

        if self.id is not None and not isinstance(
            self.id, (str, int, NoneType)
        ):
            raise TypeError("Invalid id type")

        if self.params is not None and not isinstance(
            self.params, (list, dict)
        ):
            raise TypeError("Invalid params type")

    def asdict(self) -> Dict[str, Union[int, str]]:
        """
        This method returns this class as a dict for JsonRpc request.

        >>> Request("", "", None, None).asdict()
        {'jsonrpc': '', 'method': ''}
        >>> Request("2.0", "test", 1, [1, 2, 3]).asdict()
        {'jsonrpc': '2.0', 'method': 'test', 'id': 1, 'params': [1, 2, 3]}
        >>>
        """

        value = {"jsonrpc": self.jsonrpc, "method": self.method}

        if self.id is not None:
            value["id"] = self.id

        if self.params is not None:
            value["params"] = self.params

        return value


@dataclass
class PyRequest:
    """
    This dataclass implements the modified JSON RPC request for python.
    """

    jsonrpc: str
    method: str
    id: Union[str, int, None] = None
    args: List[Json] = None
    kwargs: Dict[str, Json] = None

    def checks(self) -> None:
        """
        This method checks data type.

        >>> PyRequest("2.0", "test", 1, [], {}).checks()
        >>> PyRequest(0, "test", "test", []).checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid jsonrpc type
        >>> PyRequest("", 0, "test", []).checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid method type
        >>> PyRequest("", "", [], []).checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid id type
        >>> PyRequest("", "", "", 0, {}).checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid args type
        >>> PyRequest("", "", "", [], 0).checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid kwargs type
        >>> PyRequest("", "", "test", [], {}).checks()
        >>> PyRequest("", "", None, None, None).checks()
        >>>
        """

        if not isinstance(self.jsonrpc, str):
            raise TypeError("Invalid jsonrpc type")

        if not isinstance(self.method, str):
            raise TypeError("Invalid method type")

        if self.id is not None and not isinstance(
            self.id, (str, int, NoneType)
        ):
            raise TypeError("Invalid id type")

        if self.args is not None and not isinstance(self.args, list):
            raise TypeError("Invalid args type")

        if self.kwargs is not None and not isinstance(self.kwargs, dict):
            raise TypeError("Invalid kwargs type")

    def asdict(self) -> Dict[str, Union[int, str]]:
        """
        This method returns this class as a dict for JsonRpc request.

        >>> PyRequest("", "", None, None).asdict()
        {'jsonrpc': '', 'method': ''}
        >>> PyRequest("py2.0", "test", 1, [1, 2, 3], {'a': 'a'}).asdict()
        {'jsonrpc': 'py2.0', 'method': 'test', 'id': 1, 'args': [1, 2, 3], 'kwargs': {'a': 'a'}}
        >>>
        """

        value = {"jsonrpc": self.jsonrpc, "method": self.method}

        if self.id is not None:
            value["id"] = self.id

        if self.args is not None:
            value["args"] = self.args

        if self.kwargs is not None:
            value["kwargs"] = self.kwargs

        return value


@dataclass
class Error:
    code: int
    message: str
    data: str = None

    def checks(self) -> None:
        """
        This method checks data type.

        >>> Error(0, "test", "test").checks()
        >>> Error(0, "test", None).checks()
        >>> Error("test", "test", "test").checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid code type
        >>> Error(0, 0, "test").checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid message type
        >>> Error(0, "", 0).checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid data type
        >>>
        """

        if not isinstance(self.code, int):
            raise TypeError("Invalid code type")

        if not isinstance(self.message, str):
            raise TypeError("Invalid message type")

        if self.data is not None and not isinstance(self.data, str):
            raise TypeError("Invalid data type")

    def asdict(self) -> Dict[str, Union[int, str]]:
        """
        This method returns this class as a dict for JsonRpc response.

        >>> Error(0, "test", None).asdict()
        {'code': 0, 'message': 'test'}
        >>> Error(0, "test", "test2").asdict()
        {'code': 0, 'message': 'test', 'data': 'test2'}
        >>>
        """

        if self.data is None:
            return {"code": self.code, "message": self.message}
        return {"code": self.code, "message": self.message, "data": self.data}


@dataclass
class Response:
    """
    This dataclass implements the JSON RPC request.
    """

    jsonrpc: str
    id: Union[str, int, None]
    result: Json = None
    error: Error = None

    def checks(self) -> None:
        """
        This method checks data type.

        >>> Response("2.0", None, None, None).checks()
        >>> Response("2.0", 1, {}, Error(0, "")).checks()
        Traceback (most recent call last):
            ...
        ValueError: Error and result should not be set in the same response.
        >>> Response("2.0", 1, None, Error(0, "")).checks()
        >>> Response("2.0", 1, {}, None).checks()
        >>> Response(0, 1, {}, None).checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid jsonrpc type
        >>> Response("", [], {}, None).checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid id type
        >>> Response("", "", Error(0, ""), None).checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid result type
        >>> Response("", "", {}, {}).checks()
        Traceback (most recent call last):
            ...
        TypeError: Invalid error type
        >>>
        """

        if not isinstance(self.jsonrpc, str):
            raise TypeError("Invalid jsonrpc type")

        if not isinstance(self.id, (str, int, NoneType)):
            raise TypeError("Invalid id type")

        if self.result is not None and not isinstance(
            self.result, (list, dict, str, int, float, bool)
        ):
            raise TypeError("Invalid result type")

        if self.error is not None and not isinstance(self.error, Error):
            raise TypeError("Invalid error type")

        if self.result is not None and self.error is not None:
            raise ValueError(
                "Error and result should not be set in the same response."
            )

    def asdict(
        self, id: Union[str, int] = None
    ) -> Dict[str, Union[int, str, Json, Error]]:
        """
        This method returns this class as a dict for JsonRpc response.

        >>> Response("", "", None, None).asdict()
        {'jsonrpc': '', 'id': ''}
        >>> Response("2.0", "test", [1, 2, 3]).asdict()
        {'jsonrpc': '2.0', 'id': 'test', 'result': [1, 2, 3]}
        >>> Response("2.0", "test", None, Error(0, 'test')).asdict()
        {'jsonrpc': '2.0', 'id': 'test', 'error': {'code': 0, 'message': 'test'}}
        >>>
        """

        if id is not None:
            value = {"jsonrpc": self.jsonrpc, "id": id}
        else:
            value = {"jsonrpc": self.jsonrpc, "id": self.id}

        if self.result is not None:
            value["result"] = self.result
        elif self.error is not None:
            value["error"] = self.error.asdict()

        return value


class JsonRpcServer:
    """
    This class implements JSON RPC RFC.

    Multiples methods come from: https://github.com/mauricelambert/WebScripts/blob/main/WebScripts/modules/JsonRpc.py
    """

    functions: Dict[str, Callable] = {}

    @classmethod
    def register_function(
        cls: type, function: Callable, name: str = None
    ) -> None:
        """
        This function adds a new function in the JSON RPC calls.
        """

        if name:
            cls.functions[name] = function
            return None

        def bname(func):
            if (
                hasattr(func, "__globals__")
                and func.__globals__["__package__"]
            ):
                return (
                    func.__globals__["__package__"]
                    + "."
                    + func.__module__
                    + "."
                )
            elif hasattr(func, "__self__") and func.__self__.__package__:
                return func.__self__.__package__ + "." + func.__module__ + "."

            return func.__module__ + "."

        if hasattr(function, "__self__") and hasattr(function, "__func__"):
            cls.functions[
                bname(function.__func__)
                + function.__self__.__class__.__name__
                + "."
                + function.__name__
            ] = function
            return None

        cls.functions[bname(function) + function.__name__] = function

    @classmethod
    def check_request(
        cls: type, json: Dict[str, Any], id: Union[str, int, None]
    ) -> Union[None, Dict[str, Union[str, int, Error]]]:
        """
        This function checks the JSON RPC received requests.

        >>> JsonRpcServer.register_function(dir, 'test')
        >>> JsonRpcServer.register_function(dir)
        >>> JsonRpcServer.check_request({}, 1)
        {'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32600, 'message': 'Invalid Request'}}
        >>> JsonRpcServer.check_request({'jsonrpc': '2.0'}, 1)
        {'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32600, 'message': 'Invalid Request'}}
        >>> JsonRpcServer.check_request({'jsonrpc': '2.0', 'method': 'test', 'params': None}, 1)
        {'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32602, 'message': 'Invalid params'}}
        >>> JsonRpcServer.check_request({'jsonrpc': '2.0', 'method': 'builtins.dir'}, 1)
        >>>
        """

        method = json.get("method")

        if json.get("jsonrpc") != "2.0" or not isinstance(method, str):
            return response_invalid_request.asdict(id)

        if method not in cls.functions:
            return response_method_not_found.asdict(id)

        if "params" in json and not isinstance(json["params"], (list, dict)):
            return response_invalid_params.asdict(id)

    @classmethod
    def call(cls: type, method: Callable, json: Dict[str, Any]) -> Any:
        """
        This function calls the python function.
        """

        params = json.get("params", [])

        if isinstance(params, list):
            return method(*params)

        return method(**params)

    @classmethod
    def execute_call(
        cls: type, json: Dict[str, Any]
    ) -> Union[None, Dict[str, Union[str, int, Error, Json]]]:
        """
        This function performs a JSON RPC call.

        >>> JsonRpcServer.register_function(int)
        >>> JsonRpcServer.register_function(lambda **y: int('1', **y), 'int1')
        >>> JsonRpcServer.execute_call([])
        {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32600, 'message': 'Invalid Request'}}
        >>> JsonRpcServer.execute_call({'id': 1})
        {'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32600, 'message': 'Invalid Request'}}
        >>> JsonRpcServer.execute_call({})
        >>> JsonRpcServer.execute_call({'jsonrpc': '2.0', 'id': 1, 'method': 'builtins.int', 'params': ['1']})
        {'jsonrpc': '2.0', 'id': 1, 'result': 1}
        >>> JsonRpcServer.execute_call({'jsonrpc': '2.0', 'id': 1, 'method': 'int1', 'params': {'base': 16}})
        {'jsonrpc': '2.0', 'id': 1, 'result': 1}
        >>> JsonRpcServer.execute_call({'jsonrpc': '2.0', 'method': 'int1', 'params': {'base': 16}})
        >>> JsonRpcServer.execute_call({'jsonrpc': '2.0', 'id': 1, 'method': 'builtins.int', 'params': ['a']})
        {'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32603, 'message': 'Internal error'}}
        >>>
        """

        if not isinstance(json, dict):
            return response_invalid_request.asdict()

        id_ = json.get("id")
        error_response = cls.check_request(json, id_)

        if id_ is not None and error_response:
            return error_response
        elif error_response:
            return None

        method = json["method"]

        try:
            value = cls.call(cls.functions[method], json)
        except Exception as e:
            if id_ is None:
                return None
            return response_internal_error.asdict(id_)

        if id_ is not None:
            return Response("2.0", id_, value).asdict()

    @classmethod
    def execute_calls(
        cls: type, json: Union[Dict[str, Json], List[Dict[str, Json]]]
    ) -> Union[
        None,
        Union[
            Dict[str, Union[str, int, Error, Json]],
            Dict[str, Union[str, int, Error, Json]],
        ],
    ]:
        """
        This function performs JSON RPC calls.

        >>> JsonRpcServer.register_function(dir)
        >>> JsonRpcServer.register_function(int)
        >>> JsonRpcServer.execute_calls([])
        {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32600, 'message': 'Invalid Request'}}
        >>> JsonRpcServer.execute_calls(None)
        {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32600, 'message': 'Invalid Request'}}
        >>> JsonRpcServer.execute_calls(Request('2.0', 'dir').asdict())
        >>> JsonRpcServer.execute_calls([Request('2.0', 'builtins.int', 1, [1]).asdict()])
        [{'jsonrpc': '2.0', 'id': 1, 'result': 1}]
        >>>
        """

        if isinstance(json, list) and json:
            responses = []
            for request in json:
                if (response := cls.execute_call(request)) is not None:
                    responses.append(response)
            return responses
        elif isinstance(json, dict):
            return cls.execute_call(json)
        else:
            return response_invalid_request.asdict()

    @classmethod
    def handle_request_data(
        cls: type, json: bytes, permissive: bool = False
    ) -> Union[None, str]:
        """
        This function parses JSON from data to perform RPC calls.

        >>> JsonRpcServer.register_function(dir)
        >>> JsonRpcServer.register_function(int)
        >>> JsonRpcServer.handle_request_data(b'{"jsonrpc": "2.0", "method": "dir"}')
        >>> JsonRpcServer.handle_request_data(b'{"jsonrpc" "2.0" "method" "builtins.int", "id": 1 "params" ["1"],,,}', permissive=True)
        '{"jsonrpc": "2.0", "id": 1, "result": 1}'
        >>> JsonRpcServer.handle_request_data(b'{"jsonrpc" ')
        '{"jsonrpc": "2.0", "id": null, "error": {"code": -32600, "message": "Invalid Request"}}'
        >>>
        """

        try:
            response = cls.execute_calls(get_json(json, permissive=permissive))
        except ValueError:
            response = response_invalid_request.asdict()

        return response and dumps(response)


class PyJsonRpcServer(JsonRpcServer):
    """
    This class implements a modified JSON RPC for python.
    """

    @classmethod
    def check_request(
        cls: type, json: Dict[str, Any], id: Union[str, int, None]
    ) -> Union[None, Dict[str, Union[str, int, Error]]]:
        """
        This function checks the JSON RPC received requests.

        >>> PyJsonRpcServer.register_function(dir, 'test')
        >>> PyJsonRpcServer.register_function(dir)
        >>> PyJsonRpcServer.check_request({}, 1)
        {'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32600, 'message': 'Invalid Request'}}
        >>> PyJsonRpcServer.check_request({'jsonrpc': 'py2.0'}, 1)
        {'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32600, 'message': 'Invalid Request'}}
        >>> PyJsonRpcServer.check_request({'jsonrpc': 'py2.0', 'method': 'test', 'args': {}}, 1)
        {'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32602, 'message': 'Invalid params'}}
        >>> PyJsonRpcServer.check_request({'jsonrpc': 'py2.0', 'method': 'test', 'kwargs': []}, 1)
        {'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32602, 'message': 'Invalid params'}}
        >>> PyJsonRpcServer.check_request({'jsonrpc': 'py2.0', 'method': 'builtins.dir'}, 1)
        >>>
        """

        method = json.get("method")

        if json.get("jsonrpc") != "py2.0" or not isinstance(method, str):
            return response_invalid_request.asdict(id)

        if method not in cls.functions:
            return response_method_not_found.asdict(id)

        if "args" in json and not isinstance(json["args"], list):
            return response_invalid_params.asdict(id)

        if "kwargs" in json and not isinstance(json["kwargs"], dict):
            return response_invalid_params.asdict(id)

    @classmethod
    def call(cls: type, method: Callable, json: Dict[str, Any]) -> Any:
        """
        This function calls the python function.
        """

        args = json.get("args", [])
        kwargs = json.get("kwargs", {})
        return method(*args, **kwargs)


def get_sub_container(key: str) -> Union[dict, list]:
    """
    This function returns a new sub containers based on the key.
    """

    if key and key[0] == "#":
        return []
    elif key:
        return {}


def get_typed_value(
    key: str, value: str
) -> Tuple[str, Union[None, bool, int, float, str]]:
    """
    This function returns the real key and the typed value to add from CSV.

    >>> get_typed_value("int?test", "3")
    ('test', 3)
    >>> get_typed_value("float?test", "3.14")
    ('test', 3.14)
    >>> get_typed_value("str?test", "test")
    ('test', 'test')
    >>> get_typed_value("bool?test", "FalSe")
    ('test', False)
    >>> get_typed_value("bool?test", "0")
    ('test', False)
    >>> get_typed_value("bool?test", "any other")
    ('test', True)
    >>> get_typed_value("NoneType?test", "any value")
    ('test', None)
    >>> get_typed_value("test", "test")
    ('test', 'test')
    >>>
    """

    if key.startswith("int?"):
        return key[4:], int(value)
    elif key.startswith("float?"):
        return key[6:], float(value)
    elif key.startswith("str?"):
        return key[4:], value
    elif key.startswith("bool?"):
        return key[5:], (
            False if value.casefold() == "false" or value == "0" else True
        )
    elif key.startswith("NoneType?"):
        return key[9:], None

    return key, value


def csv_add_list_value(
    container: list, key: str, value: str, index: int
) -> None:
    """
    This function adds a value into the list container.
    """

    if len(container) <= index:
        while len(container) < index:
            container.append(None)
        if (sub_container := get_sub_container(key)) is None:
            container.append(value)
            return None
        container.append(sub_container)
        csv_add_value(sub_container, key, value)
        return None

    elif isinstance(container[index], (list, dict)):
        csv_add_value(container[index], key, value)
        return None

    sub_container = get_sub_container(key)
    if sub_container is None:
        container[index] = value
        return None

    container[index] = sub_container
    csv_add_value(sub_container, key, value)


def csv_get_index(key: str) -> Tuple[str, int]:
    """
    This function returns the index and the new key.
    """

    index = ""
    key = key[1:]
    character = key and key[0]

    while key and character in "0123456789":
        index += character
        key = key[1:]
        character = key and key[0]

    index = int(index)
    return key, index


def csv_add_value(container: Union[dict, list], key: str, value: str) -> None:
    """
    This function adds a value into the container.

    >>> a = []
    >>> csv_add_value(a, '#0', 0)
    >>> a
    [0]
    >>> csv_add_value(a, '#2', 2)
    >>> a
    [0, None, 2]
    >>> csv_add_value(a, '#1', 1)
    >>> a
    [0, 1, 2]
    >>> csv_add_value(a, '#3abc', 0)
    >>> a
    [0, 1, 2, {'abc': 0}]
    >>> csv_add_value(a, '#3def', 2)
    >>> a
    [0, 1, 2, {'abc': 0, 'def': 2}]
    >>> csv_add_value(a, '#4abc1.def1', 1)
    >>> a
    [0, 1, 2, {'abc': 0, 'def': 2}, {'abc1': {'def1': 1}}]
    >>> csv_add_value(a, '#4abc2.def2.ghi2', 2)
    >>> a
    [0, 1, 2, {'abc': 0, 'def': 2}, {'abc1': {'def1': 1}, 'abc2': {'def2': {'ghi2': 2}}}]
    >>> csv_add_value(a, '#4abc2.jkl2', 2)
    >>> a
    [0, 1, 2, {'abc': 0, 'def': 2}, {'abc1': {'def1': 1}, 'abc2': {'def2': {'ghi2': 2}, 'jkl2': 2}}]
    >>> csv_add_value(a, '#4abc3.def3.#3#3ghi3', 3)
    >>> a
    [0, 1, 2, {'abc': 0, 'def': 2}, {'abc1': {'def1': 1}, 'abc2': {'def2': {'ghi2': 2}, 'jkl2': 2}, 'abc3': {'def3': [None, None, None, [None, None, None, {'ghi3': 3}]]}}]
    >>>
    """

    if not key:
        return None

    if key[0] == "#":
        key, index = csv_get_index(key)
        csv_add_list_value(container, key, value, index)
    elif "." in key:
        if key[0] == "*":
            key = key[1:]

        key, sub_key = key.split(".", 1)
        sub_container = get_sub_container(sub_key)
        if sub_container is None:
            container[key] = value
            return None

        sub_container = container.setdefault(key, sub_container)
        csv_add_value(sub_container, sub_key, value)
    else:
        if key[0] == "*":
            key = key[1:]
        container[key] = value


def load_csv_object_as_json(
    parser: Iterable[Tuple[str]], columns: Tuple[str]
) -> Tuple[List[Json], Dict[str, Json]]:
    """
    This function loads a CSV like data as JSON.
    """

    start_dict = {}
    start_list = []

    for line in parser:
        for i, key in enumerate(columns):
            key, value = get_typed_value(key, line[i])
            if key[0] == "#":
                csv_add_value(start_list, key, value)
            else:
                csv_add_value(start_dict, key, value)

    return start_list, start_dict


def load_csv_as_json(csv: bytes) -> Tuple[List[Json], Dict[str, Json]]:
    """
    This function loads a CSV file as JSON data.
    """

    parser = csv_parse(csv)
    columns = next(parser)

    return load_csv_object_as_json(parser, columns)


def get_calls_from_csv(
    csv: bytes, pyrpc: bool = False
) -> List[Dict[str, Union[str, int, List[Json], Dict[str, Json]]]]:
    """
    This functions parses and formats CSV data bytes to RPC calls.
    """

    requests = []
    for parser in csv_files_parse(BytesIO(csv)):
        if not parser:
            continue

        columns = parser.pop(0)

        for line in parser:
            args = []
            kwargs = {}
            request = {"args": args, "kwargs": kwargs}
            requests.append(request)

            for i, key in enumerate(columns):
                key, value = get_typed_value(key, line[i])
                if key in ("jsonrpc", "method", "id"):
                    request[key] = value
                elif key[0] == "#":
                    csv_add_value(args, key, value)
                else:
                    csv_add_value(kwargs, key, value)

            if not (request["args"] and request["kwargs"]) and not pyrpc:
                request["params"] = request["args"] or request["kwargs"]
                del request["args"]
                del request["kwargs"]

    return requests


def csv_dump_response(
    response: Union[Dict[str, Json], List[Json]],
    new: Dict[str, str],
    key: str = "",
) -> None:
    """
    This function dumps a response to CSV.

    >>> a = {}
    >>> csv_dump_response({'jsonrpc': '2.0'}, a)
    >>> a
    {'str?jsonrpc': '2.0'}
    >>> csv_dump_response({'jsonrpc': '2.0', 'id': 1, 'result': None}, a)
    >>> a
    {'str?jsonrpc': '2.0', 'int?id': '1', 'NoneType?result': 'None'}
    >>> a = {}
    >>> response = {'jsonrpc': '2.0', 'id': 1, 'error': {"code": -32600, "message": "Invalid Request"}}
    >>> csv_dump_response(response, a)
    >>> a
    {'str?jsonrpc': '2.0', 'int?id': '1', 'int?error.code': '-32600', 'str?error.message': 'Invalid Request'}
    >>> test = {}
    >>> for key, value in a.items():
    ...     key, value = get_typed_value(key, value)
    ...     csv_add_value(test, key, value)
    >>> test
    {'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32600, 'message': 'Invalid Request'}}
    >>> test == response
    True
    >>>
    """

    if isinstance(response, dict):
        for new_key, value in response.items():
            temp_key = (key + "." + new_key) if key else new_key
            if isinstance(value, (dict, list)):
                csv_dump_response(value, new, temp_key)
            else:
                new[type(value).__name__ + "?" + temp_key] = str(value)
    elif isinstance(response, list):
        for index, value in enumerate(response):
            temp_key = key + "#" + str(index)
            if isinstance(value, (dict, list)):
                csv_dump_response(value, new, temp_key)
            else:
                new[type(value).__name__ + "?" + temp_key] = str(value)


def csv_dump_responses(
    responses: Union[List[Dict[str, Json]], Dict[str, Json]]
) -> str:
    r"""
    This function dumps the response(s) to CSV.

    >>> csv_dump_responses({'jsonrpc': '2.0'})
    '"jsonrpc"\r\n"2.0"\r\n'
    >>> a = {'jsonrpc': '2.0', 'id': 1, 'result': None}
    >>> c = {}
    >>> csv_dump_response(a, c)
    >>> b = csv_dump_responses(c)
    >>> c = {}
    >>> b
    '"str?jsonrpc","int?id","NoneType?result"\r\n"2.0","1","None"\r\n'
    >>> _, c = load_csv_as_json(b.encode())
    >>> c
    {'jsonrpc': '2.0', 'id': 1, 'result': None}
    >>> a == c
    True
    >>> csv_dump_responses({'str?jsonrpc': '2.0', 'int?id': '1', 'int?error.code': '-32600', 'str?error.message': 'Invalid Request'})
    '"str?jsonrpc","int?id","int?error.code","str?error.message"\r\n"2.0","1","-32600","Invalid Request"\r\n'
    >>> csv_dump_responses([{'str?jsonrpc': '2.0', 'int?id': '1', 'NoneType?result': 'None'}, {'str?jsonrpc': '2.0', 'int?id': '1', 'int?error.code': '-32600', 'str?error.message': 'Invalid Request'}])
    '"str?jsonrpc","int?id","NoneType?result"\r\n"2.0","1","None"\r\n\n"str?jsonrpc","int?id","int?error.code","str?error.message"\r\n"2.0","1","-32600","Invalid Request"\r\n'
    >>>
    """

    if isinstance(responses, dict):
        file = StringIO()
        csv = writer(file, quoting=QUOTE_ALL)
        csv.writerow(list(responses.keys()))
        csv.writerow(list(responses.values()))
        return file.getvalue()

    content = ""
    for response in responses:
        if content:
            content += "\n"

        file = StringIO()
        csv = writer(file, quoting=QUOTE_ALL)
        csv.writerow(list(response.keys()))
        csv.writerow(list(response.values()))
        content += file.getvalue()

    return content


def csv_dump_from_json(json: Json) -> str:
    """
    This function returns a CSV content from a loaded JSON.
    """

    csv_like_data = {}
    csv_dump_response(json, csv_like_data)
    return csv_dump_responses(csv_like_data)


class _CsvRpcServerInterface:
    """
    This class implements a CSV RPC interface.
    """

    @classmethod
    def handle_request_data(cls: type, csv: bytes) -> Union[None, str]:
        """
        This method parses CSV from data to perform RPC calls.
        """

        try:
            data = get_calls_from_csv(csv, cls.pyrpc)
        except ValueError:
            response = response_invalid_request.asdict()
        else:
            if len(data) == 1:
                data = data[0]
            response = cls.execute_calls(data)

        if response is None:
            return None

        return csv_dump_from_json(response)


class CsvRpcServer(_CsvRpcServerInterface, JsonRpcServer):
    r"""
    This class implements a CSV RPC.

    >>> CsvRpcServer.register_function(dir)
    >>> CsvRpcServer.register_function(int)
    >>> CsvRpcServer.handle_request_data(b'"jsonrpc","method"\n"2.0","dir"\n')
    >>> CsvRpcServer.handle_request_data(b'"jsonrpc","method","int?id","#0"\n"2.0","builtins.int","1","1"\n')
    '"str?jsonrpc","int?id","int?result"\r\n"2.0","1","1"\r\n'
    >>> CsvRpcServer.handle_request_data(b'"jsonrpc')
    '"str?jsonrpc","NoneType?id","int?error.code","str?error.message"\r\n"2.0","None","-32600","Invalid Request"\r\n'
    >>>
    """

    pyrpc = False


class PyCsvRpcServer(_CsvRpcServerInterface, PyJsonRpcServer):
    r"""
    This class implements a modified CSV RPC.

    >>> PyCsvRpcServer.register_function(dir)
    >>> PyCsvRpcServer.register_function(int)
    >>> PyCsvRpcServer.handle_request_data(b'"jsonrpc","method"\n"py2.0","dir"\n')
    >>> PyCsvRpcServer.handle_request_data(b'"jsonrpc","method","int?id","#0"\n"py2.0","builtins.int","1","1"\n')
    '"str?jsonrpc","int?id","int?result"\r\n"2.0","1","1"\r\n'
    >>> PyCsvRpcServer.handle_request_data(b'"jsonrpc')
    '"str?jsonrpc","NoneType?id","int?error.code","str?error.message"\r\n"2.0","None","-32600","Invalid Request"\r\n'
    >>>
    """

    pyrpc = True


@dataclass
class ResponseHeaders:
    error: bool

    def to_byte(self) -> int:
        """
        This method returns the byte for the headers.

        >>> bin(ResponseHeaders(True).to_byte())
        '0b10000000'
        >>> ResponseHeaders(False).to_byte()
        0
        >>>
        """

        headers = 0

        if self.error:
            headers += 0b10000000

        return headers

    @classmethod
    def from_bytes(cls: type, data: bytes) -> ResponseHeaders:
        """
        This method builds an instance for this class from data.

        >>> ResponseHeaders.from_bytes(bytes([0b10000000]))
        ResponseHeaders(error=True)
        >>> ResponseHeaders.from_bytes(bytes([0b00000000]))
        ResponseHeaders(error=False)
        >>>
        """

        value = data[0]
        return cls(bool(value & 0b10000000))


@dataclass
class RequestHeaders:
    binary: bool
    has_version: bool
    py_json_rpc: bool
    has_id: bool
    has_auth: bool

    def to_byte(self) -> int:
        """
        This method returns the byte for the headers.

        >>> RequestHeaders(True, True, True, True, True).to_byte()
        248
        >>> bin(RequestHeaders(True, False, False, False, False).to_byte())
        '0b10000000'
        >>>
        """

        headers = 0

        if self.binary:
            headers += 0b10000000

        if self.has_version:
            headers += 0b01000000

        if self.py_json_rpc:
            headers += 0b00100000

        if self.has_id:
            headers += 0b00010000

        if self.has_auth:
            headers += 0b00001000

        return headers

    @classmethod
    def from_bytes(cls: type, data: bytes) -> RequestHeaders:
        """
        This method builds an instance for this class from data.

        >>> RequestHeaders.from_bytes(bytes([248]))
        RequestHeaders(binary=True, has_version=True, py_json_rpc=True, has_id=True, has_auth=True)
        >>> RequestHeaders.from_bytes(bytes([0b10000000]))
        RequestHeaders(binary=True, has_version=False, py_json_rpc=False, has_id=False, has_auth=False)
        >>>
        """

        value = data[0]

        if not (value & 0b10000000):
            raise ValueError("Invalid headers value")

        has_version = bool(value & 0b01000000)
        py_json_rpc = bool(value & 0b00100000)
        has_id = bool(value & 0b00010000)
        has_auth = bool(value & 0b00001000)

        return cls(
            True,
            has_version,
            py_json_rpc,
            has_id,
            has_auth,
        )


class BinaryJsonRpc(JsonRpcServer):
    """
    This class implements the binary JSON RPC protocols.
    """

    @classmethod
    def handle_request_data(
        cls: type, binary: bytes, reader: Callable = None
    ) -> Union[None, str]:
        r"""
        This method parses binary JSON from data to perform RPC calls.

        >>> BinaryJsonRpc.register_function(dir)
        >>> BinaryJsonRpc.register_function(int)
        >>> BinaryJsonRpc.handle_request_data(b'\x80Cdir\x00')
        >>> BinaryJsonRpc.handle_request_data(b'\x90\x03\x01Lbuiltins.int\x81A1')
        bytearray(b'\x00\x03\x01\x03\x01')
        >>>
        """

        try:
            data = BinaryJsonRpcRequestFormat.from_bytes(
                binary, reader
            ).asdict()
        except ValueError:
            response = response_invalid_request.asdict()
        else:
            response = cls.execute_calls(data)

        if response is None:
            return None

        error = bool(response.get("error"))
        if error:
            response["error"]["code"] = abs(response["error"]["code"])

        return BinaryJsonRpcResponseFormat(
            response["id"], error, response["error" if error else "result"]
        ).to_bytes()


class BinaryJsonFormat:
    """
    This class implements the binary JSON format parsing.
    """

    def __init__(self, encoding: str, get_content: Callable = None):
        self.encoding = encoding
        self.get_content = get_content

    def list_block(self, size_length: int) -> List[Json]:
        """
        This method parses a Json like list from binary data.
        """

        return self.read_list(self.int_block(size_length, False))

    def read_list(self, size: int) -> List[Json]:
        """
        This method parses a Json like list from binary data.
        """

        return [self.read_next_element() for index in range(size)]

    def dict_block(self, size_length: int) -> Dict[str, Json]:
        """
        This method parses a Json like dict from binary data.
        """

        return self.read_dict(self.int_block(size_length, False))

    def read_dict(self, size: int) -> Dict[str, Json]:
        """
        This method parses a Json like dict from binary data.
        """

        return {
            self.read_next_element(): self.read_next_element()
            for index in range(size)
        }

    def int_block(self, size: int, signed: bool = True) -> int:
        """
        This method transfrom the next block value into an integer.
        """

        if signed and size == 3:
            return int.from_bytes(self.read(4)) * -1
        elif signed and size == 7:
            return int.from_bytes(self.read(8)) * -1

        return int.from_bytes(self.read(size))

    def read_str(self, size: int) -> str:
        """
        This method returns strings value from the binary data.
        """

        return bytes(self.read(size)).decode(self.encoding)

    def string_block(self, size_length: int) -> str:
        """
        This method transfrom the next block value into an integer.
        """

        return self.read_str(self.int_block(size_length, False))

    def read_float4(self) -> float:
        """
        This function parses next 4 bytes as float.
        """

        return unpack("f", self.read(4))[0]

    def read_float8(self) -> float:
        """
        This function parses next 8 bytes as float.
        """

        return unpack("d", self.read(8))[0]

    def unix_timestamp(self) -> datetime:
        """
        This method returns datetime for a unix timestamp from binary data.
        """

        return datetime.fromtimestamp(int.from_bytes(self.read(4)))

    def windows_timestamp(self) -> datetime:
        """
        This method returns datetime for a windows timestamp from binary data.
        """

        return datetime.fromtimestamp(
            (int.from_bytes(self.read(8)) / 10_000_000) - epoch_difference
        )

    def duration(self) -> timedelta:
        """
        This method returns timedelta from binary data.
        """

        return timedelta(
            microseconds=int.from_bytes(self.read(8), signed=True)
        )

    def read(self, number: int) -> bytes:
        """
        This method reads `number` of bytes.
        """

        while number > len(self.data_view):
            if self.get_content is None:
                raise ValueError("Not bytes enough")
            self.data_view = memoryview(
                bytes(self.data_view) + self.get_content()
            )

        value = self.data_view[:number]
        self.data_view = self.data_view[number:]
        return value

    def read_next_element(self) -> Json:
        """
        This function reads the next Json like element from binary data.
        """

        type = self.data_view[0]
        self.data_view = self.data_view[1:]
        if type == 0:
            return None
        elif type == 1:
            return True
        elif type == 2:
            return False
        elif type == 3:
            return self.int_block(1)
        elif type == 4:
            return self.int_block(2)
        elif type == 5:
            return self.int_block(3)
        elif type == 6:
            return self.int_block(4)
        elif type == 7:
            return self.int_block(5)
        elif type == 8:
            return self.int_block(6)
        elif type == 9:
            return self.int_block(7)
        elif type == 10:
            return self.int_block(8)
        elif type == 11:
            return self.read_float4()
        elif type == 12:
            return self.read_float8()
        elif type == 13:
            return self.string_block(1)
        elif type == 14:
            return self.string_block(2)
        elif type == 15:
            return self.string_block(3)
        elif type == 16:
            return self.string_block(4)
        elif type == 17:
            return self.string_block(5)
        elif type == 18:
            return self.string_block(6)
        elif type == 19:
            return self.string_block(7)
        elif type == 20:
            return self.string_block(8)
        elif type == 21:
            return self.dict_block(1)
        elif type == 22:
            return self.dict_block(2)
        elif type == 23:
            return self.dict_block(3)
        elif type == 24:
            return self.dict_block(4)
        elif type == 25:
            return self.list_block(1)
        elif type == 26:
            return self.list_block(2)
        elif type == 27:
            return self.list_block(3)
        elif type == 28:
            return self.list_block(4)
        elif type == 29:
            return self.unix_timestamp()
        elif type == 30:
            return self.windows_timestamp()
        elif type == 31:
            return self.duration()
        elif type & 0b10000000:
            return self.read_list(type & 0b01111111)
        elif type & 0b01000000:
            return self.read_str(type & 0b00111111)
        elif type & 0b00100000:
            return self.read_dict(type & 0b00011111)
        else:
            raise ValueError("Invalid type byte " + hex(type))

    def int_to_block(
        self, value: int, identifier: bool = True
    ) -> Tuple[bytes, int]:
        """
        This method returns a block for a integer value.
        """

        length = int_byte_length(value)

        if identifier:
            if length <= 4 and value < 0:
                return b"\5" + (-1 * value).to_bytes(4), 5
            elif length <= 8 and value < 0:
                return b"\x09" + (-1 * value).to_bytes(8), 9
            elif length == 1:
                return b"\3" + value.to_bytes(length), 2
            elif length == 2:
                return b"\4" + value.to_bytes(length), 3
            elif length == 3 or length == 4:
                return b"\6" + value.to_bytes(4), 5
            elif length == 5:
                return b"\7" + value.to_bytes(length), 6
            elif length == 6:
                return b"\x08" + value.to_bytes(length), 7
            elif length == 7 or length == 8:
                return b"\x0a" + value.to_bytes(8), 9

        return value.to_bytes(length), length

    def write_block_size(
        self, element: Json, base: int, bytemap: Dict[int, bytes]
    ) -> Tuple[bytes, bool]:
        """
        This method returns a block size and a boolean
        to represent the usage of base.
        """

        length = len(element)
        if base > length:
            return (base | length).to_bytes(), True

        value, value_length = self.int_to_block(length, False)
        return bytemap[value_length] + value, False

    def string_to_block(self, value: str) -> bytes:
        """
        This method returns a block for a string value.
        """

        value = value.encode(self.encoding)
        block_length, _ = self.write_block_size(
            value,
            0b01000000,
            {
                1: b"\x0d",
                2: b"\x0e",
                3: b"\x0f",
                4: b"\x10",
                5: b"\x11",
                6: b"\x12",
                7: b"\x13",
                8: b"\x14",
            },
        )
        return block_length + value

    def list_dump(self, value: List[Json], data: bytearray) -> None:
        """
        This method dumps a Json like list into binary format.
        """

        block_length, _ = self.write_block_size(
            value,
            0b10000000,
            {1: b"\x19", 2: b"\x1a", 3: b"\x1b", 4: b"\x1c"},
        )
        data.extend(block_length)

        for item in value:
            self.dumps_data(item, data)

    def dict_dump(self, value: Dict[str, Json], data: bytearray) -> None:
        """
        This method dumps a Json like dict into binary format.
        """

        block_length, _ = self.write_block_size(
            value,
            0b00100000,
            {1: b"\x15", 2: b"\x16", 3: b"\x17", 4: b"\x18"},
        )
        data.extend(block_length)

        for key, item in value.items():
            self.dumps_data(key, data)
            self.dumps_data(item, data)

    def float_dump(self, data: float) -> bytes:
        """
        This function dumps the float value.
        """

        if is_float4(data):
            return b"\x0b" + pack("f", data)
        else:
            return b"\x0c" + pack("d", data)

    def dumps_data(self, data: Json, data_dump: bytearray) -> None:
        """
        This method encodes Json like data in binary format.
        """

        if isinstance(data, dict):
            self.dict_dump(data, data_dump)
        elif isinstance(data, list):
            self.list_dump(data, data_dump)
        elif isinstance(data, str):
            data_dump.extend(self.string_to_block(data))
        elif isinstance(data, float):
            data_dump.extend(self.float_dump(data))
        elif data is False:
            data_dump.append(2)
        elif data is True:
            data_dump.append(1)
        elif isinstance(data, int):
            value, _ = self.int_to_block(data)
            data_dump.extend(value)
        elif data is None:
            data_dump.append(0)
        elif isinstance(data, datetime):
            data_dump.extend(self.unix_datetime_to_dump(data))
        elif isinstance(data, datetime):
            data_dump.extend(self.windows_datetime_to_dump(data))
        elif isinstance(data, timedelta):
            data_dump.extend(self.duration_dump(data))
        else:
            raise TypeError(
                "Invalid type to dump: "
                + type(data).__name__
                + " "
                + repr(data)
            )

    def duration_dump(self, value: timedelta) -> bytes:
        """
        This function dumps a timedelta (duration) to data bytes.
        """

        microseconds = (
            value.days * 86_400_000_000  # 1 day = 86400 seconds
            + value.seconds * 1_000_000
            + value.microseconds
        )
        return b"\x1f" + microseconds.to_bytes(8, signed=True)

    def unix_datetime_to_dump(self, value: datetime) -> bytes:
        """
        This function dumps a datetime to unix data bytes.
        """

        return b"\x1d" + int(value.timestamp()).to_bytes(4)

    def windows_datetime_to_dump(self, value: datetime) -> bytes:
        r"""
        This function dumps a datetime to windows data bytes.

        >>> BinaryJsonFormat.windows_datetime_to_dump(None, datetime(2025, 6, 22))
        b'\x1e\x01\xdb\xe2\xf7\xd5>p\x00'
        >>>
        """

        timestamp = int((value.timestamp() + epoch_difference) * 10_000_000)
        return b"\x1e" + timestamp.to_bytes(8)


class BinaryJsonRpcResponseFormat(BinaryJsonFormat):
    """
    This class implements the binary JSON RPC response format for a call.
    """

    def __init__(
        self,
        id_: int,
        error: bool,
        content: Json,
        encoding: str = "latin1",
        get_content: Callable = None,
    ):
        self.call_id = id_
        self.status = error
        self.content = content

        self.encoding = encoding
        self.get_content = get_content

        self.headers = ResponseHeaders(error)

    @classmethod
    def from_bytes(
        cls: type, data: bytes, get_content: Callable = None
    ) -> BinaryJsonRpcResponseFormat:
        r"""
        This method builds an instance for this class from data.

        >>> r = BinaryJsonRpcResponseFormat.from_bytes(b'\x80\x03\x05"Dcode\x04\x7fXGmessageOInvalid Request')
        >>> r.call_id
        5
        >>> r.headers
        ResponseHeaders(error=True)
        >>> r.status
        True
        >>> r.content
        {'code': 32600, 'message': 'Invalid Request'}
        >>>
        """

        self = cls(None, None, None)
        self.data_view = memoryview(data)
        headers = self.headers = ResponseHeaders.from_bytes(self.data_view)
        self.data_view = self.data_view[1:]

        if get_content:
            self.get_content = get_content

        self.status = headers.error
        self.call_id = self.read_next_element()
        if not isinstance(self.call_id, int):
            raise ValueError("Invalid data to parse call id")
        self.content = self.read_next_element()

        return self

    def to_bytes(self) -> bytes:
        r"""
        This method returns bytes for this instance.

        >>> BinaryJsonRpcResponseFormat(5, True, {"code": 32600, "message": "Invalid Request"}).to_bytes()
        bytearray(b'\x80\x03\x05"Dcode\x04\x7fXGmessageOInvalid Request')
        >>> BinaryJsonRpcResponseFormat(2, False, 5).to_bytes()
        bytearray(b'\x00\x03\x02\x03\x05')
        >>> BinaryJsonRpcResponseFormat(1, False, {"code": 200, "stdout": "output", "stderr": "error"}).to_bytes()
        bytearray(b'\x00\x03\x01#Dcode\x03\xc8FstdoutFoutputFstderrEerror')
        >>> BinaryJsonRpcResponseFormat(1, False, [{"code": 200, "stdout": "output", "stderr": "error"}, {"code": 200, "stdout": "output", "stderr": "error"}]).to_bytes()
        bytearray(b'\x00\x03\x01\x82#Dcode\x03\xc8FstdoutFoutputFstderrEerror#Dcode\x03\xc8FstdoutFoutputFstderrEerror')
        >>>
        """

        data = bytearray()
        data.append(self.headers.to_byte())

        if self.call_id is not None:
            value, _ = self.int_to_block(self.call_id)
            data.extend(value)
        else:
            self.dumps_data(None, data)

        self.dumps_data(self.content, data)
        return data


class BinaryJsonRpcRequestFormat(BinaryJsonFormat):
    """
    This class implements the binary JSON RPC request format for a call.
    """

    def __init__(
        self,
        method: Union[int, str],
        args: Union[None, List[Json]],
        kwargs: Union[None, Dict[str, Json]],
        interface_version: int = None,
        encoding: str = "latin1",
        id_: int = None,
        auth: Json = None,
        get_content: Callable = None,
    ):
        self.args = args
        self.params = None
        self.kwargs = kwargs
        self.method = method
        self.encoding = encoding
        self.interface_version = interface_version
        self.call_id = id_
        self.auth = auth

        if args is None:
            self.params = kwargs
        elif kwargs is None:
            self.params = args

        self.get_content = get_content

        self.headers = RequestHeaders(
            True,
            interface_version is not None,
            args is not None and kwargs is not None,
            id_ is not None,
            auth is not None,
        )

    def asdict(self) -> Dict[str, Json]:
        """
        This method returns the JSON RPC from this instance.

        >>> BinaryJsonRpcRequestFormat('test', [1, 2, 3], {'a': 'a'}, id_=1).asdict()
        {'jsonrpc': 'py2.0', 'method': 'test', 'id': 1, 'args': [1, 2, 3], 'kwargs': {'a': 'a'}}
        >>>
        """

        if self.params is not None:
            out = {
                "jsonrpc": "2.0",
                "method": self.method,
                "params": self.params,
            }
        else:
            out = {"jsonrpc": "py2.0", "method": self.method}

        if self.call_id is not None:
            out["id"] = self.call_id

        if self.params is not None:
            if self.args is not None:
                out["params"] = self.params
        else:
            if self.args is not None:
                out["args"] = self.args

            if self.kwargs is not None:
                out["kwargs"] = self.kwargs

        return out

    @classmethod
    def from_bytes(
        cls: type, data: bytes, get_content: Callable = None
    ) -> BinaryJsonRpcRequestFormat:
        r"""
        This method builds an instance for this class from data.

        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\xc0\x03\x05\r\x03abc\x19\x03\x03\x01\x03\x02\x03\x03')
        >>> rpc.headers
        RequestHeaders(binary=True, has_version=True, py_json_rpc=False, has_id=False, has_auth=False)
        >>> rpc.interface_version
        5
        >>> rpc.method
        'abc'
        >>> rpc.params
        [1, 2, 3]
        >>> rpc.args
        [1, 2, 3]
        >>> rpc.kwargs
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\r\x03abc\x15\x03\r\x01a\x03\x01\r\x01b\x03\x02\r\x01c\x03\x03')
        >>> rpc.headers
        RequestHeaders(binary=True, has_version=False, py_json_rpc=False, has_id=False, has_auth=False)
        >>> rpc.method
        'abc'
        >>> rpc.params
        {'a': 1, 'b': 2, 'c': 3}
        >>> rpc.args
        >>> rpc.kwargs
        {'a': 1, 'b': 2, 'c': 3}
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\xa0\x03\xff\x19\x03\x03\x01\x03\x02\x03\x03\x15\x03\r\x01a\x03\x01\r\x01b\x03\x02\r\x01c\x03\x03')
        >>> rpc.headers
        RequestHeaders(binary=True, has_version=False, py_json_rpc=True, has_id=False, has_auth=False)
        >>> rpc.method
        255
        >>> rpc.params
        >>> rpc.args
        [1, 2, 3]
        >>> rpc.kwargs
        {'a': 1, 'b': 2, 'c': 3}
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\xff\x19\x04\x0c\x1f\x85\xebQ\xb8\x1e\t@\x0c\xa3R]\x88\xf9#\t@\x19\x01\x03\x01\x15\x01\x03\x01\x03\x02')
        >>> rpc.headers
        RequestHeaders(binary=True, has_version=False, py_json_rpc=False, has_id=False, has_auth=False)
        >>> rpc.method
        255
        >>> rpc.params
        [3.14, 3.1425657895545824, [1], {1: 2}]
        >>> rpc.args
        [3.14, 3.1425657895545824, [1], {1: 2}]
        >>> rpc.kwargs
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\xff\x15\x01\x03\x01\x19\x05\x03\x01\x19\x01\x03\x00\x15\x02\x03\x02\x03\x03\x01\r\x03abc\x00\x02')
        >>> rpc.headers
        RequestHeaders(binary=True, has_version=False, py_json_rpc=False, has_id=False, has_auth=False)
        >>> rpc.method
        255
        >>> rpc.params
        {1: [1, [0], {2: 3, True: 'abc'}, None, False]}
        >>> rpc.args
        >>> rpc.kwargs
        {1: [1, [0], {2: 3, True: 'abc'}, None, False]}
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\xc0\x03\x05Cabc\x83\x03\x01\x03\x02\x03\x03')
        >>> rpc.headers
        RequestHeaders(binary=True, has_version=True, py_json_rpc=False, has_id=False, has_auth=False)
        >>> rpc.interface_version
        5
        >>> rpc.method
        'abc'
        >>> rpc.params
        [1, 2, 3]
        >>> rpc.args
        [1, 2, 3]
        >>> rpc.kwargs
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80Cabc#Aa\x03\x01Ab\x03\x02Ac\x03\x03')
        >>> rpc.headers
        RequestHeaders(binary=True, has_version=False, py_json_rpc=False, has_id=False, has_auth=False)
        >>> rpc.method
        'abc'
        >>> rpc.params
        {'a': 1, 'b': 2, 'c': 3}
        >>> rpc.args
        >>> rpc.kwargs
        {'a': 1, 'b': 2, 'c': 3}
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\xa0\x03\xff\x83\x03\x01\x03\x02\x03\x03#Aa\x03\x01Ab\x03\x02Ac\x03\x03')
        >>> rpc.headers
        RequestHeaders(binary=True, has_version=False, py_json_rpc=True, has_id=False, has_auth=False)
        >>> rpc.method
        255
        >>> rpc.params
        >>> rpc.args
        [1, 2, 3]
        >>> rpc.kwargs
        {'a': 1, 'b': 2, 'c': 3}
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\xff\x84\x0c\x1f\x85\xebQ\xb8\x1e\t@\x0c\xa3R]\x88\xf9#\t@\x81\x03\x01!\x03\x01\x03\x02')
        >>> rpc.headers
        RequestHeaders(binary=True, has_version=False, py_json_rpc=False, has_id=False, has_auth=False)
        >>> rpc.method
        255
        >>> rpc.params
        [3.14, 3.1425657895545824, [1], {1: 2}]
        >>> rpc.args
        [3.14, 3.1425657895545824, [1], {1: 2}]
        >>> rpc.kwargs
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\xff!\x03\x01\x85\x03\x01\x81\x03\x00"\x03\x02\x03\x03\x01Cabc\x00\x02')
        >>> rpc.headers
        RequestHeaders(binary=True, has_version=False, py_json_rpc=False, has_id=False, has_auth=False)
        >>> rpc.method
        255
        >>> rpc.params
        {1: [1, [0], {2: 3, True: 'abc'}, None, False]}
        >>> rpc.args
        >>> rpc.kwargs
        {1: [1, [0], {2: 3, True: 'abc'}, None, False]}
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\x00\x81\x1dhW+`')
        >>> rpc.headers
        RequestHeaders(binary=True, has_version=False, py_json_rpc=False, has_id=False, has_auth=False)
        >>> rpc.method
        0
        >>> rpc.params
        [datetime.datetime(2025, 6, 22, 0, 0)]
        >>> rpc.args
        [datetime.datetime(2025, 6, 22, 0, 0)]
        >>> rpc.kwargs
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\x00\x81\x1f\x00\x00\x00e\xd7\x12W\xf4')
        >>> rpc.params
        [datetime.timedelta(days=5, seconds=5400, microseconds=500)]
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\x00\x81\x1e\x01\xdb\xe2\xf7\xd5>p\x00')
        >>> rpc.args
        [datetime.datetime(2025, 6, 22, 0, 0)]
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\x01\x80')
        >>> rpc.method
        1
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x04\x01\x00\x80')
        >>> rpc.method
        256
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x05\x00\x00\x00\x01\x80')
        >>> rpc.method
        -1
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x06\x01\x00\x00\x00\x80')
        >>> rpc.method
        16777216
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x07\x01\x00\x00\x00\x00\x80')
        >>> rpc.method
        4294967296
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x08\x01\x00\x00\x00\x00\x00\x80')
        >>> rpc.method
        1099511627776
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\t\x01\x00\x00\x00\x00\x00\x00\x00\x80')
        >>> rpc.method
        -72057594037927936
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\n\x01\x00\x00\x00\x00\x00\x00\x00\x80')
        >>> rpc.method
        72057594037927936
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\r\x01a\x80')
        >>> rpc.method
        'a'
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x0e\0\x01a\x80')
        >>> rpc.method
        'a'
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x0f\0\0\x01a\x80')
        >>> rpc.method
        'a'
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x10\0\0\0\x01a\x80')
        >>> rpc.method
        'a'
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x11\0\0\0\0\x01a\x80')
        >>> rpc.method
        'a'
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x12\0\0\0\0\0\x01a\x80')
        >>> rpc.method
        'a'
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x13\0\0\0\0\0\0\x01a\x80')
        >>> rpc.method
        'a'
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x14\0\0\0\0\0\0\0\x01a\x80')
        >>> rpc.method
        'a'
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\0\x15\1\0\0')
        >>> rpc.params
        {None: None}
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\0\x16\0\1\0\0')
        >>> rpc.params
        {None: None}
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\0\x17\0\0\1\0\0')
        >>> rpc.params
        {None: None}
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\0\x18\0\0\0\1\0\0')
        >>> rpc.params
        {None: None}
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\0\x19\1\0')
        >>> rpc.params
        [None]
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\0\x1a\0\1\0')
        >>> rpc.params
        [None]
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\0\x1b\0\0\1\0')
        >>> rpc.params
        [None]
        >>> rpc = BinaryJsonRpcRequestFormat.from_bytes(b'\x80\x03\0\x1c\0\0\0\1\0')
        >>> rpc.params
        [None]
        >>>
        """

        self = cls(None, None, None, None)
        data_view = memoryview(data)
        headers = self.headers = RequestHeaders.from_bytes(data_view)
        self.data_view = data_view[1:]

        if get_content:
            self.get_content = get_content

        if headers.has_version:
            self.interface_version = self.read_next_element()
            if not isinstance(self.interface_version, int):
                raise ValueError("Invalid data to parse interface version")

        if headers.has_id:
            self.call_id = self.read_next_element()
            if not isinstance(self.call_id, int):
                raise ValueError("Invalid data to parse call id")

        if headers.has_auth:
            self.auth = self.read_next_element()

        self.method = self.read_next_element()
        if not isinstance(self.method, (str, int)):
            raise ValueError("Invalid data to parse method name or id")

        if headers.py_json_rpc:
            self.loads_pyparams()
        else:
            self.load_params()

        return self

    def loads_pyparams(self) -> None:
        """
        This method parses arguments and keywords arguments data (bytes)
        to a list and a dict.
        """

        self.args = self.read_next_element()
        self.kwargs = self.read_next_element()

        if not isinstance(self.args, (list, NoneType)):
            raise ValueError("Invalid data to parse arguments")
        elif not isinstance(self.kwargs, (dict, NoneType)):
            raise ValueError("Invalid data to parse keywords arguments")

    def load_params(self) -> None:
        """
        This method parses arguments data (bytes) to JSON.
        """

        self.params = self.read_next_element()
        if isinstance(self.params, (list, NoneType)):
            self.args = self.params
        elif isinstance(self.params, (dict, NoneType)):
            self.kwargs = self.params
        else:
            raise ValueError(
                "Invalid type byte " + repr(self.params.__class__.__name__)
            )

    def to_bytes(self) -> bytes:
        r"""
        This method returns bytes for this instance.

        >>> BinaryJsonRpcRequestFormat('abc', [1, 2, 3], None, 5).to_bytes()
        bytearray(b'\xc0\x03\x05Cabc\x83\x03\x01\x03\x02\x03\x03')
        >>> BinaryJsonRpcRequestFormat('abc', None, {'a': 1, 'b': 2, 'c': 3}).to_bytes()
        bytearray(b'\x80Cabc#Aa\x03\x01Ab\x03\x02Ac\x03\x03')
        >>> BinaryJsonRpcRequestFormat(255, [1, 2, 3], {'a': 1, 'b': 2, 'c': 3}).to_bytes()
        bytearray(b'\xa0\x03\xff\x83\x03\x01\x03\x02\x03\x03#Aa\x03\x01Ab\x03\x02Ac\x03\x03')
        >>> BinaryJsonRpcRequestFormat(255, [3.14, 3.1425657895545824, [1], {1: 2}], None).to_bytes()
        bytearray(b'\x80\x03\xff\x84\x0c\x1f\x85\xebQ\xb8\x1e\t@\x0c\xa3R]\x88\xf9#\t@\x81\x03\x01!\x03\x01\x03\x02')
        >>> BinaryJsonRpcRequestFormat(255, None, {1: [1, [0], {2: 3, True: "abc"}, None, False]}).to_bytes()
        bytearray(b'\x80\x03\xff!\x03\x01\x85\x03\x01\x81\x03\x00"\x03\x02\x03\x03\x01Cabc\x00\x02')
        >>> BinaryJsonRpcRequestFormat(2 ** 0, [], None).to_bytes()
        bytearray(b'\x80\x03\x01\x80')
        >>> BinaryJsonRpcRequestFormat(2 ** 8, [], None).to_bytes()
        bytearray(b'\x80\x04\x01\x00\x80')
        >>> BinaryJsonRpcRequestFormat(-1, [], None).to_bytes()
        bytearray(b'\x80\x05\x00\x00\x00\x01\x80')
        >>> BinaryJsonRpcRequestFormat(2 ** 24, [], None).to_bytes()
        bytearray(b'\x80\x06\x01\x00\x00\x00\x80')
        >>> BinaryJsonRpcRequestFormat(2 ** 32, [], None).to_bytes()
        bytearray(b'\x80\x07\x01\x00\x00\x00\x00\x80')
        >>> BinaryJsonRpcRequestFormat(2 ** 40, [], None).to_bytes()
        bytearray(b'\x80\x08\x01\x00\x00\x00\x00\x00\x80')
        >>> BinaryJsonRpcRequestFormat(2 ** 56 * -1, [], None).to_bytes()
        bytearray(b'\x80\t\x01\x00\x00\x00\x00\x00\x00\x00\x80')
        >>> BinaryJsonRpcRequestFormat(2 ** 56, [], None).to_bytes()
        bytearray(b'\x80\n\x01\x00\x00\x00\x00\x00\x00\x00\x80')
        >>> BinaryJsonRpcRequestFormat(0, [datetime(2025, 6, 22)], None).to_bytes()
        bytearray(b'\x80\x03\x00\x81\x1dhW+`')
        >>> BinaryJsonRpcRequestFormat(0, [timedelta(days=5, hours=1, minutes=30, microseconds=500)], None).to_bytes()
        bytearray(b'\x80\x03\x00\x81\x1f\x00\x00\x00e\xd7\x12W\xf4')
        >>> BinaryJsonRpc(0, [False] * 127, None).to_bytes()[3] == 0xff
        True
        >>> BinaryJsonRpc(0, [False] * 128, None).to_bytes()[3:5]
        bytearray(b'\x19\x80')
        >>> BinaryJsonRpc(0, [False] * 256, None).to_bytes()[3:6]
        bytearray(b'\x1a\x01\x00')
        >>> BinaryJsonRpc(0, [False] * 65536, None).to_bytes()[3:7]
        bytearray(b'\x1b\x01\x00\x00')
        >>> BinaryJsonRpc(0, [False] * 16777216, None).to_bytes()[3:8]
        bytearray(b'\x1c\x01\x00\x00\x00')
        >>> BinaryJsonRpc("a" * 63, [], None).to_bytes()[1] == 0x7f
        True
        >>> BinaryJsonRpc("a" * 64, [], None).to_bytes()[1:3]
        bytearray(b'\r@')
        >>> BinaryJsonRpc("a" * (2 ** 8), [], None).to_bytes()[1:4]
        bytearray(b'\x0e\x01\x00')
        >>> BinaryJsonRpc("a" * (2 ** 16), [], None).to_bytes()[1:5]
        bytearray(b'\x0f\x01\x00\x00')
        >>> BinaryJsonRpc("a" * (2 ** 24), [], None).to_bytes()[1:6]
        bytearray(b'\x10\x01\x00\x00\x00')
        >>> BinaryJsonRpc("a" * (2 ** 32), [], None).to_bytes()[1:7]
        bytearray(b'\x11\x01\x00\x00\x00\x00')
        >>> BinaryJsonRpc("a" * (2 ** 40), [], None).to_bytes()[1:8]
        bytearray(b'\x12\x01\x00\x00\x00\x00\x00')
        >>> BinaryJsonRpc("a" * (2 ** 48), [], None).to_bytes()[1:9]
        bytearray(b'\x13\x01\x00\x00\x00\x00\x00\x00')
        >>> BinaryJsonRpc("a" * (2 ** 56), [], None).to_bytes()[1:10]
        bytearray(b'\x14\x01\x00\x00\x00\x00\x00\x00\x00')
        >>> BinaryJsonRpc(0, None, {x: True for x in range(31)}).to_bytes()[3] == 0x3f
        True
        >>> BinaryJsonRpc(0, None, {x: True for x in range(32)}).to_bytes()[3:5]
        bytearray(b'\x15 ')
        >>> BinaryJsonRpc(0, None, {x: True for x in range(256)}).to_bytes()[3:6]
        bytearray(b'\x16\x01\x00')
        >>> BinaryJsonRpc(0, None, {x: True for x in range(65536)}).to_bytes()[3:7]
        bytearray(b'\x17\x01\x00\x00')
        >>> BinaryJsonRpc(0, None, {x: True for x in range(16777216)}).to_bytes()[3:8]
        bytearray(b'\x18\x01\x00\x00\x00')
        >>> 
        """

        data = bytearray()
        data.append(self.headers.to_byte())

        if self.headers.has_version:
            value, _ = self.int_to_block(self.interface_version)
            data.extend(value)

        if self.headers.has_id:
            value, _ = self.int_to_block(self.call_id)
            data.extend(value)

        if self.headers.has_auth:
            self.dumps_data(self.auth, data)

        if isinstance(self.method, str):
            data.extend(self.string_to_block(self.method))
        elif isinstance(self.method, int):
            value, _ = self.int_to_block(self.method)
            data.extend(value)
        else:
            raise TypeError("Invalid method type (only int or str is allowed)")

        if self.headers.py_json_rpc:
            self.list_dump(self.args, data)
            self.dict_dump(self.kwargs, data)
        else:
            self.dumps_data(self.params, data)

        return data


class AsyncServer:
    """
    This class implements a basic asynchronous TCP server.
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def start(self) -> None:
        """
        This method start the asynchronous TCP server.
        """

        server = await start_server(self.handle_client, self.host, self.port)

        async with server:
            await server.serve_forever()

    async def handle_client(
        reader: StreamReader, writer: StreamWriter
    ) -> None:
        """
        This method gets data and parses it from socket.
        """

        while not reader.at_eof():
            first_byte = await reader.readexactly(1)
            format_ = get_rpc_format(first_byte)

            if FORMATS.BINARY == format_:
                data = first_byte + await reader.read(65535)
            elif FORMATS.JSON == format_:
                data = first_byte + await reader.readline()
            elif FORMATS.CSV == format_:
                data = (
                    first_byte
                    + await reader.readline()
                    + await reader.readline()
                )
            elif FORMATS.XML == format_:
                raise NotImplementedError("XML parsing is not implemented yet")

            response = loading_classes[format_].handle_request_data(data)
            writer.write(response)
            await writer.drain()

        writer.close()
        await writer.wait_closed()


def int_byte_length(n: int) -> int:
    """
    This function returns the int length.
    """

    if n == 0:
        return 1

    negative = n < 0
    if negative:
        n = abs(n)

    length = 0
    while n:
        n >>= 8
        length += 1
    return length


def get_lengths(data: Json) -> Iterator[int]:
    """
    This generator yields all length in Json data.
    """

    lengths = {}

    if isinstance(data, dict):
        yield len(data)
        for key, value in data.items():
            yield from get_lengths(key)
            yield from get_lengths(value)

    elif isinstance(data, list):
        yield len(data)
        for item in enumerate(data):
            yield from get_lengths(item)

    elif isinstance(data, str):
        yield len(data)

    elif isinstance(data, int):
        yield int_byte_length(data)

    return lengths


from math import isnan, isinf


def is_float4(value: float) -> bool:
    """
    This function returns True when float can
    be encoded on 4 bytes.

    >>> is_float4(3.1425657895545824)
    False
    >>>
    """

    if isnan(value) or isinf(value):
        return True

    FLOAT32_MAX = 3.4028235e38
    FLOAT32_MIN = -FLOAT32_MAX

    if value > FLOAT32_MAX or value < FLOAT32_MIN:
        return False

    return value == unpack("f", pack("f", value))[0]


class FORMATS(IntEnum):
    JSON = 0
    CSV = 1
    XML = 2
    BINARY = 3


loading_classes = {
    FORMATS.JSON.value: PyJsonRpcServer,
    FORMATS.CSV.value: PyCsvRpcServer,
    FORMATS.XML.value: NotImplemented,
    FORMATS.BINARY.value: BinaryJsonRpc,
}


def get_rpc_format(first_byte: bytes) -> IntEnum:
    """
    This function returns the format from the first character.
    """

    if first_byte == b"{":
        return FORMATS.JSON
    elif first_byte == b'"':
        return FORMATS.CSV
    elif first_byte == b"<":
        return FORMATS.XML
    elif first_byte[0] & 0b10000000:
        return FORMATS.BINARY
    else:
        raise ValueError("Invalid format: invalid first byte")


response_parse_error = Response(
    "2.0", None, error=Error(-32700, "Parse error")
)
response_invalid_request = Response(
    "2.0", None, error=Error(-32600, "Invalid Request")
)
response_method_not_found = Response(
    "2.0", None, error=Error(-32601, "Method not found")
)
response_invalid_params = Response(
    "2.0", None, error=Error(-32602, "Invalid params")
)
response_internal_error = Response(
    "2.0", None, error=Error(-32603, "Internal error")
)

errors = {
    -32700: response_parse_error,
    -32600: response_invalid_request,
    -32601: response_method_not_found,
    -32602: response_invalid_params,
    -32603: response_internal_error,
}

errors.update(
    {
        x: Response("2.0", None, error=Error(-32603, "Server error"))
        for x in range(-32000, -32099, -1)
    }
)

if __name__ == "__main__":
    from doctest import testmod

    testmod()
