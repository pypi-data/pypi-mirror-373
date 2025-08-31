import datetime

from .generaltypes import __itemList__, HttpBody
from .ioutils import save_json

import json
import base64
from enum import Enum
from typing import Dict, List
from types import SimpleNamespace
import math


class uuRestMethod(Enum):
    """

    """
    GET = "GET"
    POST = "POST"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

    def __str__(self):
        if self == uuRestMethod.GET:
            return "GET"
        elif self == uuRestMethod.POST:
            return "POST"
        elif self == uuRestMethod.OPTIONS:
            return "OPTIONS"
        elif self == uuRestMethod.HEAD:
            return "HEAD"
        elif self == uuRestMethod.PUT:
            return "PUT"
        elif self == uuRestMethod.DELETE:
            return "DELETE"
        elif self == uuRestMethod.PATCH:
            return "PATCH"
        else:
            return "UNKNOWN"


class JsonObject(SimpleNamespace):
    """
    Class which can be initialized from dictionary and can be converted back to dictionary
    """   
    def __init__(self, dictionary, **kwargs):
        """
        Initializes JsonObject from dictionary
        Allows users to access dictionary items as object properties
        Can parse dictionaries like this:{"b": 2, "a": 1, 
        "%$@$*&@#%*& @%@#% - ": "None", "c": {"d": 3, "e": [4, [5, [[6]]],
        {"test": "test"}]}, "f": [7, None, {"property": None}, 9]}
        :param dictionary: dictionary to be converted to uuJsonObject
        :param kwargs: additional arguments to be passed to SimpleNamespace
        """
        def _init_list(items: list):
            # helper function to initialize list
            result = []
            for item in items:
                if isinstance(item, dict):
                    result.append(JsonObject(item))
                elif isinstance(item, list):
                    result.append(_init_list(item))
                else:
                    result.append(item)
            return result
                    
        # Initialize parent class
        super().__init__(**kwargs)
        # remember order of attributes
        self.__attr_original_order__ = []
        # for each item in dictionary
        for key, value in dictionary.items():
            # remember order of attributes
            self.__attr_original_order__.append(key)
            # if value is dictionary then convert it to uuJsonObject
            if isinstance(value, dict):
                self.__setattr__(key, JsonObject(value))
            # if value is list then convert each item in list
            elif isinstance(value, list):
                new_value = _init_list(value)
                self.__setattr__(key, new_value)
            # otherwise just set the value
            else:
                self.__setattr__(key, value)
    
    def _list_to_dict(self, items: list, force_convert_properties_to_str: bool = False) -> list:
        """
        Converts list of uuJsonObject to list of uuDict
        :param items:   list of uuJsonObject
        :return:        list of uuDict
        """
        result = []
        for item in items:
            if isinstance(item, JsonObject):
                result.append(item.to_dict(force_convert_properties_to_str=force_convert_properties_to_str))
            elif isinstance(item, list):
                result.append(self._list_to_dict(item, force_convert_properties_to_str=force_convert_properties_to_str))
            else:
                result.append(item if not force_convert_properties_to_str else str(item))
        return result
    
    def to_dict(self, force_convert_properties_to_str: bool = False):
        """
        Converts uuJsonObject to uuDict
        :return:
        """
        result = {}
        property_names = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        for property_name in property_names:
            property = getattr(self, property_name)
            if isinstance(property, JsonObject):
                result[property_name] = property.to_dict(force_convert_properties_to_str=force_convert_properties_to_str)
            elif isinstance(property, list):
                result[property_name] = self._list_to_dict(property, force_convert_properties_to_str=force_convert_properties_to_str)
            elif isinstance(property, dict):
                result[property_name] = uuDict(property)
            else:
                result[property_name] = property if not force_convert_properties_to_str else str(property)
        # reorder attributes to original order
        final_result = {}
        for key in self.__attr_original_order__:
            if key in result.keys():
                final_result[key] = result[key]
                del result[key]
        for key, value in result.items():
            final_result[key] = value
        return final_result
    
    # def to_uuDict(self, force_convert_properties_to_str: bool = False) -> 'uuDict':
    #     """
    #     Converts uuJsonObject to uuDict
    #     :return:
    #     """
    #     return uuDict(self.to_dict(force_convert_properties_to_str=force_convert_properties_to_str))
    
