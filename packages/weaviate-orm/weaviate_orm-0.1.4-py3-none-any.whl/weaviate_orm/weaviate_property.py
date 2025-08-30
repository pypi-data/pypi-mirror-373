from typing import Callable, Type, Optional, Union, List
from datetime import datetime, date, timezone
from dateutil import parser

from weaviate.classes.config import DataType, Property as weaviateProperty, Tokenization

class Property:
    """
    A robust descriptor to handle the definition of a field/property in
    a Weaviate-based ORM system.

    """

    def __init__(self,
                weaviate_type:DataType,
                cast_type:Type,
                description:str,
                required:bool=False,
                default=None,
                validator:Optional[Callable]=None,
                index_filterable:Optional[bool]=None,
                index_range_filters:Optional[bool]=None,
                index_searchable:Optional[bool]=None,
                nested_properties:Optional[Union["Property", List["Property"]]]=None,
                tokenization: Optional[Tokenization]=None,
                vectorize_property_name:bool=True,
                skip_vectorization:bool=False,
                inherited:bool=False
                 
            ):
        """
        Initialize the property descriptor.

        Args:
            cast_type (Type): The type to cast the incoming value to.
            weaviate_type (DataType): The Weaviate data type of the property.
            description (str): A human-readable description of the property.	
            required (bool, optional): Whether the property is required. Defaults to False.
            default ([type], optional): The default value for the property. Defaults to None.
            validator (Callable, optional): A function to validate the property value. Defaults to None.
            index_filterable (Optional[bool], optional): Whether the property should be filterable in the inverted index. Defaults to None.
            index_range_filters (Optional[bool], optional): Whether the property should support range filters in the inverted index. Defaults to None.
            index_searchable (Optional[bool], optional): Whether the property should be searchable in the inverted index. Defaults to None.
            nested_properties (Optional[Union["Property", List["Property"]]], optional): nested properties for data type OBJECT and OBJECT_ARRAY`. Defaults to None.
            skip_vectorization (bool, optional): Whether to skip vectorization of the property. Defaults to False.
            tokenization (Optional[Tokenization], optional): The tokenization method to use for the inverted index. Defaults to None.
            vectorize_property_name (bool, optional): Whether to vectorize the property name. Defaults to True.
            inherited (bool, optional): Whether the property is inherited from a parent class. Defaults to False.

        Raises:
            NotImplementedError: If nested properties are used.
            ValueError: If the default value is invalid.
        """

        self.cast_type = cast_type
        self.weaviate_type = weaviate_type
        self.required = required
        self.default = default
        self.validator = validator
        self.description = description
        self.vectorize_property_name = vectorize_property_name
        self.skip_vectorization = skip_vectorization
        self.index_filterable = index_filterable
        self.index_range_filters = index_range_filters
        self.index_searchable = index_searchable
        self.nested_properties = nested_properties
        self.tokenization = tokenization
        self.inherited = inherited

        if self.nested_properties is not None:
            raise NotImplementedError("Nested properties are not yet supported.")

        # Will be set by __set_name__
        self.name = None

        # Validate default value
        if default is not None:
            self._cast_and_validate(default)


    def __set_name__(self, owner, name):
        """
        Called automatically when the descriptor is assigned to a class attribute.
        """
        self.name = name
        self._owner = owner

    def __get__(self, instance, owner):
        """
        Access the value stored on the instance. If accessed from the class (instance is None),
        return the descriptor itself to allow introspection (meta-information).
        """
        if instance is None:
            # Access via class: e.g., MyModel.field
            return self

        # Return the actual instance value (stored in the instance dict)
        return instance.__dict__.get(self.name, self.default)

    def __set__(self, instance, value):        
        """
        Cast, validate, and store the value in the instance dictionary.

        Args:
            instance: The instance of the class.
            value: The value to store.

        Raises:
            ValueError: If the value is invalid.
        """

        # If we are setting the default at class initialization, instance might be None
        # (when the descriptor is created). In that case, we skip storing it on an actual instance.
        if instance is None:
            # Just validate/cast to confirm it's a good default
            self._cast_and_validate(value)
            return

        # Otherwise, cast/validate then store
        final_value = self._cast_and_validate(value)
        instance.__dict__[self.name] = final_value

    def _cast_and_validate(self, value):
        """
        Helper method to apply default rules, cast, and validate the value.

        Args:
            value (Any): The value to process.

        Returns:
            Any: The processed value.

        Raises:
            ValueError: If the value is invalid.
        """

        # Apply required/default logic
        if value is None:
            if self.required and self.default is None:
                raise ValueError(
                    f"'{self.name}' is required but no value was provided."
                )
            if self.default is not None:
                value = self.default

        # Cast
        if (self.cast_type == datetime or self.cast_type == date) and self.weaviate_type == DataType.DATE:
            if isinstance(value, str):
                try:
                    value = self._read_datetime(value)
                except ValueError as exc:
                    raise ValueError(f"Error casting value for '{self.name}': {exc}") from exc
            elif isinstance(value, datetime):
                value = self._write_datetime(value)
            else:
                raise ValueError(f"Error casting value for '{self.name}': Expected a string or datetime.")
        elif value is not None:
            try:
                value = self.cast_type(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Error casting value for '{self.name}': {exc}") from exc

        # Validation
        if value is not None and self.validator is not None:
            try:
                valid = self.validator(value)
                if not valid:
                    raise ValueError(
                        f"Validation failed for '{self.name}': validator returned False or None."
                    )
            except Exception as exc:
                raise ValueError(f"Validation failed for '{self.name}': {exc}") from exc

        return value

    def _get_weaviate_property(self) -> weaviateProperty:
        """
        Return the property definition in Weaviate format.

        Returns:
            weaviateProperty: The Weaviate property definition.

        Raises:
            ValueError: If the property name is not set.
        """

        if self.name == None:
            raise ValueError("Property name not set. Can't generate Weaviate property from non-bound property.")

        prop = weaviateProperty(
            name=self.name,
            data_type=self.weaviate_type,
            description=self.description,
            vectorize_property_name=self.vectorize_property_name,
            skip_vectorization=self.skip_vectorization,
            index_filterable=self.index_filterable,
            index_range_filters=self.index_range_filters,
            index_searchable=self.index_searchable,
            #nested_properties=self.nested_properties, TODO: Implement nested properties
            tokenization=self.tokenization
            )
        
        return prop

    def _read_datetime(self, value:str) -> datetime:
        """
        Read weaviate dates as Python datetime objects.

        Args:
            value (str): The value to read dates from.

        Returns:
            datetime: The value as a datetime object.
        """

        # Convert Weaviate date format to Python datetime
        #date_value: datetime = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        date_value: datetime = parser.isoparse(value)

        return date_value
    
    def _write_datetime(self, value:datetime) -> datetime:
        """
        Write Python datetime objects as Weaviate date strings.

        Args:
            value (datetime): The value to write dates from.
        """

        # Try to get the timezone from the engine, if available
        if hasattr(self, "_owner"):
            if hasattr(self._owner, "_engine"):
                tz = getattr(self._owner._engine, "_timezone", None)
            else:
                # Fallback to UTC if no engine is available
                tz = timezone.utc
        else:
            # Fallback to UTC if no engine is available
            tz = timezone.utc

        #If value hase timezone
        if value.tzinfo is None:
            # If the value is naive, set it to the engine's timezone
            return value.replace(tzinfo=tz)
        else:
            # If the value is timezone-aware do not change it
            return value


        if value.tzinfo is None:
            return value.replace(tzinfo=tz)
        else:
            return value.astimezone(tz)

        # Convert Python datetime to Weaviate date format
        #date_str: str = value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

