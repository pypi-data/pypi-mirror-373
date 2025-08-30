import logging
import importlib
from typing import Optional, Dict, List, Any, Type, Tuple

import requests
from requests.exceptions import HTTPError
from requests.exceptions import InvalidJSONError
from pydantic import BaseModel
from pydantic import ValidationError

from . import slurm_response
from . import slurm_endpoints
from ...errors import RemoteHttpError
from ...errors import RemoteSlurmError
from ...errors import raise_chained_errors

logger = logging.getLogger(__name__)


def validated_slurm_request(
    method: str,
    base_url: str,
    path: str,
    path_params: Optional[Dict[str, str]] = None,
    query_params: Optional[Dict[str, str]] = None,
    json: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    raise_http_error: bool = True,
    **kwargs,
) -> BaseModel:
    """
    Sends an HTTP request and convert the response to the appropriate Pydantic model.

    :param method: HTTP method to use for the request (e.g., "GET", "POST").
    :param base_url: The base URL to which the path is appended.
    :param path: The specific API path for the request (e.g., "/slurm/v0.0.38/job/{job_id}").
    :param path_params: A dictionary of path parameters to be substituted in the path.
    :param query_params: A dictionary of query parameters.
    :param json: A dictionary to represent the JSON body for POST/PUT requests.
    :param headers: A dictionary to represent the header for the request.
    :param raise_http_error: Raise `RemoteHttpError`.
    :param kwargs: Additional parameters to be passed to the `requests.request()` call.
    :return: A Pydantic model instance of the HTTP request response.
    :raises ValueError: If header keys are missing or response validation failed.
    :raises RemoteHttpError: The HTTP request status indicates an error.
    """
    if path_params:
        path_params = {k: str(v) for k, v in path_params.items()}
        url = base_url + path.format(**path_params)
    else:
        url = base_url + path

    if query_params:
        query_params = {k: str(v) for k, v in query_params.items()}

    _request_validate_headers(method, path, headers=headers)

    _warn_invalid_request_parameters(
        method, path, path_params=path_params, query_params=query_params, body=json
    )

    response = requests.request(
        method, url, params=query_params, json=json, headers=headers, **kwargs
    )

    response_model = _request_parse_response(method, path, response)

    _request_response_handling(
        method, url, response, response_model, raise_http_error=raise_http_error
    )

    return response_model


def slurm_request(
    method: str, base_url: str, path: str, headers: Optional[Dict] = None, **kwargs
) -> Any:
    """
    Sends an HTTP request and JSON decode the request.

    :param method: HTTP method to use for the request (e.g., "GET", "POST").
    :param base_url: The base URL to which the path is appended.
    :param path: The specific API path for the request (e.g., "/openapi").
    :param headers: A dictionary to represent the header for the request.
    :param kwargs: Additional parameters to be passed to the `requests.request()` call.
    :return: JSON decoded result.
    :raises ValueError: If header keys are missing or response decoding failed.
    :raises RemoteHttpError: The HTTP request status indicates an error.
    """
    _request_validate_headers(method, path, headers=headers)

    url = base_url + path
    response = requests.request(method, url, headers=headers, **kwargs)

    try:
        response.raise_for_status()
    except HTTPError as e:
        raise RemoteHttpError(f"{method} {path} failed") from e

    try:
        return response.json()
    except InvalidJSONError:
        raise ValueError(
            f"{method} {path} response decoding failed: {response.text}"
        ) from None


def parse_version(version: str) -> Tuple[int, int, int]:
    """
    Parse a version string into a tuple of integers.

    :param version: A version string in the format 'vX.X.X'.
    :return: A tuple representing the version (X, X, X).
    :raises ValueError: When the version string is badly formatted.
    """
    try:
        version_tuple = tuple(map(int, version.lstrip("v").split(".")))
        assert len(version_tuple) == 3
        return version_tuple
    except (ValueError, TypeError, AssertionError):
        raise ValueError(
            f"Invalid slurm version '{version}'. The format must be 'vX.X.X'"
        ) from None