def test_uuJsonObject():
    mydict = {"b": 2, "a": 1, "%$@$*&@#%*& @%@#% - ": "None", "c": {"d": 3, "e": [4, [5, [[6]]], {"test": "test"}]}, "f": [7, None, {"property": None}, 9]}
    print("\nOriginal mydict:")
    print(mydict)
    j = JsonObject(mydict)
    print("\nuuJsonObject j:")
    print(j)
    print("\nj.c.e[2].test:")
    print(j.c.e[2].test)
    print("\nmydict and below j.to_dict():")
    d = j.to_dict()
    print(mydict)
    print(d)
    print("\nd == mydict")
    print(d == mydict)
    j2 = JsonObject(d)
    print("\nuuJsonObject j2 from d:")
    print(j2)
    print("append 10 to j2.c.e[1][1]:")
    j2.c.e[1][1].append(10)
    j2.c.e[1][1].append(10)
    d2 = j2.to_dict()
    print("\nj2.to_dict():")
    print(d2)
    print("\nd2 == mydict")
    print(d2 == mydict)


class uuDict(dict):
    # def __init__(self, value: dict | None = None):
    #     super(uuDict, self).__init__(value if value is not None else {})

    def __init__(self, *args, **kwargs):
        super(uuDict, self).__init__(*args, **kwargs)

    def parse(self) -> JsonObject:
        return JsonObject(self)

    def save(self, filename: str, encoding: str = 'utf-8'):
        save_json(self, filename, encoding=encoding)

    def to_dict(self) -> dict:
        return dict(self)

    def __str__(self):
        return safe_convert_to_str(self, formatted=False)


def repeat_letter(value: str = "", letter: str = "#"):
    delta = len(value) % 2
    half_len_of_value = math.floor(len(value) / 2)
    result_left_len = 32 - half_len_of_value - delta
    result_right_len = 32 - half_len_of_value
    result = ""
    result += letter * result_left_len
    result += f'{value}'
    result += letter * result_right_len
    return "# " + result + "\n"


def raise_exception(message: str | dict, setup: Dict) -> dict:
    if setup["raise_exception_on_error"]:
        raise Exception(str(message))
    if isinstance(message, str):
        message = {"__error__": message}
    return message


# def dict_to_str(value: dict, formatted: bool = False) -> str:
#     if formatted:
#         return json.dumps(value, indent=4, ensure_ascii=False)
#     return json.dumps(value)


# def str_to_dict(value: str) -> dict:
#     return json.loads(value)


