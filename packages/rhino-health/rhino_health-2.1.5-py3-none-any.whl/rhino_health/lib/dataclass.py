import os
import time
from copy import deepcopy
from inspect import isclass
from typing import Any, Callable, List, Optional, Union
from warnings import warn

import arrow
from pydantic import BaseModel, ConfigDict, Field
from pydantic.fields import FieldInfo
from typing_extensions import Annotated, get_args, get_origin

from rhino_health.lib.utils import RhinoObjectWrapper, does_typing_annotation_accept

FORBID_EXTRA_RESULT_FIELDS = os.environ.get("RHINO_SDK_FORBID_EXTRA_RESULT_FIELDS", "").lower() in {
    "1",
    "on",
    "true",
}

RESULT_DATACLASS_EXTRA = "forbid" if FORBID_EXTRA_RESULT_FIELDS else "ignore"


class AliasResponse:
    """
    @autoapi False
    Placeholder interface for a raw_response to ensure backwards compatibility if a user uses unsupported internal methods
    """

    def __init__(self, dataclass):
        self.dataclass = dataclass

    @property
    def content(self):
        raise NotImplementedError  # TODO: No good way of handling this

    @property
    def status_code(self):
        return 200  # TODO: Placeholder

    def json(self):
        return self.dataclass.model_dump_json()

    def text(self):
        return self.json()


class UIDFieldInfo(RhinoObjectWrapper):
    """
    @autoapi False
    """

    @property
    def is_list(self):
        return self.__rhino_arguments.get("is_list", False)

    @property
    def name_field(self):
        return self.__rhino_arguments.get("name_field", None)

    @property
    def model_fetcher(self):
        return self.__rhino_arguments.get("model_fetcher", None)

    @property
    def model_property_name(self):
        return self.__rhino_arguments.get("model_property_name", None)

    @property
    def model_property_getter(self):
        return self.__rhino_arguments.get("model_property_getter", None)

    @property
    def model_property_setter(self):
        return self.__rhino_arguments.get("model_property_setter", None)


def UIDField(
    *args,
    is_list: bool = False,
    name_field: Optional[str] = None,
    model_fetcher: Optional[Callable] = None,
    model_property_name: Optional[str] = None,
    model_property_setter: Optional[Callable] = None,
    model_property_getter: Optional[Callable] = None,
    model_property_type: Optional[str] = None,
    **kwargs,
):
    """
    @autoapi False
    Returns Annotated parameters for a UIDField so we can automatically add
    getters and setters on the dataclasses.

    Note: Pydantic's Field is a method implementation and not a class so we cannot
    subclass it

    Parameters
    ----------
    alias: Optional[str]
        The key used in the JSON response sent by the Cloud API if different than the field name
    model_fetcher: Callable
        Endpoint to call to fetch the dataclass with. The function will receive the session object and uid as input parameters
    is_list: Optional[bool]
        Whether we should be processing a list of uids instead of a single uid
    name_field: Optional[str]
        Whether we want to store the name returned with the UID on this dataclass.
        If defined will store the name on the dataclass as a property matching the string.
        If not specified will use the field name with _uid and _uids replace with _name and _names respectively

        Eg
        response_payload:
        {
          "my_field_uid: {
            "name": <name>,
            "uid": <uid>
          }
        }

        class MyObject(RhinoBaseModel):
            my_field_uid = UIDField(name_field='other_name')

        MyObject().other_name will return the <name> in the response_payload
    model_property_name: Optional[str]
        Name of the property to add to get the dataclass. If not specified will use the field name with _uid and _uids removed

        Eg
        response_payload:
        {
          "my_field_uid: {
            "name": <name>,
            "uid": <uid>
          }
        }

        class MyObject(RhinoBaseModel):
            my_field_uid = UIDField(model_property_name='other_name')

        MyObject().other_name will return the Dataclass associated with the <uid> as a result of calling the model_property_getter function
    model_property_setter: Optional[Callable]
        We will automatically add properties to store the related model object for user convenience.
        If a custom override is required pass the property definition here
    model_property_getter: Optional[Callable]
        We will automatically add properties to fetch the related model object for user convenience.
        If a custom override is required pass the property definition here
        The default behavior is to call the model_fetcher function
    model_property_type: Optional[str]
        Used by the documentation generation code to display what the getter/setter takes. Not used internally.
        This should be the dataclass itself without List[type] wrap.
    Returns
    -------
    field_info: FieldInfo
        Pydantic field info
    """
    if model_fetcher is None:
        raise RuntimeError(f"Missing model_fetcher which must be specified for a UIDField.")
    # Pull out any custom arguments since pydantic will complain about extra arguments
    uid_arguments = {
        "is_list": is_list,
        "name_field": name_field,
        "model_fetcher": model_fetcher,
        "model_property_name": model_property_name,
        "model_property_getter": model_property_getter,
        "model_property_setter": model_property_setter,
    }
    field_info = Field(*args, **kwargs)
    # The custom fields need to be on the metadata, and the metadata needs to extend FieldInfo.
    # Yes it is confusing, blame pydantic
    field_info.metadata.append(UIDFieldInfo(field_info, uid_arguments))
    return field_info