def create_version(version: Tuple[int, int, int]) -> str:
    """
    Create a version string from a tuple of integers.

    :param version: A tuple representing the version (X, X, X).
    :return: A version string in the format 'vX.X.X'.
    """
    return f"v{'.'.join(map(str, version))}"


def _request_validate_headers(
    method: str,
    path: str,
    headers: Optional[Dict] = None,
) -> None:
    """
    Sends an HTTP request and converts the response to the appropriate Pydantic model.

    :param method: HTTP method to use for the request (e.g., "GET", "POST").
    :param path: The specific API path for the request (e.g., "/slurm/v0.0.38/job/{job_id}").
    :param headers: The request headers.
    :raises ValueError: If header keys are missing.
    """
    if not headers:
        raise ValueError(f"{method} {path}: No header provided")
    for key in ("X-SLURM-USER-NAME", "X-SLURM-USER-TOKEN"):
        if not headers.get(key):
            raise ValueError(f"{method} {path}: Missing header key '{key}'")


def _warn_invalid_request_parameters(
    method: str,
    path: str,
    path_params: Optional[Dict[str, str]],
    query_params: Optional[Dict[str, str]],
    body: Optional[Dict],
) -> None:
    """
    Validate HTTP request parameters and log warning when not valid.

    :param method: HTTP method to use for the request (e.g., "GET", "POST").
    :param path: The specific API path for the request (e.g., "/slurm/v0.0.38/job/{job_id}").
    :param path_params: A dictionary of path parameters to be substituted in the path.
    :param query_params: A dictionary of query parameters.
    :param body: A dictionary to represent the JSON body for POST/PUT requests.
    """

    model_class = _load_request_model(method, path, "path")
    _warn_invalid_data(
        path_params,
        model_class,
        f"{method} {path}: invalid path parameters. Submit request anyway.",
    )

    model_class = _load_request_model(method, path, "query")
    _warn_invalid_data(
        query_params,
        model_class,
        f"{method} {path}: invalid query parameters. Submit request anyway.",
    )

    model_class = _load_request_model(method, path, "body")
    _warn_invalid_data(
        {"content": body},
        model_class,
        f"{method} {path}: invalid request body. Submit request anyway.",
    )


def _warn_invalid_data(data: Any, model_class: Type[BaseModel], message: str) -> None:
    """
    Validate data and log warning when not valid.

    :param data: Data to be validated
    :param model_class: Pydantic model with which to validate the data.
    :param message: Warning message in addition to the validation errors.
    """
    try:
        if data is None:
            _ = model_class()
        else:
            _ = model_class.model_validate(data)
    except ValidationError as e:
        logger.warning(_compose_validation_message(e, message))


def _request_parse_response(
    method: str,
    path: str,
    response: requests.Response,
) -> BaseModel:
    """
    Sends an HTTP request and converts the response to the appropriate Pydantic model.

    :param method: HTTP method to use for the request (e.g., "GET", "POST").
    :param path: The specific API path for the request (e.g., "/slurm/v0.0.38/job/{job_id}").
    :param response: Response from HTTP request.
    :return: A Pydantic model instance of the HTTP request response.
    :raises ValueError: Pydantic model validation failed.
    """
    response_class = _load_request_model(
        method, path, str(response.status_code), "default"
    )

    # JSON decoding

    try:
        response_data = response.json()
    except InvalidJSONError:
        raise ValueError(
            f"{method} {path} response decoding failed: {response.text}"
        ) from None

    data_to_validate = {"content": response_data}

    # Pydantic validation (validation failure allowed)

    try:
        return response_class.model_validate(data_to_validate).content
    except ValidationError as e:
        message = f"{method} {path}: invalid response. Try removing invalid items."
        logger.warning(_compose_validation_message(e, message))
        validation_errors = e.errors()

    # Remove invalid items.
    #
    # Response models have only optional fields (see `force_optional=True`
    # in the model generation script) despite some being required
    # in the OpenAPI spec. We do this for best effort response handling.
    # Any field could be abscent and an AttributeError will be raised.

    data_to_validate = _remove_invalid_items(data_to_validate, validation_errors)

    # Pydantic validation (no validation failure allowed)
    try:
        return response_class.model_validate(data_to_validate).content
    except ValidationError as e:
        message = f"{method} {path}: invalid response."
        raise ValueError(_compose_validation_message(e, message)) from None


