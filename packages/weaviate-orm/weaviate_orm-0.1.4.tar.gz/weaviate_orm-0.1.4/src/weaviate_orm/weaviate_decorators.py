from functools import wraps
from weaviate import WeaviateClient
from typing import Optional
import asyncio

class _EventLoopSingleton:
    _instance = None

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def run_until_complete(self, coro, *args, **kwargs):
        # If you prefer run_until_complete:
        return self.loop.run_until_complete(coro(*args, **kwargs))
        # If you prefer thread-safe approach:
        # return asyncio.run_coroutine_threadsafe(coro(*args, **kwargs), self.loop).result()

def syncify(async_method):
    """
    Method decorator: converts an async method into a sync method
    by running it on an event loop.
    """
    @wraps(async_method)
    def wrapper(*args, **kwargs):
        loop = _EventLoopSingleton.get_instance().loop
        return loop.run_until_complete(async_method(*args, **kwargs))
    return wrapper

def with_client(require_schema_creation=False):
    """
    Decorator that provides a Weaviate client to the wrapped method.

    The wrapped method must have a signature like:
        def method(self, ..., client=None):
            ...

    If the caller doesn't pass 'client=...', we fetch the default from
    self (or cls) via self._engine.client.

    If require_schema_creation=True, we could ensure the schema is created
    right before the operation. But typically, we rely on create_all_schemas()
    being called up-front.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self_or_cls, *args, client:Optional[WeaviateClient]=None, **kwargs):
            # Attempt to get a client:
            # 1) If the user passed in a 'client', use it
            # 2) Otherwise fetch from self_or_cls._engine.client
            if client is not None:
                local_client = client
            else:
                if not hasattr(self_or_cls, "_engine") or self_or_cls._engine is None:
                    raise ValueError("No client provided and _engine is not bound.")
                local_client = self_or_cls._engine.client

            # Optionally ensure schema creation (if you don't do it up front)
            if require_schema_creation and hasattr(self_or_cls._engine, "ensure_schema_for"):
                self_or_cls._engine.ensure_schema_for(self_or_cls)

            return func(self_or_cls, *args, client=local_client, **kwargs)
        return wrapper
    return decorator
