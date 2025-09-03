#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base Regscale Model"""
import copy
import hashlib
import json
import logging
import os
import threading
import warnings
from abc import ABC
from threading import RLock
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple, TypeVar, Union, cast, get_type_hints

from cacheout import Cache
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from requests import Response
from rich.progress import Progress, TaskID
from yaml import dump

from regscale.core.app.application import Application
from regscale.core.app.utils.api_handler import APIHandler, APIInsertionError, APIResponseError, APIUpdateError
from regscale.core.app.utils.app_utils import create_progress_object
from regscale.models.regscale_models.search import Search
from regscale.utils.threading import ThreadSafeList
from regscale.utils.threading.threadsafe_dict import ThreadSafeDict

# Suppress specific Pydantic warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

T = TypeVar("T", bound="RegScaleModel")

logger = logging.getLogger("regscale")


class RegScaleModel(BaseModel, ABC):
    """Mixin class for RegScale Models to add functionality to interact with RegScale API"""

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True, arbitrary_types_allowed=True)

    _x_api_version: ClassVar[str] = "1"
    _module_slug: ClassVar[str] = "model_slug"
    _module_string: ClassVar[str] = ""
    _module_slug_id_url: ClassVar[str] = "/api/{model_slug}/{id}"
    _module_slug_url: ClassVar[str] = "/api/{model_slug}"
    _module_id: ClassVar[int] = 0
    _api_handler: ClassVar[APIHandler] = None
    _parent_id_field: ClassVar[str] = "parentId"
    _unique_fields: ClassVar[List[List[str]]] = []
    _get_objects_for_list: ClassVar[bool] = False
    _get_objects_for_list_id: ClassVar[str] = "id"
    _exclude_graphql_fields: ClassVar[List[str]] = ["extra_data", "tenantsId"]
    _original_data: Optional[Dict[str, Any]] = None

    _object_cache: ClassVar[Cache] = Cache(maxsize=100000)
    _parent_cache: ClassVar[Cache] = Cache(maxsize=50000)
    _lock_registry: ClassVar[ThreadSafeDict] = ThreadSafeDict()
    _global_lock: ClassVar[threading.Lock] = threading.Lock()  # Class-level lock
    _is_disable_cache: ClassVar[Optional[bool]] = None  # Class-level cache setting

    _pending_updates: ClassVar[Dict[str, Set[int]]] = {}
    _pending_creations: ClassVar[Dict[str, Set[str]]] = {}

    id: int = 0
    extra_data: Dict[str, Any] = Field(default={}, exclude=True)
    createdById: Optional[str] = None
    lastUpdatedById: Optional[str] = None

    def __init__(self: T, *args, **data) -> None:
        """
        Initialize the RegScaleModel.

        :param T self: The instance being initialized
        :param *args: Variable length argument list
        :param **data: Arbitrary keyword arguments
        :return: None
        :rtype: None
        """
        try:
            super().__init__(*args, **data)
            # Capture initial state after initialization
            self._original_data = self.dict(exclude_unset=True)
            # Initialize cache setting if not already set
            if self.__class__._is_disable_cache is None:
                self.__class__._is_disable_cache = self.__class__._fetch_disabled_cache_setting()
            if self.__class__._is_disable_cache:
                logger.debug("cache is disabled")
        except Exception as e:
            logger.error(f"Error creating {self.__class__.__name__}: {e} {data}", exc_info=True)

    @classmethod
    def _fetch_disabled_cache_setting(cls) -> bool:
        """
        Check if caching is disabled based on the application config.

        :return: True if caching is disabled, False otherwise
        :rtype: bool
        """
        is_disabled = False
        if config := cls._get_api_handler().config:
            is_disabled = config.get("disableCache", False)
        return is_disabled

    @classmethod
    def _is_cache_disabled(cls) -> bool:
        """
        Check if caching is disabled for this class.

        :return: True if caching is disabled, False otherwise
        :rtype: bool
        """
        if cls._is_disable_cache is None:
            cls._is_disable_cache = cls._fetch_disabled_cache_setting()
        return cls._is_disable_cache

    @classmethod
    def disable_cache(cls) -> bool:
        """
        Disable caching for the model.

        :return: True if caching is disabled, False otherwise
        :rtype: bool
        """
        cls._is_disable_cache = True
        return cls._is_disable_cache

    @classmethod
    def enable_cache(cls) -> bool:
        """
        Enable caching for the model.

        :return: True if caching is enabled, False otherwise
        :rtype: bool
        """
        cls._is_disable_cache = False
        return cls._is_disable_cache

    @classmethod
    def _get_api_handler(cls) -> APIHandler:
        """
        Get or initialize the API handler.

        :return: The API handler instance
        :rtype: APIHandler
        """
        if cls._api_handler is None:
            cls._api_handler = APIHandler()
        return cls._api_handler

    def get_object_id(self) -> int:
        """
        Get the object ID.

        :return: The object ID
        :rtype: int
        """
        if not hasattr(self, "id"):
            return 0
        logger.debug(f"Getting object ID for {self.__class__.__name__} {self.id}")
        return self.id

    @classmethod
    def _get_lock(cls, cache_key: str) -> RLock:
        """
        Get or create a lock associated with a cache key.

        :param str cache_key: The cache key
        :return: A reentrant lock
        :rtype: RLock
        """
        lock = cls._lock_registry.get(cache_key)
        if lock is None:
            with cls._global_lock:  # Use a class-level lock to ensure thread safety
                lock = cls._lock_registry.get(cache_key)
                if lock is None:
                    lock = RLock()
                    cls._lock_registry[cache_key] = lock
        return lock

    @classmethod
    def _get_cache_key(cls, obj: T, defaults: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a cache key based on the object's unique fields using SHA256 hash.

        :param T obj: The object to generate a key for
        :param Optional[Dict[str, Any]] defaults: Dictionary of default values to apply to the object, defaults to None
        :return: A string representing the cache key
        :rtype: str
        """
        defaults = defaults or {}
        # Iterate over each set of unique fields
        for fields in cls.get_unique_fields():
            unique_fields = []
            # Iterate over each field in the current set of unique fields
            for field in fields:
                value = getattr(obj, field, defaults.get(field))
                if value is not None:
                    # If the value is longer than 15 characters, hash it using SHA256
                    if len(str(value)) > 15:
                        # Hash long values
                        hash_object = hashlib.sha256(str(value).encode())
                        value = hash_object.hexdigest()
                    # Append the field and its value to the unique_fields list
                    unique_fields.append(f"{field}:{value}")

            # If all fields in the current set have values, use them to generate the cache key
            if len(unique_fields) == len(fields):
                unique_string = ":".join(unique_fields)
                cache_key = f"{cls.__name__}:{unique_string}"
                return cache_key

        # Fallback if no complete set of unique fields is found, use object ID
        return f"{cls.__name__}:{obj.get_object_id()}"

    @classmethod
    def get_cached_object(cls, cache_key: str) -> Optional[T]:
        """
        Get an object from the cache based on its cache key.

        :param str cache_key: The cache key of the object
        :return: The cached object if found, None otherwise
        :rtype: Optional[T]
        """
        if cls._is_cache_disabled():
            return None
        with cls._get_lock(cache_key):
            return cls._object_cache.get(cache_key)

    @classmethod
    def cache_object(cls, obj: T) -> None:
        """
        Cache an object and update the parent cache if applicable.

        :param T obj: The object to cache
        :return: None
        :rtype: None
        """
        if cls._is_cache_disabled():
            return
        try:
            if not obj:
                return
            cache_key = cls._get_cache_key(obj)
            cls._object_cache.set(cache_key, obj)

            # Update parent cache
            cls._update_parent_cache(obj)
        except Exception as e:
            logger.error(f"Error caching object: {e}", exc_info=True)

    @classmethod
    def get_tenant_id(cls) -> Optional[int]:
        """
        Get the tenant ID from the token in init.yaml

        :return: Tenant ID
        :rtype: Optional[int]
        """
        from regscale.models.regscale_models.user import User

        user_id = cls.get_user_id()
        return User.get_tenant_id_for_user_id(user_id) if user_id else None

    @classmethod
    def get_user_id(cls) -> Optional[str]:
        """
        Get the user ID from parsing the token from REGSCALE_TOKEN envar or the token in init.yaml
        If it isn't found, fall back to the userId from the init.yaml

        :return: User ID, if available
        :rtype: str
        """
        from regscale.core.app.internal.login import parse_user_id_from_jwt

        app = Application()
        token = os.environ.get("REGSCALE_TOKEN") or app.config.get("token")
        return parse_user_id_from_jwt(app, token) or app.config.get("userId")

    @classmethod
    def _update_parent_cache(cls, obj: T) -> None:
        """
        Update the parent cache with the new or updated object.

        :param T obj: The object to add or update in the parent cache
        :return: None
        :rtype: None
        """
        if cls._is_cache_disabled():
            return
        parent_id = getattr(obj, cls._parent_id_field, None)
        parent_module = getattr(obj, "parentModule", getattr(obj, "parent_module", ""))
        if parent_id and parent_module:
            cache_key = f"{parent_id}:{cls.__name__}"
            with cls._get_lock(cache_key):
                parent_objects = cls._parent_cache.get(cache_key, [])
                # Remove the old version of the object if it exists
                parent_objects = [o for o in parent_objects if o.id != obj.id]
                # Add the new or updated object
                parent_objects.append(obj)
                cls._parent_cache.set(cache_key, parent_objects)
            logger.debug(f"Updated parent cache for {cls.__name__} with parent ID {parent_id}")

    @classmethod
    def cache_list_objects(cls, cache_key: str, objects: List[T]) -> None:
        """
        Cache a list of objects.

        :param str cache_key: The cache key
        :param List[T] objects: The objects to cache
        :return: None
        :rtype: None
        """
        if cls._is_cache_disabled():
            return
        with cls._get_lock(cache_key):
            for obj in objects:
                cls.cache_object(obj)
            cls._parent_cache.set(cache_key, objects)

    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear the object cache.

        :return: None
        :rtype: None
        """
        cls._object_cache.clear()

    @classmethod
    def delete_object_cache(cls, obj: T) -> None:
        """
        Delete an object from the cache.

        :param T obj: The object to delete from the cache
        :return: None
        :rtype: None
        """
        if cls._is_cache_disabled():
            return
        cache_key = cls._get_cache_key(obj)
        with cls._get_lock(cache_key):
            cls._object_cache.delete(cache_key)

            parent_id = getattr(obj, cls._parent_id_field, None)
            parent_module = getattr(obj, "parentModule", getattr(obj, "parent_module", ""))

            # update parent cache
            if parent_id and parent_module:
                parent_cache_key = f"{parent_id}:{obj.__class__.__name__}"
                with obj._get_lock(parent_cache_key):
                    parent_objects = [o for o in obj._parent_cache.get(parent_cache_key, []) if o.id != obj.id]
                    obj._parent_cache.set(parent_cache_key, parent_objects)

    def has_changed(self, comp_object: Optional[T] = None) -> bool:
        """
        Check if current data differs from the original data or the provided comparison object.

        :param Optional[T] comp_object: The object to compare against, defaults to None
        :return: True if the data has changed, False otherwise
        :rtype: bool
        """
        if comp_object is None:
            comp_object = self._original_data

        if not comp_object:
            return True

        current_data = self.dict(exclude_unset=True)
        for key, value in current_data.items():
            if key not in ["id", "dateCreated"] and value != comp_object.get(key):
                return True
        return False

    def show_changes(self, comp_object: Optional[T] = None) -> Dict[str, Any]:
        """
        Display the changes between the original data and the current data.

        :param Optional[T] comp_object: The object to compare, defaults to None
        :return: A dictionary of changes
        :rtype: Dict[str, Any]
        """
        if comp_object:
            original_data = comp_object.dict(exclude_unset=True)
        else:
            original_data = self._original_data

        if getattr(self, "id", 0) == 0:
            return original_data
        if not original_data:
            return {}
        current_data = self.dict(exclude_unset=True)
        changes = {
            key: {"from": original_data.get(key), "to": current_data.get(key)}
            for key in current_data
            if current_data.get(key) != original_data.get(key)  # and key != "id"
        }
        return changes

    def diff(self, other: Any) -> Dict[str, Tuple[Any, Any]]:
        """
        Find the differences between two objects

        :param Any other: The other object to compare
        :return: A dictionary of differences
        :rtype: Dict[str, Tuple[Any, Any]]
        """
        differences = {}
        for attr in vars(self):
            if getattr(self, attr) != getattr(other, attr):
                differences[attr] = (getattr(self, attr), getattr(other, attr))
        return differences

    def dict(self, exclude_unset: bool = False, **kwargs: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Override the default dict method to exclude hidden fields

        :param bool exclude_unset: Whether to exclude unset fields, defaults to False
        :return: Dictionary representation of the object
        :rtype: Dict[str, Any]
        """
        hidden_fields = set(
            attribute_name
            for attribute_name, model_field in self.__class__.model_fields.items()
            if model_field.from_field("hidden") == "hidden"
        )
        unset_fields = set(
            attribute_name
            for attribute_name, model_field in self.__class__.model_fields.items()
            if getattr(self, attribute_name, None) is None
        )
        excluded_fields = hidden_fields.union(unset_fields)
        kwargs.setdefault("exclude", excluded_fields)
        return super().model_dump(**kwargs)

    @classmethod
    def get_module_id(cls) -> int:
        """
        Get the module ID for the model.

        :return: Module ID #
        :rtype: int
        """
        return cls._module_id

    @classmethod
    def get_module_slug(cls) -> str:
        """
        Get the module slug for the model.

        :return: Module slug
        :rtype: str
        """
        return cls._module_slug

    @classmethod
    def get_module_string(cls) -> str:
        """
        Get the module name for the model.

        :return: Module name
        :rtype: str
        """
        return cls._module_string or cls.get_module_slug()

    @classmethod
    def get_unique_fields(cls) -> List[List[str]]:
        """
        Get the unique fields for the model.

        Maintains backward compatibility with old format (List[str]) while supporting
        new format (List[List[str]]).

        :return: Unique fields as a list of lists
        :rtype: List[List[str]]
        :raises DeprecationWarning: If using old format (List[str])
        """
        if not cls._unique_fields:
            return []

        # Check if the first element is a string (old format) or a list (new format)
        if isinstance(cls._unique_fields[0], str):
            import warnings

            warnings.warn(
                f"Single list of unique fields is deprecated for {cls.__name__}. "
                "Use list of lists format instead: [[field1, field2], [field3]]",
                DeprecationWarning,
                stacklevel=2,
            )
            # Convert old format to new format by wrapping in a list
            return [cls._unique_fields]  # type: ignore

        return cls._check_override()

    @classmethod
    def _check_override(cls) -> List[List[str]]:
        """
        Check if the unique fields have been overridden in the configuration.

        :raises ValueError: If the primary fields are invalid
        :return: A list of unique fields
        :rtype: List[List[str]]
        """
        sample_format = {"uniqueOverride": {"asset": ["ipAddress"]}}
        config = Application().config

        try:
            primary = config.get("uniqueOverride", {}).get(cls.__name__.lower())
            if primary:
                if not isinstance(primary, list):
                    raise ValueError(
                        f"Invalid config format in uniqueOverride.{cls.__name__.lower()}, the configuration must be in a format like so:\n{dump(sample_format, default_flow_style=False)}"
                    )
                if primary != cls._unique_fields:
                    if all(attr in cls.model_fields for attr in primary):
                        if primary not in cls._unique_fields:
                            cls._unique_fields.insert(1, primary)
                        else:
                            # Move primary to index 1 if it exists
                            cls._unique_fields.insert(1, cls._unique_fields.pop(cls._unique_fields.index(primary)))
                    else:
                        raise ValueError(
                            f"One or more invalid attribute(s) detected: {primary}, falling back on default unique fields for type: {cls.__name__.lower()}"
                        )
        except ValueError as e:
            logger.warning(e)
        return cls._unique_fields

    @classmethod
    def _get_endpoints(cls) -> ConfigDict:
        """
        Get the endpoints for the API.

        :return: A dictionary of endpoints
        :rtype: ConfigDict
        """
        endpoints = ConfigDict(  # type: ignore
            get=cls._module_slug_id_url,  # type: ignore
            insert="/api/{model_slug}/",  # type: ignore
            update=cls._module_slug_id_url,  # type: ignore
            delete=cls._module_slug_id_url,  # type: ignore
            list="/api/{model_slug}/getList",  # type: ignore
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}/{strModule}",  # type: ignore
        )
        endpoints.update(cls._get_additional_endpoints())
        return endpoints

    def __hash__(self) -> hash:
        """
        Enable object to be hashable

        :return: Hashed Vulnerability
        :rtype: hash
        """
        return hash(tuple(tuple(getattr(self, field) for field in sublist) for sublist in self.get_unique_fields()))

    def __eq__(self, other: object) -> bool:
        """
        Enable object to be equal

        :param object other: Object to compare to
        :return: Whether the objects are equal
        :rtype: bool
        """
        if not isinstance(other, type(self)):
            return NotImplemented
        return any(
            all(getattr(self, field) == getattr(other, field) for field in sublist)
            for sublist in self.get_unique_fields()
        )

    def __repr__(self) -> str:
        """
        Override the default repr method to return a string representation of the object.

        :return: String representation of the object
        :rtype: str
        """
        return f"<{self.__str__()}>"

    def __str__(self) -> str:
        """
        Override the default str method to return a string representation of the object.

        :return: String representation of the object
        :rtype: str
        """
        fields = (
            "\n  "
            + "\n  ".join(
                f"{name}={value!r},"
                for name, value in self.dict().items()
                # if value is not None
            )
            + "\n"
        )
        return f"{self.__class__.__name__}({fields})"

    def find_by_unique(self, parent_id_field: Optional[str] = None) -> Optional[T]:
        """
        Find a unique instance of the object. First tries the defined unique fields,
        then falls back to alternative matching strategies if no match is found.

        :param Optional[str] parent_id_field: The parent ID field, defaults to None
        :raises NotImplementedError: If the method is not implemented
        :raises ValueError: If parent ID is not found
        :return: The instance or None if not found
        :rtype: Optional[T]
        """
        if not self.get_unique_fields():
            raise NotImplementedError(f"_unique_fields not defined for {self.__class__.__name__}")

        parent_id = getattr(self, parent_id_field or self._parent_id_field, None)
        if parent_id is None:
            raise ValueError(f"Parent ID not found for {self.__class__.__name__}")

        parent_module = getattr(self, "parentModule", getattr(self, "parent_module", ""))
        cache_key = self._get_cache_key(self)

        with self._get_lock(cache_key):
            # Check cache first
            if cached_object := self.get_cached_object(cache_key):
                return cached_object

            # Get all instances from parent
            instances: List[T] = self.get_all_by_parent(parent_id=parent_id, parent_module=parent_module)

            # Try to find matching instance using unique fields
            for keys in self._unique_fields:
                matching_instance = next(
                    (
                        instance
                        for instance in instances
                        if all(
                            getattr(instance, field) not in [None, ""]
                            and getattr(self, field) not in [None, ""]
                            and str(getattr(instance, field)).lower() == str(getattr(self, field)).lower()
                            for field in keys
                        )
                    ),
                    None,
                )
                if matching_instance:
                    return matching_instance

        return None

    def get_or_create_with_status(self: T, bulk: bool = False) -> Tuple[bool, T]:
        """
        Get or create an instance, returning both creation status and instance.

        :param bool bulk: Whether to perform a bulk create operation, defaults to False
        :return: Tuple of (was_created, instance)
        :rtype: Tuple[bool, T]
        """
        cache_key = self._get_cache_key(self)
        with self._get_lock(cache_key):
            if cached_object := self.get_cached_object(cache_key):
                return False, cached_object

            instance = self.find_by_unique()

            if instance:
                self.cache_object(instance)
                return False, instance
            else:
                created_instance = self.create(bulk=bulk)
                self.cache_object(created_instance)
                return True, created_instance

    def get_or_create(self: T, bulk: bool = False) -> T:
        """
        Get or create an instance.

        :param bool bulk: Whether to perform a bulk create operation, defaults to False
        :return: The instance
        :rtype: T
        """
        _, instance = self.get_or_create_with_status(bulk=bulk)
        return instance

    def create_or_update(
        self: T,
        bulk_create: bool = False,
        bulk_update: bool = False,
        defaults: Optional[Dict[str, Any]] = None,
    ) -> T:
        """
        Create or update an instance.

        :param bool bulk_create: Whether to perform a bulk create, defaults to False
        :param bool bulk_update: Whether to perform a bulk update, defaults to False
        :param Optional[Dict[str, Any]] defaults: Dictionary of default values to apply to the instance if it is created, defaults to {}
        :return: The instance
        :rtype: T
        """
        _, instance = self.create_or_update_with_status(
            bulk_create=bulk_create, bulk_update=bulk_update, defaults=defaults
        )
        return instance

    def create_or_update_with_status(
        self: T,
        bulk_create: bool = False,
        bulk_update: bool = False,
        defaults: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, T]:
        """
        Create or update an instance. Use cache methods to retrieve and store instances based on unique fields.

        :param bool bulk_create: Whether to perform a bulk create, defaults to False
        :param bool bulk_update: Whether to perform a bulk update, defaults to False
        :param Optional[Dict[str, Any]] defaults: Dictionary of default values to apply to the instance if it is created, defaults to {}
        :return: The instance of the class
        :rtype: Tuple[bool, T]
        """
        logger.debug(f"Starting create_or_update for {self.__class__.__name__}: #{getattr(self, 'id', '')}")

        cache_key = self._get_cache_key(self)

        with self._get_lock(cache_key):
            # Check if the object is already in the cache
            cached_object = self.get_cached_object(cache_key)

            # If not in cache, try to find it in the database
            instance = cached_object or self.find_by_unique()

            if instance:
                # An existing instance was found (either in cache or database)
                logger.debug(f"Found {'cached' if cached_object else 'existing'} instance of {self.__class__.__name__}")
                # Update the current object's ID with the found instance's ID
                self.id = instance.id
                # If the object has a 'dateCreated' attribute, update it
                if hasattr(self, "dateCreated"):
                    self.dateCreated = instance.dateCreated  # noqa

                # Update the _original_data attribute with the instance data
                self._original_data = instance.dict(exclude_unset=True)

                # Check if the current object has any changes compared to the found instance
                if self.has_changed():
                    logger.debug(f"Instance of {self.__class__.__name__} has changed, updating")
                    # Save the changes, potentially in bulk
                    updated_instance = self.save(bulk=bulk_update)
                    # Update the cache with the new instance
                    self.cache_object(updated_instance)
                    # Return the updated instance, optionally with a flag indicating it wasn't newly created
                    return False, updated_instance

                # If no changes, return the existing instance
                return False, instance

            # No existing instance was found, so create a new one
            # apply defaults if they are provided
            if defaults:
                for key, value in defaults.items():
                    # Handle callable values by executing them
                    if callable(value):
                        value = value()
                    setattr(self, key, value)
            logger.debug(f"No existing instance found for {self.__class__.__name__}, creating new")
            created_instance = self.create(bulk=bulk_create)
            # Cache the newly created instance
            self.cache_object(created_instance)
            # Return the created instance, optionally with a flag indicating it was newly created
            return True, created_instance

    @classmethod
    def _handle_list_response(
        cls,
        response: Response,
        suppress_error: bool = False,
        override_values: Optional[Dict] = None,
        parent_id: Optional[int] = None,
        parent_module: Optional[str] = None,
    ) -> List[T]:
        """
        Handles the response for a list of items from an API call.

        This method processes the response object to extract a list of items. If the response is successful and contains
        a list of items (either directly or within a 'items' key for JSON responses), it returns a list of class
        instances created from the items. If the response is unsuccessful or does not contain any items, it logs an
        error and returns an empty list.

        :param Response response: The response object from the API call
        :param bool suppress_error: Whether to suppress error logging, defaults to False
        :param Optional[Dict] override_values: Dictionary of values to override in the response items, defaults to None
        :param Optional[int] parent_id: The ID of the parent object, if applicable, defaults to None
        :param Optional[str] parent_module: The module of the parent object, if applicable, defaults to None
        :return: A list of class instances created from the response items
        :rtype: List[T]
        """
        logger.debug(f"Handling list response with status_code {response.status_code if response else ''}")

        if cls._is_response_invalid(response):
            logger.debug("No response or status code 204, 404, or 400")
            return []

        if response.ok and response.status_code != 400:
            items = cls._extract_items(response)
            cls._apply_override_values(items, override_values)
            return cls._create_objects_from_items(items, parent_id=parent_id, parent_module=parent_module)

        cls._log_response_error(response, suppress_error)
        return []

    @staticmethod
    def _is_response_invalid(response: Response) -> bool:
        """
        Check if the response is invalid.

        :param Response response: The response object to check
        :return: True if the response is invalid, False otherwise
        :rtype: bool
        """
        # regscale is sending ok with 400 status code for some reason
        return not response or response.status_code in [204, 404]

    @staticmethod
    def _extract_items(response: Response) -> List[Dict]:
        """
        Extract items from the response.

        :param Response response: The response object to extract items from
        :return: A list of items extracted from the response
        :rtype: List[Dict]
        """
        from requests.exceptions import JSONDecodeError

        try:
            json_response = response.json()
        except JSONDecodeError:
            return []
        if isinstance(json_response, dict) and "items" in json_response:
            return json_response.get("items", [])
        return json_response

    @staticmethod
    def _apply_override_values(items: List[Dict], override_values: Optional[Dict]) -> None:
        """
        Apply override values to the items.

        :param List[Dict] items: List of items to apply override values to
        :param Optional[Dict] override_values: Dictionary of values to override in the items, defaults to None
        :rtype: None
        """
        if override_values:
            for item in items:
                for key, value in override_values.items():
                    item[key] = value

    @classmethod
    def cast_list_object(
        cls,
        item: Dict,
        parent_id: Optional[int] = None,
        parent_module: Optional[str] = None,
    ) -> T:
        """
        Cast list of items to class instances.

        :param Dict item: Item to cast to a class instance
        :param Optional[int] parent_id: The ID of the parent object, if applicable, defaults to None
        :param Optional[str] parent_module: The module of the parent object, if applicable, defaults to None
        :return: Class instance created from the item
        :rtype: T
        """
        if parent_id is not None and "parentId" in cls.model_fields and "parentId" not in item:
            item["parentId"] = parent_id
        if parent_module is not None and "parentModule" in cls.model_fields and "parentModule" not in item:
            item["parentModule"] = parent_module
        return cls._cast_object(item)

    @classmethod
    def _cast_object(cls, item: Dict) -> T:
        """
        Cast an item to a class instance.

        :param Dict item: Item to cast to a class instance
        :return: Class instance created from the item
        :rtype: T
        :raises ValidationError: If the item fails validation when creating the class instance
        :raises TypeError: If there's a type mismatch when creating the class instance
        """
        try:
            obj: T = cls(**item)
        except ValidationError as e:
            logger.error(f"Failed to cast item to {cls.__name__}: {e}", exc_info=True)
            raise e
        except TypeError as e:
            logger.error(f"Failed to cast item to {cls.__name__}: {e}", exc_info=True)
            raise
        return obj

    @classmethod
    def _create_objects_from_items(
        cls,
        items: List[Dict],
        parent_id: Optional[int] = None,
        parent_module: Optional[str] = None,
    ) -> List[T]:
        """
        Create objects from items using threading to improve performance.

        :param List[Dict] items: List of items to create objects from
        :param Optional[int] parent_id: The ID of the parent object, if applicable, defaults to None
        :param Optional[str] parent_module: The module of the parent object, if applicable, defaults to None
        :return: List of class instances created from the items
        :rtype: List[T]
        """
        from concurrent.futures import ThreadPoolExecutor

        def fetch_object(item):
            return cls.get_object(object_id=item.get(cls._get_objects_for_list_id))

        if cls._get_objects_for_list:
            with ThreadPoolExecutor(max_workers=3) as executor:
                objects: List[T] = list(executor.map(fetch_object, items))
            return [item for item in objects if item]
        return [cls.cast_list_object(item, parent_id=parent_id, parent_module=parent_module) for item in items if item]

    @classmethod
    def _log_response_error(cls, response: Response, suppress_error: bool) -> None:
        """
        Log an error message for the response.

        :param Response response: The response object to log an error for
        :param bool suppress_error: Whether to suppress error logging
        :rtype: None
        """
        if not suppress_error:
            logger.error(f"Error in response: {response.status_code}, {response.text}")

    @classmethod
    def _handle_response(cls, response: Response) -> Optional[T]:
        """
        Handles the response for a single item from an API call.

        This method processes the response object to extract a single item. If the response is successful and contains
        an item, it returns an instance of the class created from the item. If the response is unsuccessful or does not
        contain an item, it logs an error and returns None.

        :param Response response: The response object from the API call
        :return: An instance of the class created from the response item, or None if unsuccessful
        :rtype: Optional[T]
        """
        if not response or response.status_code in [204, 404]:
            return None
        if response.ok:
            return cast(T, cls(**response.json()))
        else:
            logger.error(f"Failed to get {cls.get_module_slug()} for {cls.__name__}")
            return None

    @classmethod
    def _handle_graph_response(cls, response: Dict[Any, Any], child: Optional[Any] = None) -> List[T]:
        """
        Handle graph response

        :param Dict[Any, Any] response: Response from API
        :param Optional[Any] child: Child object, defaults to None
        :return: List of RegScale model objects
        :rtype: List[T]
        """
        items = []
        for k, v in response.items():
            if hasattr(v, "items"):
                for o in v["items"]:
                    if child:
                        items.append(cast(T, cls(**o[child])))
                    else:
                        items.append(cast(T, cls(**o)))
        return items

    @classmethod
    def get_field_names(cls, use_aliases: bool = False) -> List[str]:
        """
        Get the field names for the Asset model.

        :param bool use_aliases: Whether to use aliases for the field names, defaults to False
        :return: List of field names
        :rtype: List[str]
        """
        if use_aliases:
            return [val.alias or key for key, val in cls.model_fields.items() if not key.startswith("_")]
        return [x for x in get_type_hints(cls).keys() if not x.startswith("_")]

    @classmethod
    def build_graphql_fields(cls, use_aliases: bool = False) -> str:
        """
        Dynamically builds a GraphQL query for a given Pydantic model class.

        :param bool use_aliases: Whether to use aliases for the field names, defaults to False
        :return: A string representing the GraphQL query
        :rtype: str
        """
        return "\n".join(
            x
            for x in cls.get_field_names(use_aliases=use_aliases)
            if x not in cls._exclude_graphql_fields and x != "extra_data"
        )

    @classmethod
    def get_by_parent(cls, parent_id: int, parent_module: str) -> List[T]:
        """
        Get a list of objects by parent.

        DEPRECATED: This method will be removed in future versions. Use 'get_all_by_parent' instead.

        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :return: A list of objects
        :rtype: List[T]
        """
        warnings.warn(
            "The method 'get_by_parent' is deprecated and will be removed in future versions. "
            "Use 'get_all_by_parent' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return cls.get_all_by_parent(parent_id, parent_module)

    @classmethod
    def get_all_by_parent(
        cls,
        parent_id: int,
        parent_module: Optional[str] = None,
        search: Optional[Search] = None,
    ) -> List[T]:
        """
        Get a list of objects by parent, optimized for speed.

        :param int parent_id: The ID of the parent
        :param Optional[str] parent_module: The module of the parent, defaults to None
        :param Optional[Search] search: The search object, defaults to None
        :return: A list of objects
        :rtype: List[T]
        """
        cache_key = f"{parent_id}:{cls.__name__}"

        with cls._get_lock(cache_key):
            cached_objects = cls._parent_cache.get(cache_key)
            # Check for None and empty list
            if cached_objects is not None and len(cached_objects) > 0:
                return cached_objects

            if "get_all_by_search" in cls._get_endpoints() and parent_id and parent_module and not search:
                logger.debug("Using get_all_by_search")
                search = Search(parentID=parent_id, module=parent_module)
            if search:
                objects: List[T] = cls._handle_looping_response(search)
            else:
                try:
                    endpoint = cls.get_endpoint("get_all_by_parent").format(
                        intParentID=parent_id, strModule=parent_module
                    )
                    objects: List[T] = cls._handle_list_response(
                        cls._get_api_handler().get(endpoint=endpoint), parent_id=parent_id, parent_module=parent_module
                    )
                except ValueError as e:
                    logger.error(f"Failed to get endpoint: {e}", exc_info=True)
                    objects = []

            cls.cache_list_objects(cache_key=cache_key, objects=objects)

            return objects

    @classmethod
    def _handle_looping_response(cls, search: Search, page: int = 1, page_size: int = 500) -> List[T]:
        """
        Handles the response for a list of items from an API call.

        :param Search search: The search object
        :param int page: The starting page, defaults to 1
        :param int page_size: The number of items per page, defaults to 500
        :return: A list of objects
        :rtype: List[T]
        """
        items: List[T] = []
        this_search = copy.deepcopy(search)
        this_search.page = page
        this_search.pageSize = page_size

        while True:
            data: List[T] = cls._handle_list_response(
                cls._get_api_handler().post(
                    endpoint=cls.get_endpoint("get_all_by_search"),
                    data=this_search.model_dump(),
                )
            )
            try:
                if not any(data):
                    break
            except AttributeError:
                break

            items.extend(data)
            this_search.page += 1

        return items

    @staticmethod
    def _get_additional_endpoints() -> Union[ConfigDict, dict]:
        """
        Get additional endpoints for the API.

        :return: A dictionary of additional endpoints
        :rtype: Union[ConfigDict, dict]
        """
        return ConfigDict()

    @classmethod
    def get_endpoint(cls, endpoint_type: str) -> str:
        """
        Get the endpoint for a specific type.

        :param str endpoint_type: The type of endpoint
        :raises ValueError: If the endpoint type is not found
        :return: The endpoint
        :rtype: str
        """
        endpoint = cls._get_endpoints().get(endpoint_type, "na")  # noqa
        if not endpoint or endpoint == "na":
            logger.error(f"{cls.__name__} does not have endpoint {endpoint_type}")
            raise ValueError(f"Endpoint {endpoint_type} not found")
        endpoint = str(endpoint).replace("{model_slug}", cls.get_module_slug())
        return endpoint

    @classmethod
    def _get_pending_updates(cls) -> Set[Union[int, str]]:
        """
        Get the set of pending updates for the class.

        :return: Set of pending update IDs
        :rtype: Set[Union[int, str]]
        """
        class_name = cls.__name__
        if class_name not in cls._pending_updates:
            cls._pending_updates[class_name] = set()
        return cls._pending_updates[class_name]

    @classmethod
    def _get_pending_creations(cls) -> Set[str]:
        """
        Get the set of pending creations for the class.

        :return: Set of pending creation cache keys
        :rtype: Set[str]
        """
        class_name = cls.__name__
        if class_name not in cls._pending_creations:
            cls._pending_creations[class_name] = set()
        return cls._pending_creations[class_name]

    def save(self: T, bulk: bool = False) -> T:
        """
        Save the current object, either immediately or in bulk.

        :param bool bulk: Whether to perform a bulk save operation, defaults to False
        :return: The saved object
        :rtype: T
        """
        # Check if the model has change tracking and if there are changes
        has_change_tracking = hasattr(self, "has_changed") and callable(getattr(self, "has_changed", None))
        should_save = not has_change_tracking or self.has_changed()

        if should_save:
            if bulk:
                logger.debug(f"Adding {self.__class__.__name__} {self.id} to pending updates")
                self._get_pending_updates().add(self._get_cache_key(self))
                self.cache_object(self)  # Update the cache with the current state
                return self
            else:
                logger.debug(f"Saving {self.__class__.__name__} {self.id}")
                return self._perform_save()
        else:
            logger.debug(f"No changes detected for {self.__class__.__name__} {self.id}")
            return self

    def create(self: T, bulk: bool = False) -> T:
        """
        Create a new object, either immediately or in bulk.

        :param bool bulk: Whether to perform a bulk create operation, defaults to False
        :return: The created object
        :rtype: T
        """
        if bulk:
            logger.debug(f"Adding new {self.__class__.__name__} to pending creations")
            cache_key = self._get_cache_key(self)
            with self._get_lock(cache_key):
                self._get_pending_creations().add(cache_key)
                self.cache_object(self)
                return self
        else:
            with self._get_lock(self._get_cache_key(self)):
                created_object = self._perform_create()
                self.cache_object(created_object)
                return created_object

    @classmethod
    def bulk_save(cls, progress_context: Optional[Progress] = None) -> Dict[str, List[T]]:
        """
        Perform bulk save operations for both updates and creations.

        :param Optional[Progress] progress_context: Optional progress context for tracking
        :return: Dictionary containing lists of updated and created objects
        :rtype: Dict[str, List[T]]
        """
        result = {"updated": [], "created": []}

        # Handle updates
        pending_updates = cls._get_pending_updates()
        if pending_updates:
            logger.debug(f"Analyzing {len(pending_updates)} {cls.__name__} objects for bulk update...")
            objects_to_update = [
                cls.get_cached_object(cache_key=cache_key)
                for cache_key in pending_updates
                if cls.get_cached_object(cache_key=cache_key)
            ]
            logger.debug(
                f"{len(objects_to_update)}/{len(pending_updates)} {cls.__name__} objects qualify for bulk update."
            )
            if objects_to_update:
                logger.info(f"Performing bulk update for {len(objects_to_update)} {cls.__name__} objects...")
                result["updated"] = cls.batch_update(items=objects_to_update, progress_context=progress_context)
            pending_updates.clear()

        # Handle creations
        pending_creations = cls._get_pending_creations()
        if pending_creations:
            logger.debug(f"Analyzing {len(pending_creations)} {cls.__name__} objects for bulk creation...")
            objects_to_create = [
                cls.get_cached_object(cache_key=cache_key)
                for cache_key in pending_creations
                if cls.get_cached_object(cache_key=cache_key)
            ]
            logger.debug(
                f"{len(objects_to_create)}/{len(pending_creations)} {cls.__name__} objects qualify for bulk creation."
            )
            if objects_to_create:
                logger.info(f"Performing bulk creation for {len(pending_creations)} {cls.__name__} objects...")
                result["created"] = cls.batch_create(items=objects_to_create, progress_context=progress_context)
            pending_creations.clear()

        return result

    @classmethod
    def _get_headers(cls) -> Optional[Dict[str, str]]:
        """
        Get the headers for the API request.

        :return: Dictionary of headers if api version is not 1, otherwise None
        :rtype: Optional[Dict[str, str]]
        """
        if cls._x_api_version != "1":
            return {"x-api-version": cls._x_api_version}
        return None

    def _perform_create(self: T) -> T:
        """
        Perform the actual create operation.

        :raises APIInsertionError: If the insert fails
        :return: The created object
        :rtype: T
        """
        endpoint = self.get_endpoint("insert")
        response = self._get_api_handler().post(endpoint=endpoint, data=self.dict(), headers=self._get_headers())
        if response and response.ok:
            obj = self.__class__(**response.json())
            self.cache_object(obj)
            return obj
        else:
            logger.error(
                f"Failed to create {self.__class__.__name__}\n Endpoint: {endpoint}\n Payload: "
                f"{json.dumps(self.dict(), indent=2)}",
                exc_info=True,
            )
            if response and not response.ok:
                logger.error(
                    f"Response Error: Code #{response.status_code}: {response.reason}\n{response.text}", exc_info=True
                )
            if response is None:
                error_msg = "Response was None"
                logger.error(error_msg)
                raise APIInsertionError(error_msg)
            error_msg = f"Response Code: {response.status_code}:{response.reason} - {response.text}"
            logger.error(error_msg)
            raise APIInsertionError(error_msg)

    def _perform_save(self: T) -> T:
        """
        Perform the actual save operation.

        :raises APIUpdateError: If the update fails
        :return: The updated object
        :rtype: T
        """
        logger.debug(f"Updating {self.__class__.__name__} {self.id}")
        endpoint = self.get_endpoint("update").format(id=self.id)
        response = self._get_api_handler().put(endpoint=endpoint, data=self.dict(), headers=self._get_headers())
        if hasattr(response, "ok") and response.ok:
            logger.debug(f"Successfully saved {self.__class__.__name__} {self.id}")
            obj = self.__class__(**response.json())
            self.cache_object(obj)
            return obj
        else:
            logger.error(
                f"Failed to update {self.__class__.__name__}\n Endpoint: {endpoint}\n Payload: "
                f"{json.dumps(self.dict(), indent=2)}"
            )
            if response is not None:
                raise APIUpdateError(f"Response Code: {response.status_code} - {response.text}")
            else:
                raise APIUpdateError("Response was None")

    @classmethod
    def batch_create(
        cls,
        items: Union[List[T], ThreadSafeList[T]],
        progress_context: Optional[Progress] = None,
        remove_progress: Optional[bool] = False,
    ) -> List[T]:
        """
        Use bulk_create method to create assets.

        :param List[T] items: List of Asset Objects
        :param Optional[Progress] progress_context: Optional progress context for tracking
        :param Optional[bool] remove_progress: Whether to remove the progress bar after completion, defaults to False
        :return: List of cls items from RegScale
        :rtype: List[T]
        """
        batch_size = 100
        results = []
        total_items = len(items)

        def process_batch(progress: Optional[Progress] = None, remove_progress_bar: Optional[bool] = False):
            """
            Process the batch of items

            :param Optional[Progress] progress: Optional progress context for tracking
            :param Optional[bool] remove_progress_bar: Whether to remove the progress bar after completion, defaults to False
            """
            nonlocal results  # noqa: F824
            create_job = None
            if progress:
                create_job = progress.add_task(
                    f"[#f68d1f]Creating {total_items} RegScale {cls.__name__}s...",
                    total=total_items,
                )
            for i in range(0, total_items, batch_size):
                batch = items[i : i + batch_size]
                batch_results = cls._handle_list_response(
                    cls._get_api_handler().post(
                        endpoint=cls.get_endpoint("batch_create"),
                        data=[item.model_dump() for item in batch if item],
                    )
                )
                results.extend(batch_results)
                if progress and create_job is not None:
                    progress_increment = min(batch_size, total_items - i)
                    progress.advance(create_job, progress_increment)
                for created_item in batch_results:
                    cls.cache_object(created_item)
            cls._check_and_remove_progress_object(progress, remove_progress_bar, create_job)

        if progress_context:
            process_batch(progress=progress_context, remove_progress_bar=remove_progress)
        else:
            with create_progress_object() as create_progress:
                process_batch(progress=create_progress, remove_progress_bar=remove_progress)
        return results

    @classmethod
    def batch_update(
        cls,
        items: Union[List[T], ThreadSafeList[T]],
        progress_context: Optional[Progress] = None,
        remove_progress: Optional[bool] = False,
    ) -> List[T]:
        """
        Use bulk_update method to update assets.

        :param List[T] items: List of cls Objects
        :param Optional[Progress] progress_context: Optional progress context for tracking
        :param Optional[bool] remove_progress: Whether to remove the progress bar after completion, defaults to False
        :return: List of cls items from RegScale
        :rtype: List[T]
        """
        batch_size = 100
        results: List[T] = []
        total_items = len(items)

        def process_batch(progress: Optional[Progress] = None, remove_progress_bar: Optional[bool] = False):
            """
            Process the batch of items

            :param Optional[Progress] progress: Optional progress context for tracking
            :param Optional[bool] remove_progress_bar: Whether to remove the progress bar after completion, defaults to False
            """
            nonlocal results  # noqa: F824
            update_job = None
            if progress:
                update_job = progress.add_task(
                    f"[#f68d1f]Updating {total_items} RegScale {cls.__name__}s...",
                    total=total_items,
                )
            for i in range(0, total_items, batch_size):
                batch = items[i : i + batch_size]
                batch_results = cls._handle_list_response(
                    cls._get_api_handler().put(
                        endpoint=cls.get_endpoint("batch_update"),
                        data=[item.model_dump() for item in batch if item],
                    )
                )
                results.extend(batch_results)
                if progress and update_job is not None:
                    progress_increment = min(batch_size, total_items - i)
                    progress.advance(update_job, progress_increment)
                for item in batch_results:
                    cls.cache_object(item)
            cls._check_and_remove_progress_object(progress_context, remove_progress_bar, update_job)

        if progress_context:
            process_batch(progress_context)
        else:
            with create_progress_object() as create_progress:
                process_batch(create_progress)

        return results

    @staticmethod
    def _check_and_remove_progress_object(
        progress_context: Optional[Progress] = None,
        remove_progress: Optional[bool] = False,
        progress_task: Optional[TaskID] = None,
    ) -> None:
        """
        Check if the progress object exists and remove it.

        :param Optional[Progress] progress_context: Optional progress context for tracking
        :param Optional[bool] remove_progress: Whether to remove the progress bar after completion, defaults to False
        :param Optional[TaskID] progress_task: Optional progress task ID to remove, defaults to None
        :rtype: None
        """
        if progress_context and remove_progress and progress_task is not None:
            progress_context.remove_task(progress_task)

    @classmethod
    def get_object(cls, object_id: Union[str, int]) -> Optional[T]:
        """
        Get a RegScale object by ID.

        :param Union[str, int] object_id: The ID of the object
        :return: The object or None if not found
        :rtype: Optional[T]
        """
        response = cls._get_api_handler().get(endpoint=cls.get_endpoint("get").format(id=object_id))
        if response and response.ok:
            if response.json() and isinstance(response.json(), list):
                return cast(T, cls(**response.json()[0]))
            else:
                return cast(T, cls(**response.json()))
        else:
            logger.debug(f"Failing response: {response.status_code}: {response.reason} {response.text}")
            logger.warning(f"{cls.__name__}: No matching record found for ID: {cls.__name__} {object_id}")
            return None

    @classmethod
    def get_objects_and_attachments_by_parent(
        cls, parent_id: int, parent_module: str
    ) -> Tuple[List[T], Dict[int, List["File"]]]:
        """
        Get a list of objects and their attachments by the provided parent ID and module

        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :return: A tuple of a list of objects and a list of attachments
        :rtype: Tuple[List[T], dict[int, List["File"]]]
        """
        from regscale.models import File

        # get the existing issues for the parent record that are already in RegScale
        logger.info("Fetching full %s list from RegScale %s #%i.", cls.__name__, parent_module, parent_id)
        try:
            objects_data = cls.get_all_by_parent(
                parent_id=parent_id,
                parent_module=parent_module,
            )
        except Exception as e:
            logger.error("Error fetching %s list from RegScale %s #%i: %s", cls.__name__, parent_module, parent_id, e)
            return [], []

        if len(objects_data) == 0:
            logger.warning("No existing %s from RegScale %s #%i.", cls.__name__, parent_module, parent_id)
            return [], []

        attachments = {
            regscale_object.id: files
            for regscale_object in objects_data
            if (
                files := File.get_files_for_parent_from_regscale(
                    parent_id=regscale_object.id,
                    parent_module=cls.get_module_slug(),
                )
            )
        }
        logger.info(
            "Found %i %s(s) from RegScale %s #%i for processing.",
            len(objects_data),
            cls.__name__,
            parent_module,
            parent_id,
        )
        return objects_data, attachments

    @classmethod
    def get_list(cls) -> List[T]:
        """
        Get a list of objects.

        :return: A list of objects
        :rtype: List[T]
        """
        response = cls._get_api_handler().get(endpoint=cls.get_endpoint("list").format(module_slug=cls._module_slug))
        if response.ok:
            return cast(List[T], [cls.get_object(object_id=sp["id"]) for sp in response.json()])
        else:
            logger.error(f"Failed to get list of {cls.__name__} {response}")
            return []

    def delete(self) -> bool:
        """
        Delete an object in RegScale.

        :return: True if successful, False otherwise
        :rtype: bool
        """
        # Clear the cache for this object
        self.delete_object_cache(self)

        response = self._get_api_handler().delete(
            endpoint=self.get_endpoint("delete").format(id=self.id), headers=self._get_headers()
        )
        if response.ok:
            return True
        elif response.ok is False and response.status_code == 404:
            logger.debug(f"Failed to delete {self.__class__.__name__} {self.dict()}, {response.status_code}")
            return False
        else:
            logger.error(f"Failed to delete {self.__class__.__name__} {self.dict()}")
            return False

    @classmethod
    def from_dict(cls, obj: Dict[str, Any], copy_object: bool = False) -> T:  # type: ignore
        """
        Create RegScale Model from dictionary

        :param Dict[str, Any] obj: dictionary
        :param bool copy_object: Whether to copy the object without an id, defaults to False
        :return: Instance of RegScale Model
        :rtype: T
        """
        copy_obj = copy.copy(obj)
        if "id" in copy_obj and copy_object:
            del copy_obj["id"]
        return cast(T, cls(**copy_obj))

    @classmethod
    def parse_response(cls, response: Response, suppress_error: bool = False) -> Optional[T]:
        """
        Parse a response.

        :param Response response: The response
        :param bool suppress_error: Whether to suppress the error, defaults to False
        :return: An object or None
        :rtype: Optional[T]
        """
        if response and response.ok:
            logger.debug(json.dumps(response.json(), indent=4))
            return cast(T, cls(**response.json()))
        else:
            cls.log_response_error(response=response, suppress_error=suppress_error)
            return None

    @classmethod
    def log_response_error(cls, response: Response, suppress_error: bool = False) -> None:
        """
        Log an error message.

        :param Response response: The response
        :param bool suppress_error: Whether to suppress the error, defaults to False
        :raises APIResponseError: If the response is None
        :rtype: None
        """
        if response is not None:
            message = f"{cls.__name__}: - StatusCode: {response.status_code} Reason: {response.reason}"
            if response.text:
                message += f" - {response.text}"
            if suppress_error:
                logger.error(message)
            else:
                raise APIResponseError(message)
        else:
            if suppress_error:
                logger.error(f"{cls.__name__}: Response was None")
            else:
                raise APIResponseError(f"{cls.__name__}: Response was None")

    # pylint: disable=W0613
    @classmethod
    def get_sort_position_dict(cls) -> dict:
        """
        This method is for use with the genericized bulk loader, and is intended to be overridden
        by all models that can be instantiated by that module.
        The purpose is to provide a sort-order for populating the columns
        in the generated spreadsheet.

        Any field name that returns a sort position of -1 will be supressed in the generated Excel
        workbook.
        :return: dict The sort position in the list of properties
        :rtype: dict
        """
        return {}

    @classmethod
    def get_enum_values(cls, field_name: str) -> list:
        """
        This method is for use with the genericized bulk loader, and is intended to be overridden
        by all models that can be instantiated by that module.
        The purpose is to provide a list of enumerated values that can be used for the specified
        property on the model. This is to be used for building a drop-down of values that can be
        used to set the property.

        :param str field_name: The property name to provide enum values for
        :return: list of strings
        :rtype: list
        """
        return []

    @classmethod
    def get_lookup_field(cls, field_name: str) -> str:
        """
        This method is for use with the genericized bulk loader, and is intended to be overridden
        by all models that can be instantiated by that module.
        The purpose is to provide a query that can be used to pull a list of records and IDs for
        building a drop-down of lookup values that can be used to populate the appropriate
        foreign-key value into the specified property.

        :param str field_name: The property name to provide lookup value query for
        :return: str The GraphQL query for building the list of lookup values and IDs
        :rtype: str
        """
        return ""

    @classmethod
    def is_date_field(cls, field_name: str) -> bool:
        """
        This method is for use with the genericized bulk loader, and is intended to be overridden
        by all models that can be instantiated by that module.
        The purpose is to provide a flag that the field specified should be treated/formatted as
        a date field in the generated spreadsheet.

        :param str field_name: The property name to specify whether should be
                                treated as a date field
        :return: bool
        :rtype: bool
        """
        return False

    @classmethod
    def get_export_query(cls, app: Application, parent_id: int, parent_module: str) -> list:
        """
        This method is for use with the genericized bulk loader, and is intended to be overridden
        by all models that can be instantiated by that module.
        The purpose is to provide a graphQL query for retrieving all data to
        be edited in an Excel workbook.

        :param Application app: RegScale Application object
        :param int parent_id: RegScale ID of parent
        :param str parent_module: Module of parent
        :return: list GraphQL response from RegScale
        :rtype: list
        """
        return []

    @classmethod
    def use_query(cls) -> bool:
        """
        This method is for use with the genericized bulk loader, and is intended to be overridden
        by all models that can be instantiated by that module.
        The purpose is to determine whether the model instantiated will use a graphQL query
        to produce the data for the Excel workbook export. If a query isn't used, then the
        get_all_by_parent method will be used.

        :return: bool
        :rtype: bool
        """
        return False

    @classmethod
    def get_extra_fields(cls) -> list:
        """
        This method is for use with the genericized bulk loader, and is intended to be overridden
        by all models that can be instantiated by that module.
        The purpose is to provide a list of extra fields to include in the workbook.
        These are fields that are pulled in as part of the graphQL query, but are not members of
        the model definition.

        :return: list of extra field names
        :rtype: list
        """
        return []

    @classmethod
    def get_include_fields(cls) -> list:
        """
        This method is for use with the genericized bulk loader, and is intended to be overridden
        by all models that can be instantiated by that module.
        The purpose of this method is to provide a list of fields to be
        included in the Excel workbook despite not being included in the graphQL query.

        :return: list of  field names
        :rtype: list
        """
        return []

    @classmethod
    def is_required_field(cls, field_name: str) -> bool:
        """
        This method is for use with the genericized bulk loader, and is intended to be overridden
        by all models that can be instantiated by that module.
        The purpose of this method is to provide a list of fields that are required when
        creating a new record of the class type. This is to indicate when fields are defined
        as Optional in the class definition, but are required when creating a new record.

        :param str field_name: field name to check
        :return: bool indicating if the field is required
        :rtype: bool
        """
        return False

    @classmethod
    def is_new_excel_record_allowed(cls) -> bool:
        """
        This method is for use with the genericized bulk loader, and is intended to be overridden
        by all models that can be instantiated by that module.
        The purpose of this method is to provide a boolean indicator of whether new records are
        allowed when editing an excel spreadsheet export of the model.

        :return: bool indicating if the field is required
        :rtype: bool
        """
        return True

    @classmethod
    def create_new_connecting_model(cls, instance: Any) -> Any:
        """
        This method is used to create a required supporting model for connecting the
        current object to another in the database.

        :param Any instance: The instance to create a new connecting model for when loading new records.
        :return Any:
        :rtype Any:
        """
        return None

    @classmethod
    def get_bool_enums(cls, field_name: str) -> list:
        """
        This method is used to provide a list of boolean values that can be used to populate a
        drop-down list in the Excel workbook.

        :param str field_name: The field name to provide boolean values for
        :return: list of boolean values
        :rtype: list
        """
        try:
            if cls.__annotations__[field_name] in [Optional[bool], bool]:
                return ["TRUE", "FALSE"]
        except (AttributeError, KeyError):
            return []
        return []
