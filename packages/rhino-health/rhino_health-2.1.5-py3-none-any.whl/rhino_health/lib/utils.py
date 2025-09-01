import functools
import logging
import sys
from typing import Union
from warnings import warn

from pydantic._internal._typing_extra import NoneType
from typing_extensions import get_args, get_origin


def url_for(base_url, endpoint):
    # Urljoin doesn't actually work correctly
    return f"{base_url.strip().rstrip('/')}/{endpoint.strip().lstrip('/')}"


class RhinoSDKException(Exception):
    """
    @autoapi False
    Use this in order to conditionally suppress stack traces
    """

    def __init__(self, original_exception):
        if isinstance(original_exception, str):
            self.original_class = self.__class__
            self.original_class_name = "RhinoSDKException"
        else:
            self.original_class = original_exception.__class__
            self.original_class_name = self.original_class.__name__
        super(RhinoSDKException, self).__init__(original_exception)

    @property
    def __name__(self):
        return self.original_class_name


def setup_traceback(old_exception_handler, show_traceback):
    def rhino_exeception_handler(error_type, error_value, traceback):
        is_rhino_exception = error_type == RhinoSDKException
        original_error_type = error_value.original_class if is_rhino_exception else error_type
        if not show_traceback and is_rhino_exception:
            print(": ".join([str(error_value.__name__), str(error_value)]))
        else:
            old_exception_handler(original_error_type, error_value, traceback)

    if hasattr(__builtins__, "__IPYTHON__") or "ipykernel" in sys.modules:
        logging.debug("Setting up IPython override")
        ipython = (
            get_ipython()
        )  # This exists in globals if we are in ipython, don't worry unresolved

        def rhino_ipython_handler(shell, error_type, error_value, tb, **kwargs):
            if not show_traceback:
                print(": ".join([str(error_value.__name__), str(error_value)]))
            else:
                shell.showtraceback((error_value.original_class, error_value, tb))

        # this registers a custom exception handler for the whole current notebook
        ipython.set_custom_exc((RhinoSDKException,), rhino_ipython_handler)
    else:
        logging.debug("Setting up default python override")
        sys.excepthook = rhino_exeception_handler


def rhino_error_wrapper(func):
    """
    Add this decorator to the top level call to ensure the traceback suppression works
    """

    @functools.wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, RhinoSDKException):
                raise
            raise RhinoSDKException(e) from e

    return wrapper_func


def alias(
    new_function,
    old_function_name,
    deprecation_warning=True,
    new_function_name=None,
    base_object="",
    is_property=False,
):
    """
    @autoapi False
    Used to alias old functions or provide convenience for users

    If this is being set to replace a self attribute or property instead of a function,
    pass IS_PROPERTY=True and immediately call the result of this function.

    Example Usages

    search_for_dataschemas_by_name = alias(
        search_for_data_schemas_by_name,
        "search_for_dataschemas_by_name",
        base_object="session.data_schema",
    )

    @property
    def get_dataschema_by_name(self):
        return alias(
            self.get_data_schema_by_name,
            "get_dataschema_by_name",
            is_property=True,
            new_function_name="get_data_schema_by_name",
            base_object="project",
        )()
    """

    def closure(*args, **kwargs):
        """
        @autoapi False
        """
        if deprecation_warning:
            new_name = new_function_name or getattr(
                new_function, "__name__", new_function.__class__.__name__
            )
            base_object_name = (
                base_object
                if isinstance(base_object, str)
                else getattr(base_object, "__name__", new_function.__class__.__name__)
            )
            base_object_string = "" if not base_object_name else f"{base_object_name}."
            function_string = "" if is_property else "()"
            warn(
                f"{base_object_string}{old_function_name}{function_string} is deprecated and will be removed in the future, please use {base_object_string}{new_name}{function_string}",
                DeprecationWarning,
                stacklevel=2,
            )
        return new_function if is_property else new_function(*args, **kwargs)

    return closure


def does_typing_annotation_accept(annotation, desired_type):
    """
    Returns if a pydantic/python type annotation accepts a given type
    """
    if not annotation:
        return False
    if desired_type is None:
        desired_type = NoneType
    field_types = []
    pending_evaluation = [annotation]
    # Internally within python typing, the type object
    # has various wrapper objects which obfuscates the actual type
    # that is defined, so we need to go down the tree of the objects
    # in order to get the actual list of types that are accepted.
    while pending_evaluation:
        _current_field_type = pending_evaluation.pop()
        # Origin is the internal python name for a "wrapping type object".
        origin_type = get_origin(_current_field_type)
        if origin_type == Union:
            pending_evaluation.extend(get_args(_current_field_type))
        elif origin_type == list:
            pending_evaluation.append(get_args(_current_field_type)[0])
        else:
            field_types.append(_current_field_type)
    return desired_type in field_types


class RhinoObjectWrapper:
    """
    @autoapi False

    Wrapper class for frozen classes because the implementation
    cannot be extended easily due to changes they made.

    Primarily for pydantic internals

    """

    def __init__(self, wrapped_object, rhino_arguments):
        """
        :param wrapped_object: Any object you want to wrap which cannot be extended because the class overrides getattr and setattr and/or uses reflection to dynamically create a new class type from code
        :param rhino_arguments: Dict[str, Any] for dynamic properties you want to be accessible from the object
        """
        object.__setattr__(self, "__wrapped_object", wrapped_object)
        object.__setattr__(self, "__rhino_arguments", rhino_arguments)

    def __getattribute__(self, attribute):
        my_class = object.__getattribute__(self, "__class__")
        # Python sometimes prepends the class name to the method instead of passing the actual method name
        if attribute.startswith(f"_{my_class.__name__}"):
            attribute = attribute.replace(f"_{my_class.__name__}", "")
        try:
            result = object.__getattribute__(self, attribute)
            return result
        except AttributeError:
            wrapped_object = object.__getattribute__(self, "__wrapped_object")
            return object.__getattribute__(wrapped_object, attribute)

    def __contains__(self, attribute):
        try:
            object.__getattribute__(self, attribute)
            return True
        except AttributeError:
            try:
                wrapped_object = object.__getattribute__(self, "__wrapped_object")
                object.__getattribute__(wrapped_object, attribute)
                return True
            except AttributeError:
                pass
        return False

    def __setattr__(self, attribute, value):
        my_class = object.__getattribute__(self, "__class__")
        # Python sometimes prepends the class name to the method instead of passing the actual method name
        if attribute.startswith(f"_{my_class.__name__}"):
            attribute = attribute.replace(f"_{my_class.__name__}", "")
        try:
            wrapped_object = object.__getattribute__(self, "__wrapped_object")
            object.__getattribute__(wrapped_object, attribute)
            object.__setattr__(wrapped_object, attribute, value)
        except AttributeError:
            object.__setattr__(self, attribute, value)