def _compose_validation_message(exc: ValidationError, message: str) -> str:
    validation_error = str(exc).replace("\n", "\n ")
    return f"{message}\n {validation_error}\n"


def _remove_invalid_items(data: Any, validation_errors: List[Dict[str, Any]]) -> Any:
    """
    Removes invalid items from the data based on the error details.

    :param data: The data that may contain invalid items (usually the parsed response).
    :param validation_errors: The list of error details returned by Pydantic.
    :return: The data with invalid items removed.
    """
    invalid_paths = {tuple(error["loc"]): error for error in validation_errors}
    return _recursive_remove(data, (), invalid_paths)


def _recursive_remove(data: Any, path: tuple, invalid_paths: set) -> Any:
    """
    Recursively removes invalid items from nested data.

    :param data: The data (dict/list) to process.
    :param path: The path to the field to remove.
    :param invalid_paths: A set of paths that should be removed.
    :return: The data with invalid items removed.
    """
    if isinstance(data, dict):
        data_copy = {}
        for key, value in data.items():
            new_path = path + (key,)
            if new_path in invalid_paths:
                logger.debug(
                    "Remove key %s from path %s", key, ".".join(map(str, path))
                )
            else:
                data_copy[key] = _recursive_remove(value, new_path, invalid_paths)
        return data_copy

    if isinstance(data, list):
        data_copy = []
        for index in range(len(data)):
            new_path = path + (index,)
            if new_path in invalid_paths:
                logger.debug(
                    "Remove index %s from path %s", index, ".".join(map(str, path))
                )
            else:
                data_copy.append(
                    _recursive_remove(data[index], new_path, invalid_paths)
                )
        return data_copy

    return data


def _request_response_handling(
    method: str,
    path: str,
    response: requests.Response,
    response_model: BaseModel,
    raise_http_error: str,
):
    """
    Handle the HTTP response.

    :param method: HTTP method to use for the request (e.g., "GET", "POST").
    :param url: HTTP URL.
    :param response: Response from HTTP request.
    :param response_model: Pydantic model of the response data.
    :param raise_http_error: Raise `RemoteHttpError`.
    :raises RemoteHttpError: The HTTP request status indicates an error.
    """
    for warning in slurm_response.slurm_warning_messages(method, path, response_model):
        logger.warning(warning)

    errors, suffix = slurm_response.slurm_error_messages(response_model)
    errors = [RemoteSlurmError(msg) for msg in errors]

    try:
        response.raise_for_status()
    except HTTPError as e:
        errors.append(e)

    if errors:
        if raise_http_error:
            errors.append(RemoteHttpError(f"{method} {path} failed{suffix}"))
            raise_chained_errors(errors)
        else:
            logger.error(
                "%s %s failed%s\n %s",
                method,
                path,
                suffix,
                "\n ".join(map(str, errors)),
            )


def _load_request_model(
    method: str, path: str, field: str, default_field: Optional[str] = None
) -> Type[BaseModel]:
    """
    Load the Pydantic model class for an endpoint field.

    :param method: HTTP method to use for the request (e.g., "GET", "POST").
    :param path: The specific API path for the request (e.g., "/slurm/v0.0.38/job/{job_id}").
    :param field: Endpoint field name.
    :param default_field: Default field name when it does not exist.
    :return: A Pydantic model class.
    :raises KeyError: Endpoint or endpoint field is not supported.
    """
    try:
        module_name, model_to_class_name = slurm_endpoints.ENDPOINTS[(method, path)]
    except KeyError:
        raise KeyError(f"{method} {path} is not supported") from None

    if field not in model_to_class_name and default_field:
        field = default_field

    try:
        class_name = model_to_class_name[field]
    except KeyError:
        raise KeyError(
            f"Field '{field}' is not supported for {method} {path}"
        ) from None

    module = _load_module(module_name)
    return getattr(module, class_name)


def _load_module(module_name: str) -> BaseModel:
    """
    :param module_name:
    :raises KeyError: Endpoint is not supported.
    """
    return importlib.import_module(f".{module_name}", package=__package__)
