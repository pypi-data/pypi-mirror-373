"""
uufetch
===================================

Implementation of the ultra universal fetch function similar to the 
fetch function in the Chrome, Firefox, Edge, Opera browser.
Open the browser developer tools, go to the network tab, right click on any
http request and select "copy as fetch". Paste the copied fetch command
into the python script and call the fetch function.

"""

from .generaltypes import __itemList__, HttpBody
from .common import (uuDict, repeat_letter, convert_to_str, safe_convert_to_str,
                     convert_to_dict, safe_convert_to_dict, timestamp,
                     raise_exception, duplicate_dict)
from .uucommand import uuCommand, uuDataType, get_data_type, detect_header, get_header_value, update_header


def _get_example_str() -> str:
    return "https://pypi.org/project/uufetch/"


def _is_valid_method(method: str) -> bool:
    method = method.upper()
    methods = ["GET", "POST", "OPTIONS", "HEAD", "PUT", "DELETE", "PATCH"]
    if method in methods:
        return True
    return False


def _fetch_prepare_params(url: str, request_body: HttpBody = None, 
                          setup: uuDict | dict | None = None) -> tuple[str, str, str | uuDict | None, uuDict]:
    """
    Returns url, method, body and setup from chrome fetch
    :return:
    """
    # check url
    if url is None or not isinstance(url, str):
        raise Exception(f'url must be string')

    # get setup
    if setup is None:
        setup = fetch_setup(duplicate=True)
    setup = uuDict(setup)

    # solve the case when only url is specified
    if request_body is None:
        return url, "GET", None, setup

    # solve the case when only url is specified
    if isinstance(request_body, str):
        return url, "GET", request_body, setup

    if isinstance(request_body, dict):
        request = safe_convert_to_dict(request_body)
        request_body = convert_to_dict(request.case_insensitive_get_value("body"))
        # process body from chrome fetch
        if request_body is not None:
            temp_body = request_body
            temp_body_data_type = get_data_type(temp_body)
            # if body is json then set body as dict
            if temp_body_data_type == uuDataType.__json__:
                request_body = temp_body
            # otherwise if body is not a str then raise exception
            elif temp_body_data_type != uuDataType.__text__:
                raise Exception(f'Unknown data type of "body" element in "request_body" parameter.')
        # get method
        if request.case_insensitive_find_key("method") is None:
            raise Exception(f'Parameter "method" must exist in the request_body but it is not.\n{str(request)}. '
                            f'If the first argument of the "fetch" fuction is a string (which is the case) '
                            f'the second argument must be either null or a dictionary containing "method" element '
                            f'for example "method": "GET", or "method": "POST".\n\nIt is assumed the "fetch" function was copied'
                            f'from chrome browser using "copy as fetch" item in the network popup menu. See {_get_example_str()}')
        method = str(request.case_insensitive_get_value("method")).strip().upper()
        if not _is_valid_method(method):
            raise_exception(f'Method "{method}" is not a valid http method. Try to use "GET" or "POST".', setup=setup)
        # switch headers
        if request.case_insensitive_find_key("headers") is not None:
            setup["http_headers"] = request.case_insensitive_get_value("headers")
        return url, method, request_body, setup
    raise Exception(f"fetch was called using invalid combination of arguments. See {_get_example_str()}")


# null is typically used in the fetch export
null = None


_fetch_setup_global_vars = uuDict({
    # Will raise exception if error occurs. Default value is True. Default value can be modified using fetch_global_setup(...)
    "raise_exception_on_error": False,
    # timeout: How long to wait for the http, https response. Default value is 120. Default value can be modified using fetch_global_setup(...)
    "timeout": 120,
    # if verbose is true then fetch will automatically print out result into the console output
    "verbose_level": 3,
    # following http headers will be sent during fetch request
    "http_headers": {
        "accept": "*/*;q=0.9",
        "accept-language": "*;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=1",
        "sec-ch-ua-mobile": "?0"
    }
})
_fetch_setup_global_vars.indentation = 4
_fetch_setup_global_vars["verbose_level"] = 3 if __debug__ else 0
# make fetch_setup_global_vars available globally 
globals()["fetch_setup_global_vars"] = _fetch_setup_global_vars


