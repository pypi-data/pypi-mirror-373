from abc import ABC, abstractmethod
from uuid import UUID, uuid4 ,uuid5
from typing import Optional, Union, List, Sequence, Any, Union, TYPE_CHECKING, Callable, Literal
import inspect

from weaviate import Client, WeaviateClient
from weaviate.collections.classes.config_vectorizers import _VectorizerConfigCreate
from weaviate.collections.classes.config_named_vectors import _NamedVectorConfigCreate
from weaviate.collections.classes.config_vector_index import _VectorIndexConfigCreate
from weaviate.collections.classes.config import Configure
from weaviate.collections.classes.data import DataReferences
from weaviate.classes.query import QueryReference
from weaviate.classes.data import DataReference
from weaviate.collections import Collection

from weaviate.collections.classes.internal import ObjectSingleReturn, QueryReturn
from weaviate.classes.query import MetadataQuery

from weaviate.collections.classes.config import (
    CollectionConfig,
    CollectionConfigSimple,
    _GenerativeProvider,
    _InvertedIndexConfigCreate,
    _MultiTenancyConfigCreate,
    Property,
    _ShardingConfigCreate,
    _ReferencePropertyBase,
    _ReplicationConfigCreate,
    _RerankerProvider,
)

VectorizerConfig = Optional[Union["_VectorizerConfigCreate", List["_NamedVectorConfigCreate"]]]

# EventName = str  # Type alias for event names
ALLOWED_EVENTS = set([
    "pre_save", "post_save",
    "pre_update", "post_update",
    "pre_delete", "post_delete",
])
EVENT_NAMES = Literal[ALLOWED_EVENTS]


from .weaviate_meta import Weaviate_Meta
from .weaviate_decorators import with_client
from .weaviate_engine import Weaviate_Engine
from .weaviate_utility import _Handle_Referenzes
from .weavitae_reference import Reference_Type