def shorten_text(value: str | None,
                 max_lines_from_beginning: int | None = None, max_letters_from_beginning: int | None = None,
                 max_lines_to_end: int | None = None, max_letters_to_end: int | None = None) -> str | None:
    """
    Shortens text if it is too long. It keeps specified number of lines and letters from the beginning
    and specified number of lines and letters from the end of the text. The middle part is replaced by "..."
    :param value: text to be shortened
    :param max_lines_from_beginning: maximum number of lines to keep from the beginning. Default is 25
    :param max_letters_from_beginning: maximum number of letters to keep from the beginning. Default is 700
    :param max_lines_to_end: maximum number of lines to keep from the end. Default is 15
    :param max_letters_to_end: maximum number of letters to keep from the end. Default is 300
    :return: shortened text
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise Exception(f'Parameter "value" must be a string in shorten_text function but it is type of "{str(type(value))}"')
    # setup default values
    max_lines_b = max_lines_from_beginning if max_lines_from_beginning is not None else 25
    max_letters_b = max_letters_from_beginning if max_letters_from_beginning is not None else 700
    max_lines_e = max_lines_to_end if max_lines_to_end is not None else 15
    max_letters_e = max_letters_to_end if max_letters_to_end is not None else 300
    # split lines into array
    lines = value.split("\n")
    len_lines = len(lines)
    # if there is no need to shorten the text then return the original value
    if len_lines <= max_lines_b + max_lines_e and len(value) <= max_letters_b + max_letters_e:
        return value
    # get text from the beginning
    result_b = ""
    total_letters_b = 0
    # will stop after the specified amount of lines
    lines_b = lines[:min(max_lines_b, len_lines)]
    for line in lines_b:
        len_line = len(line)
        # will stop after the specified amount of letters
        if total_letters_b + len_line > max_letters_b:
            result_b += line[:max_letters_b - total_letters_b]
            result_b += "\n"
            break
        # add line
        total_letters_b += len_line
        result_b += line + "\n"
    # get text from the end
    result_e = ""
    total_letters_e = 0
    # will stop after the specified amount of lines
    lines_e = lines[max(0, len_lines - max_lines_e):]
    for line in reversed(lines_e):
        len_line = len(line)
        # will stop after the specified amount of letters
        if total_letters_e + len_line > max_letters_e:
            result_e = line[-(max_letters_e - total_letters_e):] + "\n" + result_e
            # determine indentation of the last line
            line_len = len(line)
            spaces_from_the_beginning = line_len - len(line.lstrip())
            result_e = " " * spaces_from_the_beginning + result_e
            break
        # add line
        total_letters_e += len_line
        result_e = line + "\n" + result_e
    # combine beginning, separator and end and return the result
    separator = "|   " * 16
    result = result_b + separator + "\n" + result_e
    return result


def test_shorten_text():
    text = ""
    for i in range(1, 101):
        text += f'This is line number {i}. ' + 'A' * 100 + '\n'
    print(text)
    print("--------------------------------------------------")
    print(shorten_text(text))
    print("--------------------------------------------------")
    print(shorten_text(text, max_lines_from_beginning=10))
    print(shorten_text(text, max_lines_from_beginning=1))
    print("--------------------------------------------------")
    print(shorten_text(text, max_letters_from_beginning=300))
    print("--------------------------------------------------")
    print(shorten_text(text, max_lines_to_end=3))
    print("--------------------------------------------------")
    print(shorten_text(text, max_letters_to_end=150))
    print("--------------------------------------------------")
    print(shorten_text(text, max_lines_from_beginning=10, max_letters_from_beginning=300,
                       max_lines_to_end=5, max_letters_to_end=150))
    print("--------------------------------------------------")




def _safe_str_to_dict(value: str, encoding: str = 'utf-8') -> uuDict:
    """
    Converts str to dict. First tries to convert str to json.
    If it fails it returns dict with plain text
    :param value:
    :return:
    """
    try:
        result = json.loads(value)
        # if result is instance of list
        # replaces list with object containing itemList
        # ["item1", "item2] is replace by {"itemList": ["item1", "item2]}
        if isinstance(result, list):
            result = uuDict({__itemList__: result})
        # result is dict
        else:
            result = uuDict(result)
        return result
    except:
        return uuDict({"__text__": value})


def _safe_bytes_to_dict(value: bytes, encoding: str = 'utf-8') -> uuDict:
    """
    Converts bytes to dict. First tries to convert bytes to json.
    If it fails it tries to convert bytes to string.
    If it fails it tries to convert bytes to base64.
    :param value:
    :param encoding:
    :return:
    """
    try:
        result = value.decode(encoding=encoding)
        return _safe_str_to_dict(result)
    except:
        return uuDict({"__base64__": base64.b64encode(value).decode()})


def convert_to_dict(value, encoding: str = 'utf:8') -> uuDict | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return uuDict(value)
    if isinstance(value, str):
        return _safe_str_to_dict(value, encoding=encoding)
    elif isinstance(value, bytes):
        return _safe_bytes_to_dict(value, encoding=encoding)
    return json.loads(value)

def safe_convert_to_dict(value, encoding: str = 'utf-8') -> uuDict:
    result = convert_to_dict(value, encoding=encoding)
    if result is None:
        return uuDict()
    return result


def convert_to_str(value: HttpBody, formatted: bool = False) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if formatted:
            return json.dumps(value, indent=4, ensure_ascii=False)
        return json.dumps(value)
    raise Exception("Unexpected type of value. Value must be either dict or json or str")


def safe_convert_to_str(value: HttpBody, formatted: bool = False) -> str:
    result = convert_to_str(value, formatted=formatted)
    if result is None:
        return ""
    return result


def duplicate_dict(value: dict) -> dict | None:
    result = convert_to_str(value)
    result = convert_to_dict(result)
    return result


def printdict(value) -> None:
    """
    Prints dictionary or string in readable format
    :param value:   Any value
    :return:        None
    """
    if value is None:
        print("None")
    elif isinstance(value, dict):
        print(json.dumps(value, indent=4, ensure_ascii=False))
    else:
        print(str(value))


def escape_text(value: str) -> str:
    """
    Escapes text in error message
    :param value:
    :return:
    """
    result = ""
    allowed_letters = '0123456789/*-+.,<>?`´\'"~!@#$%^&*()_-=[]{}:\\|abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ \t\n\r'
    result = ''
    for letter in value:
        if letter in allowed_letters:
            result += letter
        else:
            result += "~"
    return result


def timestamp() -> str:
    """
    Returns current local time in ISO format with UTC offset
    :return: string like "[2023-11-02T15:04:05 local, +02H utc]"    
    """
    local_time = datetime.datetime.now()
    utc_time = datetime.datetime.utcnow()
    delta = int(round((local_time-utc_time).seconds / 3600, 0))
    local_time = datetime.datetime(local_time.year, local_time.month, local_time.day,
                                   local_time.hour, local_time.minute, local_time.second)
    result = f"[{local_time.isoformat()} local, +{delta:02}H utc]"
    return result



def linearize_dictionary(dictionary: dict, parent_path: str = "") -> dict:
    """
    From dict structure of {"level1": {"level2": {"variable1": "value1", "variable2": "value2"}}} creates dictionary
    {"level1.level2.variable1": "value1", "level1.level2.variable2": "value2"}
    :param dictionary:
    :param parent_path:
    :return:
    """
    result = {}
    for key, value in dictionary.items():
        if isinstance(value, str) or isinstance(value, int):
            result.update({f'{parent_path}{key}': value})
        else:
            sub_dictionary = linearize_dictionary(value, f'{parent_path}{key}.')
            for skey, svalue in sub_dictionary.items():
                result.update({skey: svalue})
    return result


def dict_path_exists(item: dict, path: str, is_null_value_allowed: bool = True) -> bool:
    """
    Test if dictionary contains specific path. For example if html is written like a JSON
    the user can test if json contains element h1 like this dict_path_exists(json, "html.body.h1")
    :param item:
    :param path:
    :param is_null_value_allowed:
    :return:
    """
    stop_pos = path.find(f'.')
    # if this is the last element and there are no more dots
    # then test if the element is not None (if required) and return True
    if stop_pos < 0:
        if path in item.keys():
            if is_null_value_allowed:
                return True
            else:
                return item[path] is not None
        return path in item.keys()
    # if this is not the last element
    else:
        key = path[:stop_pos]
        remaining_path = path[stop_pos+1:]
        if key not in item.keys():
            return False
        else:
            return dict_path_exists(item[key], remaining_path)


def dict_multiple_path_exists(item: dict, paths: List[str], is_null_value_allowed: bool = True) -> bool:
    """
    Test if dictionary contains multiple paths. If all paths exists the result value is True.
    Otherwise the result value is False.
    :param item:
    :param paths:
    :param is_null_value_allowed:
    :return:
    """
    for path in paths:
        if not dict_path_exists(item, path, is_null_value_allowed):
            return False
    return True


def dict_get_item_by_path(item: dict, path: str) -> dict | object:
    """
    Gets item from dictionary by path. For example if html is written like a JSON
    the user can get element h1 like this dict_get_item_by_path(json, "html.body.h1")
    :param item: dictionary
    :param path: path to the item separated by dots (e.g. "html.body.h1")
    :return: item at the specified path or None if the path does not exist
    """
    stop_pos = path.find(f'.')
    if stop_pos < 0:
        if path not in item.keys():
            raise Exception(f'Item does not exist at path "{path}" in given ditionary.')
        return item[path]
    else:
        key = path[:stop_pos]
        remaining_path = path[stop_pos+1:]
        if key not in item.keys():
            return None
        else:
            return dict_get_item_by_path(item[key], remaining_path)


def substitute_variables(value: str, variables_dict: dict, var_begin: str = "${", var_end: str = "}") -> str:
    """
    Substitutes variables in template string with variable from dictionary
    For example if value is "Hello ${name} ${surname}" and variables_dict is {"name": "John", "surname": "Smith"}
    the result will be "Hello John Smith"
    :param value:
    :param variables_dict:
    :param var_begin:
    :param var_end:
    :return:
    """
    if not isinstance(value, str):
        return value
    result = ""
    remaining = value
    len_begin = len(var_begin)
    len_end = len(var_end)
    pos_begin = value.find(var_begin)
    while pos_begin >= 0:
        result += remaining[:pos_begin]
        remaining = remaining[pos_begin + len_begin:]
        pos_end = remaining.find(var_end)
        if pos_end <= 0:
            raise Exception(f"Cannot find \"{var_end}\" in string: {remaining}")
        variable_name = remaining[:pos_end]
        if variable_name not in variables_dict.keys():
            raise Exception(f'Variable with name "{variable_name}" in string "{value}" cannot be substituted because it  is not in dictionary {variables_dict}')
        result += variables_dict[variable_name]
        remaining = remaining[pos_end + len_end:]
        pos_begin = remaining.find(var_begin)
    result += remaining
    return result