# def fetch_setup(raise_exception_on_error: bool or None = None, timeout: int or None = None, verbose: bool or None = None):
def fetch_setup(duplicate: bool = False) -> uuDict:
    """
    Gets a copy of fetch setup dictionary
    :return:
    """
    result: uuDict = globals()["fetch_setup_global_vars"]
    if duplicate:
        result = uuDict(duplicate_dict(result))
    return result


def call(url: str, method: str | None = None, body: HttpBody = None, setup: dict | None = None) -> uuCommand:
    # check parameters
    method = str(method).strip().upper()
    if method is None and body is None:
        method = "GET"
    if method is None and body is not None:
        method = "POST"
    if not isinstance(method, str):
        raise Exception(f'argument "method" must be a string but it is type of "{str(type(method))}"')
    if body is not None and not isinstance(body, dict) and not isinstance(body, str):
        raise Exception(f'argument "body" must be a dict or str or None but it is type of "{str(type(body))}"')
    if setup is None:
        setup = fetch_setup(duplicate=True)
    if not isinstance(setup, dict):
        raise Exception(f'argument "setup" must be a dict but it is type of "{str(type(body))}"')
    # if verbose then print header
    if setup["verbose_level"] >= 1:
        print(repeat_letter(value=f' call ').rstrip())
    if setup["verbose_level"] >= 3:
        verbose_message = ""
        verbose_message += repeat_letter(value=f' INPUTS ', letter='-')
        verbose_message += repeat_letter(value=f' {timestamp()} ', letter='-')
        arguments = {"url": url, "method": method, "body": body, "setup": setup}
        verbose_message += safe_convert_to_str(arguments, dict_indent=4) + "\n"
        print(verbose_message)
    # call command
    result = uuCommand(url=url, method=method, request_body=body, setup=setup)
    return result


def fetch(url: str, body: HttpBody = None, setup: dict | None = None) -> uuCommand:
    """
    Calls rest api url and returns response.
    Fetch command is typically copied directly from the Chrome browser
    :param url: Contains url string or dictionary (json) containing url, method and optionally a token for example {"url": "...", "method": "POST", "token": "..."}
    :param method: "GET" or "POST"
    :param body:
    :param setup:
    :return:
    """
    new_url, new_method, new_body, new_setup = _fetch_prepare_params(url=url, request_body=body, setup=setup)
    # if verbose then print info
    if new_setup["verbose_level"] >= 3:
        verbose_message = ""
        arguments = {"url": url, "body": body, "setup": setup}
        verbose_message += repeat_letter(value=f' fetch ')
        verbose_message += repeat_letter(value=f' INPUTS ', letter='-')
        verbose_message += repeat_letter(value=f' {timestamp()} ', letter='-')
        verbose_message += safe_convert_to_str(arguments, dict_indent=4) + "\n"
        verbose_message += repeat_letter(value=' TRIGGERING CALL(...) ', letter='-')
        verbose_message += f"Triggering \"call\" function. fetch() is always translated to call()\n"
        print(verbose_message)
    result = call(url=new_url, method=new_method, body=new_body, setup=new_setup)
    return result


