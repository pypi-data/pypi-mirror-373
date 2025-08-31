import traceback
from functools import wraps
from http import HTTPStatus
from typing import Any

from .mini_logger import MiniLogger as logger
from .utilities import camel_to_snake, snake_to_camel, to_dict, to_json

HEADERS_KEY = 'headers'
AUTHORIZATION_KEY = 'authorization'
AUTHORIZATION_PREFIX = 'Bearer '


# TODO Align those methods with typescript-sdk https://github.com/circles-zone/typescript-sdk-remote-typescript-package/blob/dev/typescript-sdk/src/utils/index.ts  # noqa: E501
# TODO Shall we create also createInternalServerErrorHttpResponse(), createOkHttpResponse() like we have in TypeScript?

# TODO: add handler wrapper?

# TODO Shall we add the word body? i.e. get_body_payload_idct_from_event()
def get_payload_dict_from_event(event: dict) -> dict:
    """Extracts params sent with payload"""
    get_payload_dict_from_event_result = to_dict(event.get('body'))
    return get_payload_dict_from_event_result


def get_path_parameters_dict_from_event(event: dict) -> dict:
    """Extracts params sent implicitly: `url/param?test=5` -> param
    (when the path is defined with /{param})"""
    get_path_parameters_dict_from_event_result = event.get("pathParameters") or {}
    return get_path_parameters_dict_from_event_result


def get_query_string_parameters_from_event(event: dict) -> dict:
    """Extracts params sent explicitly: `url/test?a=1&b=2` ->  {'a': '1', 'b': '2'}"""
    # params sent with ?a=1&b=2
    get_query_string_parameters_from_event_result = event.get("queryStringParameters") or {}
    return get_query_string_parameters_from_event_result


def get_request_parameters_from_event(event: dict) -> dict:
    """Extracts all params from the event object.
    The order of precedence is: payload > path > query string
    returns a dictionary with all the parameters, with both camelCase and snake_case keys."""
    all_parameters_dict = get_payload_dict_from_event(event)
    all_parameters_dict.update(get_path_parameters_dict_from_event(event))
    all_parameters_dict.update(get_query_string_parameters_from_event(event))
    all_parameters_dict = {camel_to_snake(key): value for key, value in all_parameters_dict.items()}
    all_parameters_dict.update({snake_to_camel(key): value for key, value in all_parameters_dict.items()})
    return all_parameters_dict


# TODO: test
def handler_decorator(logger):
    """Decorator for AWS Lambda handler functions. It wraps the handler function with logging and error handling.
    Usage:
    from python_sdk_remote.http_response import handler_decorator
    logger = ...
    @handler_decorator(logger=logger)
    def my_handler(request_parameters: dict) -> dict:
        return {"message": "Hello, World!"}"""

    def decorator(handler: callable) -> callable:
        @wraps(handler)
        def wrapper(event, context):
            handler_response = None
            try:
                logger.start(object={"event": event, "context": context})
                request_parameters = get_request_parameters_from_event(event)
                body_result: dict = handler(request_parameters)
                handler_response = create_ok_http_response(body_result)
            except Exception as e:
                handler_response = create_error_http_response(e)
            finally:
                logger.end(object={"handler_response": handler_response})
            return handler_response

        return wrapper

    return decorator


# TODO: should we auto detect user_jwt if not provided?
def create_authorization_http_headers(user_jwt: str) -> dict:
    logger.start(object={"user_jwt": user_jwt})
    # TODO check the validity of user_jwt and it is not None and raise exception, please do the same in all other functions.
    authorization_http_headers = {
        'Content-Type': 'application/json',
        'Authorization': AUTHORIZATION_PREFIX + user_jwt,
    }
    logger.end(object={"authorization_http_headers": authorization_http_headers})
    return authorization_http_headers


def get_user_jwt_from_event(event: dict) -> str:
    logger.start(object={"event": event})
    auth_header = event.get(HEADERS_KEY, {}).get(AUTHORIZATION_KEY)
    if auth_header is None:
        auth_header = event.get(HEADERS_KEY, {}).get(AUTHORIZATION_KEY.capitalize())
    user_jwt = auth_header.split(AUTHORIZATION_PREFIX)[1]
    logger.end(object={"user_jwt": user_jwt})
    return user_jwt


def create_return_http_headers() -> dict:
    logger.start()
    # Adding "Access-Control-Allow-Origin" : "*" to take care of CORS from localhost
    # TODO Do we need to add those? In which cases? try  adding crossDomain: true, to the request, 'Access-Control-Allow-Credentials': true to header  # noqa: E501
    return_http_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }
    logger.end(object={"return_http_headers": return_http_headers})
    return return_http_headers


def create_error_http_response(exception: Exception, status_code: HTTPStatus = HTTPStatus.BAD_REQUEST) -> dict:
    logger.start(object={"exception": exception})
    error_http_response = {
        "statusCode": status_code.value,
        "headers": create_return_http_headers(),
        "body": create_http_body({"error": str(exception)}),
        "traceback": traceback.format_exc()
    }
    logger.end(object={"error_http_response": error_http_response})
    return error_http_response


def create_ok_http_response(body: Any) -> dict:
    logger.start(object={"body": body})
    # TODO: test sending statusCode/headers/body inside the body
    ok_http_response = {
        "statusCode": body.get("statusCode") or HTTPStatus.OK.value,
        "headers": body.get("headers") or create_return_http_headers(),
        "body": create_http_body(body.get("body") or body)
    }
    logger.end(object={"ok_http_response": ok_http_response})
    return ok_http_response


# https://google.github.io/styleguide/jsoncstyleguide.xml?showone=Property_Name_Format#Property_Name_Format
def create_http_body(body: Any) -> str:
    # TODO console.warning() if the body is not a valid camelCase JSON
    # https://stackoverflow.com/questions/17156078/converting-identifier-naming-between-camelcase-and-underscores-during-json-seria
    logger.start(object={"body": body})
    http_body = to_json(body)
    logger.end(object={"http_body": http_body})
    return http_body
