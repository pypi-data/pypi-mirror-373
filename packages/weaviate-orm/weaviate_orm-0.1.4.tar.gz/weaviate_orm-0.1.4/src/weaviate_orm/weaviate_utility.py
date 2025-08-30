from __future__ import annotations

import inspect
from typing import Any, Dict, Type, Tuple, Callable, Optional, List, Iterable, Union, TYPE_CHECKING
from uuid import UUID

from weaviate import WeaviateClient

from .weavitae_reference import Reference_Type, Reference

if TYPE_CHECKING:
    from .weaviate_base import Base_Model

def validate_method_params(method: Callable, params: Dict[str, Any]) -> Optional[Type]:
    """
    Validate that `params` contain all required arguments with correct types for `method`.
    Returns the expected return type if specified in the function signature.

    Args:
        method (callable): The method to validate.
        params (Dict[str, Any]): The parameters to validate. Keys are parameter names.

    Returns:
        Type: The expected return type of the method. None if not specified.
    """
    
    # Get function signature
    sig = inspect.signature(method)

    # Extract required parameters and their expected types
    required_params = {
        k: v.annotation
        for k, v in sig.parameters.items()
        if v.default == inspect.Parameter.empty and not (k == 'self' or k == 'cls')  # Only required params
    }

    # Check for missing required parameters
    missing_params = [param for param in required_params if param not in params]
    if missing_params:
        raise ValueError(f"Missing required parameters: {missing_params}")

    # Validate types if type hints exist
    for param, expected_type in required_params.items():
        if expected_type is not inspect.Parameter.empty and not isinstance(params[param], expected_type):
            raise TypeError(f"Parameter '{param}' should be {expected_type}, got {type(params[param])}")

    # Extract return type if specified
    return_type = sig.return_annotation
    return return_type if return_type is not inspect.Signature.empty else None

def compare_instance(instance_a: Any, instance_b: Any) -> bool:

    #Try get an uuid
    uuid_a = None
    uuid_b = None

    if hasattr(instance_a, 'get_uuid'):
        uuid_a = instance_a.get_uuid()
    elif isinstance(instance_a, UUID):
        uuid_a = instance_a
    if hasattr(instance_b, 'get_uuid'):
        uuid_b = instance_b.get_uuid()
    elif isinstance(instance_b, UUID):
        uuid_b = instance_b

    #Check equality
    if uuid_a and uuid_b:
        return uuid_a == uuid_b
    else:
        return instance_a == instance_b