def translate_fetch(url: str, body: HttpBody = None) -> str:
    """
    Translate fetch command into call command and print generated source code
    :param url:
    :param body:
    :return:
    """
    url, method, body, setup = _fetch_prepare_params(url=url, request_body=body)
    result = ""
    # generate code
    # setup url and method
    result += f'url = "{url}"\n'
    result += f'method = "{method}"\n'
    # setup body
    if body is None:
        result += f'body = None\n'
    elif isinstance(body, str):
        result += f'body = """{body}"""\n'
    elif isinstance(body, dict):
        result += f'body = {convert_to_str(body, dict_indent=4)}\n'
    else:
        result += f'{"__error__": "Unknown type of body"}\n'
    custom_setup = convert_to_str(setup, dict_indent=4)
    # fix boolean values in the generated code convert true/false to True/False
    if custom_setup is not None:
        custom_setup = custom_setup.replace('"raise_exception_on_error": false,', '"raise_exception_on_error": False,')
        custom_setup = custom_setup.replace('"raise_exception_on_error": true,', '"raise_exception_on_error": True,')
    # create call command
    result += f'custom_setup = {custom_setup}\n'
    result += f'response = call(url=url, method=method, body=body, setup=custom_setup)\n'
    # if verbose then print result
    if setup["verbose_level"] >= 1:
        print(result)
    return result


def smart_translate_fetch(url: str, request_body: HttpBody = None) -> str:
    url, method, body, setup = _fetch_prepare_params(url=url, request_body=request_body)
    # setup body_str
    body_str = None
    if body is not None:
        if isinstance(body, str):
            body_str = f'"{convert_to_str(body, dict_indent=4)}"'
        elif isinstance(body, dict):
            body_str = f'{convert_to_str(body, dict_indent=4)}'
        else:
            raise Exception(f'Unknown type of body in smart translate fetch command. Body must be either str or dict but it is {str(type(body))}')
    # setup authorization if the authorization header exists
    authorization = uuDict(setup["http_headers"]).case_insensitive_get_value("authorization")
    if authorization is not None:
        if not isinstance(authorization, str):
            raise Exception(f'Authorization header must be a string but it is {str(type(authorization))}')
    # generate code
    result = ""
    # if the input is like fetch("http://example.com") then translate to call(url="http://example.com")
    if body_str is None and method == "GET" and authorization is None:
        result += f'response = call(url="{url}")\n'
    # if the input is like fetch("http://example.com", setup={..."Authorization": "Bearer or Token ..."})
    # then translate to call with custom setup containing authorization header
    elif body_str is None and method == "GET" and authorization is not None:
        result += f'custom_setup = fetch_setup(duplicate=True)\n'
        result += f'custom_setup["http_headers"]["authorization"] = "{convert_to_str(authorization)}"\n'
        result += f'response = call(url="{url}", method="GET", setup=custom_setup)\n'
    # if the input is like fetch("http://example.com", "POST") then translate to call(url="http://example.com", method="POST")
    elif body_str is None and method != "GET" and authorization is None:
        result += f'response = call(url="{url}", method="{method}")'
    # if the input is like fetch("http://example.com", setup={..."Authorization": "Bearer or Token ..."})
    # then translate to call with method post and custom setup containing authorization header
    elif body_str is None and method != "GET" and authorization is not None:
        result += f'custom_setup = fetch_setup(duplicate=True)\n'
        result += f'custom_setup["http_headers"]["authorization"] = "{convert_to_str(authorization)}"\n'
        result += f'response = call(url="{url}", method="{method}", setup=custom_setup)\n'
    # if the input contains body then translate to call with body
    elif body_str is not None and authorization is None:
        result += f'body = {body_str}\n'
        result += f'response = call(url="{url}", method="{method}", payload=payload)\n'
    # if the input contains body and authorization 
    # then translate to call with body and custom setup containing authorization header
    elif body_str is not None and authorization is not None:
        result += f'custom_setup = fetch_setup(duplicate=True)\n'
        result += f'custom_setup["http_headers"]["authorization"] = "{convert_to_str(authorization)}"\n'
        result += f'body = {body_str}\n'
        result += f'response = call(url="{url}", method="{method}", body=body, setup=custom_setup)\n'
    # otherwise return None
    else:
        result = None
    # result is not None and the verbose level is at least 1 then print the generated code
    if result is not None and setup["verbose_level"] >= 1:
        print(result)
    # if result is None then fallback to translate fetch
    else:   
        result = translate_fetch(url=url, body=request_body)
    return result