class RhinoBaseModel(BaseModel):
    session: Annotated[Any, Field(exclude=True)] = None
    _trace_id: Optional[str] = None
    _persisted: bool = False

    def __init__(self, **data):
        self._handle_aliases(data)
        pre_uid_data = deepcopy(data)
        self._handle_uids(data)
        self._handle_models(data)
        self._handle_hidden(data)
        super().__init__(**data)
        self._handle_uids(
            pre_uid_data
        )  # Need to rerun again since pydantic removes the dynamic fields

    def __str__(self):
        return f"{self.__class__.__name__} {super(RhinoBaseModel, self).__str__()}"

    model_config = ConfigDict(extra=RESULT_DATACLASS_EXTRA)

    def dict(self, *args, **kwargs):
        """
        Return a dictionary representation of the data class.
        See https://docs.pydantic.dev/latest/concepts/serialization/#modelmodel_dump for available arguments
        """
        return self.model_dump(*args, **kwargs)

    def to_dict(self, *args, **kwargs):
        """
        @autoapi False

        In the event users are used to pandas
        """
        return self.dict(*args, **kwargs)

    def json(self, *args, **kwargs):
        """
        @autoapi False

        Pydantic is deprecating the name but the old name is much clearer
        """
        # TODO: Need to reverse the uids
        return self.model_dump_json(*args, **kwargs)

    def _is_v2_uid_field(self, value):
        """
        @autoapi False
        """
        return (
            isinstance(value, dict) and "uid" in value and ("name" in value or "full_name" in value)
        )

    def _add_field(self, field_name, field_value):
        """
        Adds a dynamic field to this dataclass with FIELD_NAME and FIELD_VALUE
        """
        # Cannot use setattr due to pydantic override of the attr function
        object.__setattr__(self, field_name, field_value)

    def _add_model_property(
        self,
        field_name,
        model_property_name,
        model_fetcher,
        model_property_getter,
        model_property_setter,
        is_list,
    ):
        """
        Adds a dynamic model property MODEL_PROPERTY_NAME to this dataclass with FIELD_NAME.
        If the value is not cached will call MODEL_FETCHER with session and uid to fetch the model object.

        If the value is a list then will pass the list of uids to the MODEL_FETCHER.

        If MODEL_PROPERTY_GETTER or MODEL_PROPERTY_SETTER is specified will use that instead of the default property definition.
        """
        # Note we need to use object functions instead of setattr/getattr due to pydantic internals.

        # Add the cache
        cache_name = f"_{model_property_name}"
        object.__setattr__(self, cache_name, None)

        def _generic_getter(dataclass):
            cache_value = object.__getattribute__(dataclass, cache_name)
            session = object.__getattribute__(dataclass, "session")
            uid_value = object.__getattribute__(dataclass, field_name)
            if cache_value is None:
                object.__setattr__(dataclass, cache_name, model_fetcher(session, uid_value))
            return object.__getattribute__(dataclass, cache_name)

        def _generic_setter(dataclass, dataclass_value):
            session = object.__getattribute__(dataclass, "session")
            uid_value = object.__getattribute__(dataclass, field_name)
            object.__setattr__(dataclass, cache_name, dataclass_value)
            uid_value = [d.uid for d in dataclass_value] if is_list else dataclass_value.uid
            object.__setattr__(dataclass, field_name, uid_value)

        _getter = model_property_getter or _generic_getter
        _setter = model_property_setter or _generic_setter

        model_property_function = property(fget=_getter, fset=_generic_getter)
        # Properties are assigned at the class level, pydantic class is immutable
        object_class = object.__getattribute__(self, "__class__")
        child_class = type(
            object_class.__name__, (object_class,), {model_property_name: model_property_function}
        )
        object.__setattr__(self, "__class__", child_class)

    def _handle_uids(self, data):
        """
        Handle support for UIDFields which only affects data we receive from the backend Cloud API.

        This should not be used for inputs to the backend.
        """

        for field_name, field_info in self.model_fields.items():
            # Is a field we should remap
            metadata = field_info.metadata
            if metadata and len(metadata):
                uid_field_infos = [
                    metadata for metadata in metadata if isinstance(metadata, UIDFieldInfo)
                ]
                if uid_field_infos:
                    uid_field_info = uid_field_infos[0]
                    old_key = field_info.alias or field_name
                    response_value = data.get(old_key, None)
                    uid_value = response_value
                    name_value = None
                    if uid_field_info.is_list:
                        if not isinstance(response_value, list):
                            if (
                                does_typing_annotation_accept(field_info.annotation, None)
                                and response_value is None
                            ):
                                continue
                            raise TypeError(
                                f"Expected {field_name} to be a list but received {type(response_value)} instead"
                            )
                        if len(response_value) and self._is_v2_uid_field(response_value[0]):
                            uid_value = [uid_and_name["uid"] for uid_and_name in response_value]
                            name_value = [
                                uid_and_name.get("name", uid_and_name.get("full_name"))
                                for uid_and_name in response_value
                            ]
                    elif self._is_v2_uid_field(response_value):
                        uid_value = response_value["uid"]
                        name_value = response_value.get(
                            "name", response_value.get("full_name", None)
                        )

                    # Pydantic expects the arguments to be received as the alias
                    data[field_info.alias or field_name] = uid_value
                    if (
                        RESULT_DATACLASS_EXTRA == "forbid"
                        and field_info.alias is not None
                        and field_name != field_info.alias
                    ):
                        data.pop(field_name, None)

                    # Create name property and getter
                    if name_value is not None:
                        name_field = uid_field_info.name_field or field_name.replace(
                            "_uids", "_names"
                        ).replace("_uid", "_name")
                        self._add_field(name_field, name_value)

                    # Create model property
                    model_property_name = uid_field_info.model_property_name or field_name.replace(
                        "_uid", ""
                    ).replace("_uids", "s")
                    self._add_model_property(
                        field_name=field_name,
                        model_property_name=model_property_name,
                        model_fetcher=uid_field_info.model_fetcher,
                        model_property_getter=uid_field_info.model_property_getter,
                        model_property_setter=uid_field_info.model_property_setter,
                        is_list=uid_field_info.is_list,
                    )

    def _handle_models(self, data):
        """
        Add the session variable to any child models
        """
        # TODO: Is this necessary anymore now with API v2 and no nested classes?
        # TODO Replace the detection of this to use ModelField or something of that nature.
        session = getattr(self, "session", data.get("session"))
        for field, field_attr in self.model_fields.items():
            field_type = field_attr.annotation
            # With type annotations there can be many wrapping types and there's
            # no convenience get_actual_base_class function so we need
            # to get the actual base class
            field_types = []
            pending_evaluation = [field_type]
            while pending_evaluation:
                _current_field_type = pending_evaluation.pop()
                origin = get_origin(_current_field_type)
                if origin == Union:
                    pending_evaluation.extend(get_args(_current_field_type))
                elif origin == list:
                    pending_evaluation.append(get_args(_current_field_type)[0])
                else:
                    field_types.append(_current_field_type)
            for _field_type in field_types:
                if isclass(_field_type) and issubclass(_field_type, RhinoBaseModel):
                    value = data.get(field, None)
                    if isinstance(value, list):
                        for entry in value:
                            if isinstance(entry, dict):
                                entry["session"] = session
                        break
                    elif isinstance(value, dict):
                        data[field]["session"] = session
                        break

    def _handle_aliases(self, data):
        """
        Pydantic expects the input to the data class constructor to use the kwargs for the aliases and will throw an error
        if the user provides the field name instead. This is greatly inconvenient for users of our dataclasses
        as we want to allow users to be able to use the field name or the alias.`

        If you have:
        class MyClass(BaseModel):
            my_field: Annotated[str, Field(alias="my_alias")]

        MyClass(my_field='foo') will raise an exception in base Pydantic

        This function allows the above call to work
        """
        for field_name, field_attr in self.model_fields.items():
            if field_attr.alias is not None and field_name != field_attr.alias:
                if field_name in data:
                    data[field_attr.alias] = data.get(field_name, data.get(field_attr.alias, None))
                if RESULT_DATACLASS_EXTRA == "forbid":
                    # Need to remove unaliased kwarg due to pydantic complaining
                    data.pop(field_name, None)

    def _handle_hidden(self, data):
        """
        Remove any explicitly hidden fields from the constructor of the pydantic model
        in order to not fail the Extra forbidden check.
        """
        for field_name in getattr(self.__class__, "__hidden__", []):
            if field_name in data:
                data.pop(field_name, None)

    def raw_response(self):
        warn(
            f"The SDK method you called now returns a {self.__class__.__name__} dataclass. Please update your code to use the dataclass instead. You can directly access fields on the return result, or call .dict() for a similar interface"
        )
        return AliasResponse(self)

    def parsed_response(self):
        warn(
            f"The SDK method you called now returns a {self.__class__.__name__} dataclass. Please update your code to use the dataclass instead. You can directly access fields on the return result, or call .dict() for a similar interface"
        )
        return AliasResponse(self)

    def _wait_for_completion(
        self,
        name: str,
        is_complete: bool,
        query_function: Callable,
        validation_function: Callable,
        timeout_seconds: int = 600,
        poll_frequency: int = 10,
        print_progress: bool = True,
        is_successful: Callable = lambda result: True,
        on_success: Callable = None,
        on_failure: Callable = lambda result: print("Finished with errors"),
    ):
        """
        @autoapi False

        Reusable code for waiting for pending operations to complete
        :param name: Name of the operation
        :param is_complete: Whether or not the object has finished
        :param query_function: lambda(self) -> dataclass What SDK function to call to check
        :param validation_function: lambda(old_object, new_object) -> bool whether to break checking
        :param timeout_seconds: Timeout in total seconds
        :param poll_frequency: Frequency to poll
        :param print_progress: Show progress to users
        :param is_successful: lambda(result) -> bool Whether the operation was successful
        :param on_success: lambda(result) -> None What to do on success
        :param on_failure: lambda(result) -> None What to do on failure
        :return: dataclass
        """
        if is_complete:
            return self
        if on_success is None:
            on_success = lambda result: print("Done.") if print_progress else None
        start_time = arrow.utcnow()
        timeout_time = start_time.shift(seconds=timeout_seconds)
        while arrow.utcnow() < timeout_time:
            try:
                new_result = query_function(self)
                if validation_function(self, new_result):
                    if is_successful(new_result):
                        on_success(new_result)
                    else:
                        on_failure(new_result)
                    return new_result
            except Exception as e:
                raise Exception(f"Exception in wait_for_completion() calling get_status(): {e}")
            if print_progress:
                time_elapsed = arrow.utcnow().humanize(
                    start_time, granularity=["hour", "minute", "second"], only_distance=True
                )
                print(f"Waiting for {name} to complete ({time_elapsed})")
            if poll_frequency:
                time.sleep(poll_frequency)
        raise Exception(f"Timeout waiting for {name} to complete")