class _Handle_Referenzes():

    @staticmethod
    def _get_relevant_referenzes(client:WeaviateClient, reference_collection=None) -> Dict[str, list[str]]:
        """Get all references in the Weaviate schema that point to a specific collection.
        
        Args:
            client (WeaviateClient): The Weaviate client to use.
            target_collection (str): The name of the target collection to search for. If None, all references are returned.

        Returns:
            Dict[str, List[str]]: A dictionary of collection names and their references.
        """
    
        shema = client.collections.list_all()
        refs = {}
        rel_refs = []

        for col_name, col in shema.items():

            if reference_collection:
                rel_refs = [ref.name for ref in col.references if reference_collection in ref.target_collections]
            else:
                rel_refs = [ref.name for ref in col.references]

            if rel_refs and rel_refs != []:
                refs[col_name] = rel_refs

        return refs

    @staticmethod
    def _generate_graphql_query_for_referenzes(referenzes:Dict[str, list[str]], reference_collection:str, to_uuid:UUID) -> dict[str, str]:
        """Generate a GraphQL query string to retrieve all referenzes.
        
        Args:
            referenzes (Dict[str, List[str]]): A dictionary of collection names and their references.

        Returns:
            str: The generated GraphQL query string.
        """
    
        graphql_queries = {}
        refs = referenzes


        nl = ',\n'

        for col, col_refs in refs.items():
            operands = []
            outputs = []

            #Generate an operand per ref
            for ref in col_refs:
                q = f"""
                {{
                    path: ["{ref}", "{reference_collection}", "id"],
                    operator: Equal,
                    valueText: "{to_uuid}"
                }}"""

                o = f"""
                    {ref}{{
                        ... on Author {{
                            _additional {{
                            id
                            }}
                        }}
                        }}
                        """

                operands.append(q)
                outputs.append(o)

            #Generate Query per Collection
            output = '\n'.join(outputs)
            col_q = f"""
            {{
                Get {{
                    {col}(
                        where : {{
                            operator: Or
                            operands : [ {nl.join(operands)}
                            ]
                        }}
                    ){{
                        _additional {{
                            id
                        }}
                        {output}
                        
                    }}

                }}      
            }}"""

            graphql_queries[col] = col_q

        return graphql_queries
    
    @staticmethod
    def get_referenzes(client:WeaviateClient, reference_collection:str, to_uuid:UUID) -> dict:

        referenzes = {}

        #Get all relevant referenzes
        refs = _Handle_Referenzes._get_relevant_referenzes(client, reference_collection)

        #Generate GraphQL Queries
        queries = _Handle_Referenzes._generate_graphql_query_for_referenzes(refs, reference_collection, to_uuid)

        #Execute Queries
        for col, query in queries.items():
            resp = client.graphql_raw_query(query)

            #Check if the collection is in the response #GEÄNDERT 08.04 THE
            if col not in resp.get.keys() or resp.get[col] == [] or resp.get[col] is None:
                continue

            referenzes[col] = {}

            for obj in resp.get[col]:
                referenzes[col][obj["_additional"]["id"]] = {}
                for key, prop in obj.items():
                    if key != "_additional" and prop:
                        
                        elements = [element["_additional"]["id"] for element in prop if element["_additional"]["id"] == to_uuid]
                        if elements and elements != []:
                            referenzes[col][obj["_additional"]["id"]][key] = elements

        return referenzes

    @staticmethod
    def handle_reference_entity(reference: Reference, reference_value:Union[Base_Model, UUID], auto_create_entity:bool=True, client:Optional[WeaviateClient]=None) -> tuple[bool, UUID]:

        success = False

        target_class = reference._get_target_class()

        # Check existence
        ref_exists = False
        if hasattr(reference_value, 'exists') and hasattr(reference_value, '_weaviate_schema') and not isinstance(reference_value, UUID): #Check if is instance of Base_Model avoiding circular imports
            ref_exists = reference_value.exists
            _ref = reference_value
            _uuid = _ref.get_uuid()
        elif isinstance(reference_value, UUID):
            ref_exists = target_class.instance_exists(reference_value, client=client)
            if ref_exists:
                _ref = target_class.get(reference_value, client=client)
                _uuid = _ref
        else:
            raise ValueError(f"Reference value {reference_value} : {reference.name} is not a valid reference object - must be an instance of Base_Model or UUID.")
        
        #DEBUG
        if not isinstance(_uuid, UUID):
            raise ValueError(f"Reference value {reference_value} : {reference.name} does not have a valid UUID.")

        # Handle reference
        if ref_exists:
            return success, _uuid
            #TODO Add warning -> No creation necessary!
        elif not ref_exists and not auto_create_entity:
            raise ValueError(f"Reference value {reference_value} : {reference.name} does not exist in Weaviate and auto_create_entity is False.")
        elif _ref is None:
            raise ValueError(f"Reference value with UUID {reference_value} : {reference.name} does not exist in Weaviate and can't be created from UUID")
        else:
            success = _ref.save(client=client, include_references=True, recursive=True)

        return success, _uuid

    @staticmethod
    def _uuid_of(x: Any) -> Optional[UUID]:
        """
        Normalize to lowercase UUID string, or None if not available/invalid.
        Accepts: UUID, str(UUID), or object with .get_uuid() returning either.
        """
        if x is None:
            return None
        if isinstance(x, UUID):
            return x
        if isinstance(x, str):
            try:
                return UUID(x)
            except Exception:
                return None
        if hasattr(x, "get_uuid"):
            try:
                val = x.get_uuid()
            except Exception:
                return None
            return _Handle_Referenzes._uuid_of(val)
        return None



    # ---------- single & list compare ----------
    @staticmethod
    def _compare_single_reference(ref_a: Any, ref_b: Any) -> bool:
        """Compare two SINGLE references allowing UUID or obj with get_uuid()."""
        if ref_a is None and ref_b is None:
            return True
        if ref_a is None or ref_b is None:
            return False
        ua = _Handle_Referenzes._uuid_of(ref_a)
        ub = _Handle_Referenzes._uuid_of(ref_b)
        return ua is not None and ua == ub

    @staticmethod
    def compare_references(
        ref_a: Any,
        ref_b: Any,
        *,
        order_sensitive: bool = False
    ) -> bool:
        """
        Compare two references (SINGLE or LIST).
        - order_sensitive=True: lists must match in order (your current behavior).
        - order_sensitive=False: treat lists as sets of UUIDs (order ignored).
        """
        a_is_list = isinstance(ref_a, list)
        b_is_list = isinstance(ref_b, list)

        if a_is_list and b_is_list:
            # Normalize to UUID lists (drop None/invalids)
            ua = [_Handle_Referenzes._uuid_of(x) for x in ref_a]
            ub = [_Handle_Referenzes._uuid_of(x) for x in ref_b]
            ua = [u for u in ua if u is not None]
            ub = [u for u in ub if u is not None]

            if order_sensitive:
                return ua == ub
            else:
                # Treat as sets (deduplicate) – good for Weaviate refs
                return set(ua) == set(ub)

        if a_is_list and ref_b is None:
            return len(ref_a) == 0
        if b_is_list and ref_a is None:
            return len(ref_b) == 0
        if a_is_list != b_is_list:
            return False

        # single vs single
        return _Handle_Referenzes._compare_single_reference(ref_a, ref_b)

    # ---------- diffs ----------
    @staticmethod
    def diff_references(
        old: Optional[Iterable[Any]],
        new: Optional[Iterable[Any]],
        *,
        order_sensitive: bool = False,
    ) -> Dict[str, Dict]:
        """
        Compute additions and deletions to turn list 'old' into list 'new'.

        Returns dict with:
          - add:    [{"id": <uuid>, "index": <idx_in_new>}, ...]
          - delete: [{"id": <uuid>, "index": <idx_in_old>}, ...]
          - keep:   [{"id": <uuid>, "old_index": i, "new_index": j}, ...]  (handy for logs/tests)

        Behavior:
          - order_sensitive=True  -> minimal add/delete script via LCS
          - order_sensitive=False -> set math on UUIDs (fast), first occurrence index
        """
        old_list = list(old or [])
        new_list = list(new or [])

        old_ids = [_Handle_Referenzes._uuid_of(x) for x in old_list]
        new_ids = [_Handle_Referenzes._uuid_of(x) for x in new_list]
        # Drop items without valid UUIDs
        old_ids = [u for u in old_ids if u is not None]
        new_ids = [u for u in new_ids if u is not None]

        if not order_sensitive:
            # --- order-insensitive: set-based diff ---
            set_old, set_new = set(old_ids), set(new_ids)

            # map first occurrence index for stable reporting
            first_idx_old: Dict[UUID, int] = {}
            for i, u in enumerate(old_ids):
                first_idx_old.setdefault(u, i)

            first_idx_new: Dict[UUID, int] = {}
            for j, u in enumerate(new_ids):
                first_idx_new.setdefault(u, j)

            add_ids = sorted(set_new - set_old, key=lambda u: first_idx_new[u])
            del_ids = sorted(set_old - set_new, key=lambda u: first_idx_old[u])

            add = {u : first_idx_new[u] for u in add_ids}
            delete = {u : first_idx_old[u] for u in del_ids}
            # keep (unordered; we still expose one mapping using first indices)
            keep_ids = set_old & set_new
            keep = {u : (first_idx_old[u], first_idx_new[u]) for u in sorted(keep_ids, key=lambda u: first_idx_old[u])}

            return {"add": add, "delete": delete, "keep": keep}

        # --- order-sensitive: LCS-backed minimal edit script ---
        # Build DP for LCS on the UUID sequences
        n, m = len(old_ids), len(new_ids)
        dp = [[0]*(m+1) for _ in range(n+1)]
        for i in range(n-1, -1, -1):
            oi = old_ids[i]
            for j in range(m-1, -1, -1):
                dp[i][j] = 1 + dp[i+1][j+1] if oi == new_ids[j] else max(dp[i+1][j], dp[i][j+1])

        # Recover LCS positions
        i = j = 0
        keep_positions: List[Tuple[int, int, UUID]] = []
        while i < n and j < m:
            if old_ids[i] == new_ids[j]:
                keep_positions.append((i, j, old_ids[i]))
                i += 1
                j += 1
            elif dp[i+1][j] >= dp[i][j+1]:
                i += 1
            else:
                j += 1

        keep_i = {i for (i, _j, _u) in keep_positions}
        keep_j = {j for (_i, j, _u) in keep_positions}

        delete = {old_ids[i] :  i for i in range(n) if i not in keep_i}
        add    = {new_ids[j] :  j for j in range(m) if j not in keep_j}
        keep   = {u: (i, j) for (i, j, u) in keep_positions}

        return {"add": add, "delete": delete, "keep": keep}