class Base_Model(ABC, metaclass=Weaviate_Meta):
    """
    Abstract base class. The metaclass builds _weaviate_schema for each subclass.
    The engine reference is used to get a client, or to do create_all_schemas() once.
    """

    #Classvariables

    _engine = None  # Will be set when bind_engine(engine) is called
    _namespace = None #Needs to be set as classvariable
    _weaviate_schema: dict[str, Any]

    # Callback-registry
    _callbacks: dict[str, List[Callable]] = {}
    ALLOWED_EVENTS =  ALLOWED_EVENTS
    

    #Weaviate schema related
    __collection_name__: Optional[str] = None #Needs to be set as classvariable

    description : Optional[str] = ""
    generative_config: Optional[_GenerativeProvider] = None
    inverted_index_config: Optional[_InvertedIndexConfigCreate] = None
    multi_tenancy_config: Optional[_MultiTenancyConfigCreate] = None
    replication_config: Optional[_ReplicationConfigCreate] = None
    #reranker_config: Optional[_RerankerProvider] = None
    sharding_config: Optional[_ShardingConfigCreate] = None
    vector_index_config: Optional[_VectorIndexConfigCreate] = None
    vectorizer_config: Optional[Union[_VectorizerConfigCreate, List[_NamedVectorConfigCreate]]] = Configure.Vectorizer.none()
    
    #Classmethods

    @classmethod
    def get_collection_name(cls) -> str:
        """
        Get the collection name for the class.

        Returns:
            str: The collection name.
        """
        return cls.__collection_name__ if cls.__collection_name__ else cls.__name__

    @classmethod
    @with_client(require_schema_creation=False)
    def get_collection(cls, *, client:Optional[WeaviateClient]=None) -> Collection:
        """
        Get the collection object for the class.

        Args:
            client (Client): Optional; The Weaviate client to use.

        Returns:
            Collection: The collection object.
        """

        if client != None:
            return client.collections.get(cls.get_collection_name())
        
        else:
            raise ValueError("No client provided.")

    @classmethod
    @with_client(require_schema_creation=False)
    def instance_exists(cls, uuid:UUID, *, client:Optional[WeaviateClient]=None) -> bool:

        """
        Check if an object with the given UUID exists in Weaviate.

        Args:
            uuid (UUID): The UUID to check.
            client (Client): The Weaviate client to use.
        
        Returns:
            bool: True if the object exists.
        """

        return cls.get_collection(client=client).data.exists(str(uuid))

    @classmethod
    def _cast_from_response(cls, response: ObjectSingleReturn) -> "Base_Model":
        """
        Cast a response object to an instance of the class based on its __init__ signature.

        Args:
            response (ObjectSingleReturn): The response object.

        Returns:
            Base_Model: The instance of the class.
        """
        # Get the __init__ signature (exclude 'self')
        init_sig = inspect.signature(cls.__init__)
        init_params = list(init_sig.parameters.values())  # skip 'self'

        # Filter response properties that match init parameters
        init_args = {
            param.name: response.properties.get(param.name, param.default)
            for param in init_params
            if param.name in response.properties or param.default is not inspect.Parameter.empty
        }

        # Create instance with collected init_args
        inst = cls(**init_args)

        # Set UUID if it exists
        if hasattr(inst, 'uuid'):
            inst.uuid = response.uuid

        # Optionally set any extra properties not covered by __init__
        for key, prop in response.properties.items():
            if not hasattr(inst, key):
                setattr(inst, key, prop)

        return inst

    @classmethod
    @with_client(require_schema_creation=False)
    def _get_instances_from_query(cls, response: QueryReturn, include_references=False, include_vector=False,  client:Optional[WeaviateClient]=None) -> List["Base_Model"]:

        instances = []

        for r in response.objects:
            instances.append(cls.get(r.uuid, include_references=include_references, include_vector=include_vector, client=client))

        return instances


    @classmethod
    @with_client(require_schema_creation=False)
    def get(cls, uuid:UUID, include_references=False, include_vector:Union[bool, List[str]]=False, *, client:Optional[WeaviateClient]=None) -> Union["Base_Model", None]:
        """
        Retrieve an object by UUID. #TODO Read all properties of the object; option to include references; option to include vectors.
        """

        uuid_str = str(uuid)

        if client == None:
            raise ValueError("No client provided.")
        
        #Get a list of all crossreferences
        if include_references:
            q_ref= []
            for ref in cls._references:
                if not ref.name:
                    raise ValueError("Reference field name is not set.")
                qr = QueryReference(link_on=ref.name, return_properties=False)
                q_ref.append(qr)
        
            #Get the object from weaviate
            collection = client.collections.get(cls.get_collection_name())
            response = collection.query.fetch_object_by_id(
                uuid = uuid_str,
                include_vector = include_vector,
                return_references=q_ref
            )
        else:
             #Get the object from weaviate
            collection = client.collections.get(cls.get_collection_name())
            response = collection.query.fetch_object_by_id(
                uuid = uuid_str,
                include_vector = include_vector
            )
        
        if response == None:
            return None

        #Create an instance of the class
        instance = cls._cast_from_response(response)

        #Load references
        if include_references:
            instance._set_references(response)

        return instance

    @classmethod
    def bind_engine(cls, engine:Weaviate_Engine):
        """
        Bind the WeaviateEngine to the class. This is required for schema creation.

        Args:
            engine (WeaviateEngine): The engine instance to bind.
        """
        cls._engine = engine
        cls._engine._register_model(cls)

    @classmethod
    @with_client(require_schema_creation=False)
    def raw_near_vector(cls, *args, client:Optional[WeaviateClient]=None, **kwargs) -> Any:
        """
        Perform a near-vector query.
        """
        collection = cls.get_collection(client=client)
        result = collection.query.near_vector(*args, **kwargs)

        return result
    
    @classmethod
    @with_client(require_schema_creation=False)
    def raw_near_text(cls, *args, client:Optional[WeaviateClient]=None, **kwargs) -> Any:
        """
        Perform a near-text query.
        """
        collection = cls.get_collection(client=client)
        result = collection.query.near_text(*args, **kwargs)
        return result

    @classmethod
    @with_client(require_schema_creation=False)
    def near_vector(cls, vector:list[float], include_references, include_vector, client:Optional[WeaviateClient]=None, similarity=True, top_n = 5) -> Any:
        """
        Perform a near-vector query.
        """

        #Create Metadata query
        return_metadata=MetadataQuery(distance=similarity)

        collection = cls.get_collection(client=client)
        result = collection.query.near_vector(vector, return_metadata=return_metadata, limit=top_n)

        result_obj = cls._get_instances_from_query(result, include_references=include_references, include_vector=include_vector, client=client)

        return result_obj
    
    @classmethod
    @with_client(require_schema_creation=False)
    def near_text(cls, query_str:str, include_references, include_vector, client:Optional[WeaviateClient]=None, similarity=True, top_n = 5) -> Any:
        """
        Perform a near-text query.
        """

        #Create Metadata query
        return_metadata=MetadataQuery(distance=similarity)

        collection = cls.get_collection(client=client)
        result = collection.query.near_text(query_str, return_metadata=return_metadata, limit=top_n)

        result_obj = cls._get_instances_from_query(result, include_references=include_references, include_vector=include_vector, client=client)

        return result_obj
    

    #Properties

    @property
    def exists(self) -> bool:
        """
        Check if the object exists in Weaviate.

        Returns:
            bool: True if the object exists.
        """
        return self.instance_exists(self.get_uuid())

    @property
    def is_valid(self) -> bool:
        """
        Check if the object is valid.

        Returns:
            bool: True if the object is valid.
        """

        _is_valid = True

        #Check if get_uuid() raises an error
        #try:
        #except ValueError:
        #    _is_valid = False
        
        #Check all Properties run their validators
        #TODO

        return _is_valid

    #Callback-Helpers
    @classmethod
    def register_callback(cls, event: str):
        """Decorator:  @MyModel.register_callback('post_save')"""

        if event not in cls.ALLOWED_EVENTS:                  # ← runtime guard
            raise ValueError(
                f"Unknown event {event!r}. "
                f"Allowed: {', '.join(sorted(cls.ALLOWED_EVENTS))}"
            )
        
        def _decorator(fn):
            cls._callbacks.setdefault(event, []).append(fn)
            return fn
        return _decorator

    def _emit(self, event: str, **ctx) -> None:
        """
        Call all callbacks registered for *event* on the full MRO,
        making sure each callback receives **exactly one**
        ``instance=...`` keyword.
        """
        ctx.setdefault("instance", self)          # add only if missing
        for cls in self.__class__.__mro__:
            for fn in getattr(cls, "_callbacks", {}).get(event, []):
                fn(**ctx)

    #Methods

    def generate_uuid(self, force:bool=False) -> UUID:
        """
        Generate a UUID for the object. 
        If a namespace is provided and _get_uuid_name_str is implemented uuid5 is used else uuid4.

        Args:
            force (bool): If True, regenerate the UUID even if it is already set.

        Returns:
            UUID: The generated UUID

        Raises:
            ValueError: If the UUID is already set and force=False.
            ValueError: If a name is provided but no namespace is set.
            NotImplementedError: If _get_uuid_name_string() is not implemented and a namespace is set.
    
        """

        name = self._get_uuid_name_string()

        if hasattr(self, "uuid") and self.uuid and not force:
            raise ValueError("UUID already set; use force=True to regenerate.")

        if self._namespace and name:
            self.uuid = uuid5(self._namespace, name)
        elif name and not self._namespace:
            raise ValueError("Namespace must be set to generate a UUID with a name (uuid5); make sure to to provide a namespace as classvariable")
        elif not name and self._namespace:
            raise NotImplementedError("_get_uuid_name_string() method must be implemented explicitly to generate a UUID with a namespace (uuid5) otherwise uuid4 is used.")
        else:
            self.uuid = uuid4()

        return self.uuid
    
    def _get_uuid_name_string(self) -> Optional[str]:
        """
        Abstract method to get the name for the UUID generation. Implement this method in subclasses to provide a name string. 
        This method is implemented to return None and fall back to uuid4 generation if not implemented explicitly.

        Returns:
            str: The name for the UUID generation; None if not implemented.
        """

        return None

        raise NotImplementedError("get_uuid_name_string() not implemented.")

    def get_uuid(self) -> UUID:
        """
        Abstract method to get the UUID of the object.

        Returns:
            UUID: The UUID of the object.

        Raises:
            ValueError: If the UUID is not set.
        """

        if not hasattr(self, "uuid"): #Check if this is  a good idea
            self.generate_uuid()
        
        if self.uuid == None:
            raise ValueError("UUID not set")
        
        return self.uuid

    def _set_references(self, response:ObjectSingleReturn):
        """
        Set all references of the object.

        Args:
            response (ObjectSingleReturn): The response object.
        """


        if response.references and response.references != {}:
            for key, ref in response.references.items():
                ref_obj = ref.objects
                if isinstance(ref_obj, list):
                    self.__setattr__(key, [o.uuid for o in ref_obj])
                else:
                    self.__setattr__(key, ref_obj.uuid)

    @with_client(require_schema_creation=False)
    def _is_referenced(self, *, client:Optional[WeaviateClient]=None) -> bool:
        """
        Check if the object is referenced in Weaviate.

        Args:
            client (Client): Optional; The Weaviate client to use

        Returns:
            bool: True if the object is referenced.
        """

        if client == None:
            raise ValueError("No client provided.")

        to_uuid = self.get_uuid()
        reference_collection = self.get_collection_name()

        #Get all relevant referenzes
        refs = _Handle_Referenzes.get_referenzes(client, reference_collection, to_uuid)

        return refs != {}

    @with_client(require_schema_creation=False)
    def _delete_referenced_self(self, *, client:Optional[WeaviateClient]=None):
        """
        Delete all references to the object.

        Args:
            client (Client): Optional; The Weaviate client to use
        """

        if client == None:
            raise ValueError("No client provided.")

        to_uuid = self.get_uuid()
        reference_collection = self.get_collection_name()

        #Get all relevant referenzes
        refs = _Handle_Referenzes.get_referenzes(client, reference_collection, to_uuid)

        #Delete Referenzes
        for col, col_refs in refs.items():

            #Get collection
            collection = client.collections.get(col)

            for obj_id, obj_refs in col_refs.items():
                for ref, elements in obj_refs.items():
                     
                    #Delete Referenzes
                    from_uuid = obj_id
                    from_property = ref
                    collection.data.reference_delete(from_uuid, from_property, to_uuid)

    @with_client(require_schema_creation=False)
    def save(self, vector:Optional[list[float]]=None, update:bool=False, include_references:bool=False, recursive:bool=False, *, client:Optional[WeaviateClient]=None, **named_vectors) -> bool:
        """
        Save the object to Weaviate.

        Args:
            client (Client): Optional; The Weaviate client to use for saving.
            vector (list[float]): Optional; The vector to save.
            update (bool): Update the object if it already exists.
            include_references (bool): Include cross-references in the save.
            recursive (bool): Save all properties recursively.
            named_vectors (dict): Optional; Named vectors to save.

        Returns:
            bool: True if the object was saved successfully.
        """

        # pre-callback
        self._emit("pre_save", instance=self, client=client)

        _success = False

        #Add the object
        reference_dict = self._save_properties(client=client, vector=vector, update=update, include_references=include_references, recursive=recursive, **named_vectors)

        #Add all references TODO -> if not include_references raise an error if references does not exists else add them
        if include_references:
            self._save_references(reference_dict, client=client)

        _success = True

        # post-callback
        self._emit("post_save", instance=self, client=client)

        return _success

    @with_client(require_schema_creation=False)
    def update(self, include_references: bool = True, recursive:bool=True, *, client:Optional[WeaviateClient]=None) -> bool:
        """
        Update the object in Weaviate if there are any changes.
        Only changed properties and references are sent.

        Args:
            include_references (bool): Whether to include cross-references during comparison.
            client (WeaviateClient): The Weaviate client (injected via decorator).
        """

        #TODO: Handle vectors, named vectors, and replacements as well as delitions

        #pre-callback
        self._emit("pre_update", instance=self, client=client)

        _uuid = self.get_uuid()
        if not _uuid:
            raise ValueError("Object must have a UUID before updating.")

        existing = self.get(_uuid, include_references=include_references, client=client, include_vector=True)
        if existing is None:
            raise ValueError("Object does not exist in the database.")

        # Check if UUID-generating fields changed
        if hasattr(self, "_get_uuid_name_string") and callable(self._get_uuid_name_string):
            try:
                current_uuid_str = self._get_uuid_name_string()
                existing_uuid_str = existing._get_uuid_name_string()
                if current_uuid_str != existing_uuid_str:
                    raise ValueError(
                        f"Cannot update object: fields relevant to UUID generation have changed "
                        f"(was: '{existing_uuid_str}', now: '{current_uuid_str}')."
                    )
            except NotImplementedError:
                pass

        changes = self._get_diff(existing, include_references=include_references, recursive=recursive)

        if not changes:
            return True  # No changes to update
        
        self._update(changes, client=client)

        #Recursive update of references
        if include_references and recursive and len(changes.keys()) > 1:
            for uuid in changes.keys():
                if uuid != self.get_uuid():
                    #Get the object from Weaviate
                    changes[uuid]['obj']._update(changes, client=client)

        #TODO check if update was successful

        # post-callback
        self._emit("post_update", instance=self, client=client)

        return True

    @with_client(require_schema_creation=False) 
    def delete(self, force:bool=False, clean_references:bool=False, *, client:Optional[WeaviateClient]=None) -> bool:
        """
        Delete the object from Weaviate.

        Args:
            force (bool): Force deletion even if the object is used as a cross-reference.
            clean_references (bool): Delete all references to the object.
            client (Client): Optional; The Weaviate client to use for deletion.

        Returns:
            bool: True if the object was deleted successfully.
        
        Raises:
            ValueError: If the object has no UUID.
            ValueError: If the object does not exist in Weaviate.
            ValueError: If the object is used as a cross-reference and force=False.
        """

        # pre-callback
        self._emit("pre_delete", instance=self, client=client)

        #Check if the object has a UUID and exists
        if not self.get_uuid():
            raise ValueError("Object must have a UUID before deleting.")
        
        if not self.instance_exists(self.get_uuid(), client=client):
            raise ValueError("Object does not exist in the database.")
        
        #Check if object is used as cross-reference
        if not force and self._is_referenced(client=client):
            raise ValueError("Object is used as a cross-reference; use force=True to delete.")
        
        #Delete all references to the object if clean_references=True
        if clean_references:
            self._delete_referenced_self(client=client)        

        #Delete the object
        self.get_collection(client=client).data.delete_by_id(self.get_uuid())

        #Check if the object was deleted
        success = not self.instance_exists(self.get_uuid(), client=client)

        #post-callback
        self._emit("post_delete", instance=self, client=client)

        return success

    #TODO: Include update_existing
    @with_client(require_schema_creation=False)
    def _save_properties(self, update:bool=False, include_references:bool=False, recursive:bool=False, vector:Optional[list[float]]=None, *, client:Optional[WeaviateClient]=None, **named_vectors ) -> dict[str, List[DataReferences]]:
        """
        Save the properties of the object to Weaviate.

        Args:
            client (Client): Optional; The Weaviate client to use for saving.
            vector (list[float]): Optional; The vector to save.
            update (bool): Update the object if it already exists.
            include_references (bool): Include cross-references in the save.
            recursive (bool): Save all properties recursively.
            named_vectors (dict): Optional; Named vectors to save.
        
        Returns:
            dict[str, List[DataReferences]]: A dictionary of collection names and their references.

        Raises:
            ValueError: If the object already exists and update=False.
            NotImplementedError: If named vectors are provided.
        """

        #Get all propertiy_names & cross-reference names
        prop_names = [p.name for p in getattr(self, "_weaviate_schema", {}).get("properties", [])]
        ref_names = [p.name for p in getattr(self, "_weaviate_schema", {}).get("references", [])]

        #Get all properties & cross-references
        _uuid:str = str(self.get_uuid())
        _properties = {k:v for k,v in self.__dict__.items() if k in prop_names}

        #Check if named vectors are provided
        if named_vectors:
            raise NotImplementedError("Named vectors are not implemented yet.")

        #Check if an object with this uuid already exists
        if self.instance_exists(self.get_uuid(), client=client):
            if not update:
                raise ValueError("Object already exists; use update=True to update.")
            else:
                self.update(include_references=include_references, client=client)
        else:
            #Add the object
            self.get_collection(client=client).data.insert(
                properties = _properties,
                uuid = _uuid,
                #vector = vector,
            )

        #Get all cross-references
        references_dict = {}

        if include_references:

            for ref_name, ref in {k:v for k,v in self.__dict__.items() if k in ref_names}.items():

                if not isinstance(ref, list):
                    ref = [ref]

                for r in ref:

                    if r is None:
                        continue

                    #Check if the reference exists in Weaviate
                    if not r.exists:
                        if not recursive:
                            raise ValueError(f"Reference {ref} : {r} does not exist in Weaviate.")
                        
                        #If not save recursively and return the references
                        recursive_references = r._save_properties(client=client, include_references=include_references, recursive=recursive)
                        for col, rec_refs in recursive_references.items():
                            if col not in references_dict:
                                references_dict[col] = []
                            references_dict[col].extend(rec_refs)

                    #Add collection name to the references_dict
                    #if type(r).get_collection_name() not in references_dict:
                    if self.get_collection_name() not in references_dict:
                        references_dict[self.get_collection_name()] = []

                    #Add the reference to the references_dict
                    references_dict[self.get_collection_name()].append(
                        DataReference(
                            from_property=ref_name,
                            from_uuid=self.get_uuid(),
                            to_uuid=r.get_uuid()
                        )
                    )

        return references_dict

    @with_client(require_schema_creation=False)
    def _save_references(self, reference_dict:dict[str, List[DataReferences]], *, client:Optional[WeaviateClient]=None):

        """
        Save all references of the object to Weaviate.

        Args:
            reference_dict (dict[str, List[DataReferences]): A dictionary of collection names and their references.
            client (Client): Optional; The Weaviate client to use for saving.
        
        Raises:
            ValueError: If no client is provided.

        """
        
        if client == None:
            raise ValueError("No client provided.")

        #Iterate over all collections
        for col_name, references in reference_dict.items():

            #Get the collection
            collection = client.collections.get(col_name)

            # Ensure references is a list of correct type
            if not isinstance(references, list):
                references = [references]  # Wrap single item in a list

            # Explicitly type the list
            references: List[DataReferences] = references or []

            #Add all references
            batch_return = collection.data.reference_add_many(references)

            if batch_return.has_errors:
                raise ValueError(f"Error adding references to collection '{col_name}': {batch_return}")

    @with_client(require_schema_creation=False)
    def _remove_reference(self, reference, old_reference_value, *, client:Optional[WeaviateClient]=None, handle_two_way=False):
        """
        Remove the reference from the owner class. If the reference is two-way, also remove the back-reference from the target class.
        """

        # Check if Two-Way
        if reference.way_type == Reference_Type.TWOWAY and handle_two_way:
            
            raise NotImplementedError("Two-way references are not implemented yet.")
    
        # Get collection object
        collection = self.get_collection(client=client)

        # Check if old_reference_value is a list
        if reference.reference_type == Reference_Type.SINGLE:
            old_reference_value = [old_reference_value] #Wrap in list to simplify processing

        # Remove reference
        for old_ref in old_reference_value:

            #Get to_uuid
            if isinstance(old_ref, Base_Model):
                to_uuid = old_ref.get_uuid()
            elif isinstance(old_ref, UUID):
                to_uuid = old_ref
            elif isinstance(old_ref, str):
                try:
                    to_uuid = UUID(old_ref)
                except ValueError:
                    raise ValueError(f"Invalid UUID string: {old_ref}")
            else:
                raise ValueError(f"Invalid reference type: {type(old_ref)}")

            # Delete the reference
            collection.data.reference_delete(
                from_uuid=self.get_uuid(),
                from_property=reference.name,
                to=to_uuid
            )

    def _get_diff(self, existing, include_references=True, recursive=True, changes = None) -> dict:
        """
        Recursively compute differences between self and the existing instance.

        Args:
            existing (Base_Model): The object loaded from Weaviate to compare against.

        Returns:
            dict: A dictionary of fields that differ (property_name -> (new_value, old_value)).
        """
        if not existing:
            raise ValueError("Cannot compute diff: existing object is None.")

        if changes is None:
            changes = {
                self.uuid :{
                    'obj': self,
                    'properties': {},
                    'old_properties': {},
                    'references': {},
                    'old_references': {},
                    'updated' : False
                }
            }
        #Handle two way crossreferences
        elif self.get_uuid() in changes.keys():
            return {}
        else:
            changes[self.uuid] = {
                'obj': self,
                'properties': {},
                'old_properties': {},
                'references': {},
                'old_references': {},
                'updated' : False
            }

        #Handle properties for the given instance
        for prop in self._properties:
            name = prop.name
            if not name:
                raise ValueError(f"Property name for {prop} is not set.")
            old_val = getattr(existing, name, None)
            new_val = getattr(self, name, None)

            if old_val != new_val:
                changes[self.uuid]['properties'][name] = new_val
                changes[self.uuid]['old_properties'][name] = old_val

        #Handle references for the given instance
        if include_references:
            for ref in self._references:
                name = ref.name
                if not name:
                    raise ValueError(f"Reference field name is not set.")
                old_val = getattr(existing, name, None)
                new_val = getattr(self, name, None)

                if not _Handle_Referenzes.compare_references(old_val, new_val):
                    changes[self.uuid]['references'][name] = new_val
                    changes[self.uuid]['old_references'][name] = old_val
                
                if recursive:

                    if isinstance(new_val, list):
                        if not isinstance(old_val, list) and old_val != None and old_val != []:
                            raise ValueError(f"Reference {name} is not a list (OLD: {old_val} | NEW: {new_val}) can not compare to a single object.")
                        elif old_val == None or old_val == []:
                            continue
                            #raise NotImplementedError("Adding new items to a list is not implemented yet.")
                            #TODO: Mark for creation
                        for i, ref in enumerate(new_val):
                            if hasattr(ref, '_get_diff') and ref != None and old_val != None and i < len(old_val):
                                rec_changes = ref._get_diff(old_val[i], include_references=include_references, recursive=recursive, changes=changes)
                            elif old_val == None or old_val == [] or i >= len(old_val):
                                continue
                                #TODO: Mark for creation
                                #raise NotImplementedError("Adding new items to a list is not implemented yet.")
                            else:
                                raise ValueError(f"Reference {name} is not a list or a valid reference object - does not inheriate from BaseModel.")
                            changes = changes | rec_changes
                    elif hasattr(new_val, '_get_diff') and new_val != None:
                        rec_changes = new_val._get_diff(old_val, include_references=include_references, recursive=recursive, changes=changes)
                    elif new_val == None and old_val == None:
                        continue
                    elif new_val == None and old_val != None:
                        #TODO: Mark for delete
                        continue
                    else:
                        raise ValueError(f"Reference {name} is not a list or a valid reference object - does not inheriate from BaseModel.")
                    changes = changes | rec_changes

        return changes

    @with_client(require_schema_creation=False)
    def _update(self, changes, auto_create_instances = True, *, client:Optional[WeaviateClient]=None) -> bool:
        """
        Update the object in Weaviate.

        Args:
            changes (dict): A dictionary of changes to apply.
            client (Client): Optional; The Weaviate client to use for updating.

        Returns:
            bool: True if the update was successful.
        """

        if client == None:
            raise ValueError("No client provided.")

        #Get collection object
        collection = self.get_collection(client=client)

        #Update properties
        collection.data.update(
            self.get_uuid(),
            properties=changes[self.uuid]['properties']
        )

        #Update references
        for ref_name, ref in changes[self.uuid]['references'].items():

            reference = getattr(self.__class__, ref_name)

            #Handle single references
            if not isinstance(ref, list) and ref != None:

                #Handle reference entity
                entity_created = _Handle_Referenzes.handle_reference_entity(reference, ref, client=client)

                collection.data.reference_replace(
                    from_uuid=self.get_uuid(),
                    from_property=ref_name,
                    to=ref.get_uuid()
                )
            
            #Handle None references -> delete the reference
            elif ref == None or ref == []:
                # Get old reference
                old_ref = changes[self.uuid]['old_references'].get(ref_name)
                _class = self.__class__
                reference = getattr(_class, ref_name)
                if reference.required:
                    raise ValueError(f"Reference {ref_name} is required and can't be None.")
                self._remove_reference(reference=reference, old_reference_value=old_ref, client=client)
                #raise NotImplementedError(f"Deleting references is not implemented yet.")
                

            #Handle list references #TODO Handle the removing of items in a list!

            # Reference is a list of references
            else:

                # Get ref-diff
                old_ref = changes[self.uuid]['old_references'].get(ref_name)
                new_ref = changes[self.uuid]['references'].get(ref_name)
                diff_dict = _Handle_Referenzes.diff_references(old_ref, new_ref)

                new_ref_objs = []
                for r in ref:
                    # Get reference UUID
                    r_uuid : Any = _Handle_Referenzes._uuid_of(r)

                    # Remove not used references
                    if r_uuid in diff_dict["delete"].keys():
                        collection.data.reference_delete(
                            from_uuid=self.get_uuid(),
                            from_property=ref_name,
                            to=r_uuid
                        )

                    # Add new references entity and add reference
                    elif r_uuid in diff_dict["add"].keys():
                        entity_created, _uuid = _Handle_Referenzes.handle_reference_entity(reference, r, client=client)
                        ref_obj = DataReference(from_uuid=self.get_uuid(), from_property=ref_name, to_uuid=r_uuid)
                        new_ref_objs.append(ref_obj)

                    # Update existing references
                    collection.data.reference_replace(
                        from_uuid=self.get_uuid(),
                        from_property=ref_name,
                        to=r_uuid
                    )

                # Add all new references
                if new_ref_objs != []:
                    collection.data.reference_add_many(new_ref_objs)

        return True