import asyncio
import inspect
from typing import (
    Any,
    Callable,
    Concatenate,
    Coroutine,
    ParamSpec,
    Sequence,
    TypeVar, Literal,
)

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

F = TypeVar("F", bound=DeclarativeBase)
T = TypeVar("T", bound=BaseModel)
P = ParamSpec("P")

class NoFuncType:
    """Marker that the mapping is registered intentionally without a function."""

_NoFunc = NoFuncType()

class ObjectMapper:
    def __new__(cls, *args, **kwargs):
        raise TypeError(f"It is not possible to create {cls.__name__} instance")

    # {from_class: {to_class: funс}}
    _mappers_single: dict[type, dict[type, Callable | NoFuncType]] = {}
    _mappers_bulk: dict[type, dict[type, Callable | NoFuncType]] = {}

    __scopes = {"single", "bulk"}

    @staticmethod
    def _validate_from_cls(cls: type[F]):
        if not issubclass(cls, DeclarativeBase):
            raise TypeError("from_ must be a class inheriting from sqlalchemy.orm.DeclarativeBase")

    @staticmethod
    def _validate_to_cls(cls: type[T]):
        if not issubclass(cls, BaseModel):
            raise TypeError("to_ must be a class inheriting from pydantic.BaseModel")

    @classmethod
    def _validate_already_registered(cls, from_: type[F], to: type[T], *, is_bulk: bool):
        mapper = cls._mappers_bulk if is_bulk else cls._mappers_single
        if from_ in mapper and to in mapper[from_]:
            raise KeyError(
                f"A {"bulk" if is_bulk else ""} mapping from {from_.__name__} to {to.__name__} is already registered."
            )

    @staticmethod
    def _validate_pydantic_from_attributes(to: type[T]):
        config = getattr(to, "model_config", None)
        if not (config and config.get("from_attributes", False)):
            raise ValueError(
                f"Pydantic-model {to.__name__} doesn't have "
                f"model_config = ConfigDict(from_attributes=True), "
                f"and the custom mapping function has not been passed."
            )

    @classmethod
    def register(
            cls,
            from_: type[F],
            to: type[T],
            *,
            func: Callable[[Concatenate[F, P]], T | Coroutine[Any, Any, T]] | None = None,
            override_existing: bool = False,
    ):
        """
        Registers a mapping function between a SQLAlchemy ORM class and a Pydantic model class.

        This method allows specifying a custom function that converts instances of the
        `from_` class (subclass of `DeclarativeBase`) into instances of the `to` class
        (subclass of `BaseModel`). If no function is provided, Pydantic's fallback
        mapping (`model_validate` with `from_attributes=True`) is used, provided that
        the Pydantic model is configured to allow attribute-based initialization.

        :param from_: The SQLAlchemy ORM class to map from. Must inherit from `DeclarativeBase`.
        :param to: The Pydantic model class to map to. Must inherit from `BaseModel`.
        :param func: Optional; a callable that takes an instance of `from_` and returns
        an instance of `to`, or an awaitable returning `to`.
        :param override_existing: If True mapping can be re-registered
        :return: The registered function if provided, otherwise a decorator to register a function.
        :raises TypeError: If `from_` is not a subclass of `DeclarativeBase` or `to` is not a subclass of `BaseModel`.
        :raises ValueError: If `to` does not have `model_config = ConfigDict(from_attributes=True)` and no custom function is provided.
        :raises KeyError: If mapping with `from_` and `to` already exists and ``override_existing`` is not ``True``.
        Notes
        -----
        - If a function is provided via `func`, it is used for mapping calls.
        - If no function is provided, the fallback mapping relies on Pydantic's
          `model_validate(from_, from_attributes=True)`, which requires that
          objects do not contain lazy-loaded attributes.
        - Can be used as a decorator to register a mapping function after method definition.
        """
        cls._validate_from_cls(from_)
        cls._validate_to_cls(to)

        if not override_existing:
            cls._validate_already_registered(from_, to, is_bulk=False)

        def decorator(f: Callable[[Concatenate[F, P]], T | Coroutine[Any, Any, T]]):
            cls._mappers_single.setdefault(from_, {})[to] = f
            return f

        if func is not None:
            cls._mappers_single.setdefault(from_, {})[to] = func
            return func
        else:
            cls._validate_pydantic_from_attributes(to)
            cls._mappers_single.setdefault(from_, {})[to] = _NoFunc
        return decorator

    @classmethod
    def register_bulk(
            cls,
            from_: type[F],
            to: type[T],
            *,
            func: Callable[[Concatenate[Sequence[F], P]], Sequence[T] | Coroutine[Any, Any, Sequence[T]]] | None = None,
            override_existing: bool = False,
    ):
        """
        Registers a mapping function between a Sequence of SQLAlchemy ORM classes and a Sequence of Pydantic model classes.

        This method allows specifying a custom function that converts sequence of instances of the
        `from_` class (subclass of `DeclarativeBase`) into sequence of instances of the `to` class
        (subclass of `BaseModel`). If no function is provided, Pydantic's fallback
        mapping (`model_validate` with `from_attributes=True`) is used for each sequence element and ``list`` of models is returned,
        it is also provided that the Pydantic model is configured to allow attribute-based initialization.

        :param from_: The SQLAlchemy ORM class to map from. Must inherit from `DeclarativeBase`.
        :param to: The Pydantic model class to map to. Must inherit from `BaseModel`.
        :param func: Optional; a callable that takes a sequence of instances of `from_` and returns
        a sequence of instance of `to`, or an awaitable returning a sequence of `to`.
        :param override_existing: If True mapping for sequences can be re-registered
        :return: The registered function if provided, otherwise a decorator to register a function.
        :raises TypeError: If `from_` is not a subclass of `DeclarativeBase` or `to` is not a subclass of `BaseModel`.
        :raises ValueError: If `to` does not have `model_config = ConfigDict(from_attributes=True)` and no custom function is provided.
        :raises KeyError: If mapping with `from_` and `to` already exists and ``override_existing`` is not ``True``.
        Notes
        -----
        - If a function is provided via `func`, it is used for mapping calls.
        - If no function is provided, the fallback mapping relies on Pydantic's
          `model_validate(from_, from_attributes=True)`, which requires that
          objects do not contain lazy-loaded attributes.
        - Can be used as a decorator to register a mapping function after method definition.
        """
        cls._validate_from_cls(from_)
        cls._validate_to_cls(to)

        if not override_existing:
            cls._validate_already_registered(from_, to, is_bulk=True)

        def decorator(f: Callable[[Concatenate[Sequence[F], P]], T | Coroutine[Any, Any, Sequence[T]]]):
            cls._mappers_bulk.setdefault(from_, {})[to] = f
            return f

        if func is not None:
            cls._mappers_bulk.setdefault(from_, {})[to] = func
            return func
        else:
            cls._validate_pydantic_from_attributes(to)
            cls._mappers_bulk.setdefault(from_, {})[to] = _NoFunc
        return decorator

    @classmethod
    def unregister(cls, from_: type[F], to: type[T], *, scope: Literal['single', 'bulk'] | None = None) -> None:
        """
        Removes a registered mapping between a SQLAlchemy ORM class and a Pydantic model class.

        :param from_: The SQLAlchemy ORM class of the mapping to remove.
        :param to: The Pydantic model class of the mapping to remove.
        :param scope: Optional; one of {"single", "many"} to remove from a specific registry. If None, tries to remove from both.
        :raises KeyError: If mapping not found in the specified (or both) scopes.
        """
        def _remove(mapping: dict[type, dict[type, Callable]]):
            if from_ in mapping and to in mapping[from_]:
                mapping[from_].pop(to)
                if not mapping[from_]:
                    mapping.pop(from_)
                return True
            return False

        if scope is not None:
            if scope not in cls.__scopes:
                raise ValueError("scope must be one of {\"single\", \"bulk\"}")

            if scope == "single":
                if not _remove(cls._mappers_single):
                    raise KeyError(f"No single-object mapping {from_.__name__} -> {to.__name__}")
            else:
                if not _remove(cls._mappers_bulk):
                    raise KeyError(f"No sequence mapping {from_.__name__} -> {to.__name__}")
            return

        removed = _remove(cls._mappers_single) or _remove(cls._mappers_bulk)
        if not removed:
            raise KeyError(f"No mapping {from_.__name__} -> {to.__name__} found in any scope")

    @classmethod
    def is_registered(cls, from_: type[F], to: type[T],*, scope: Literal["single", "bulk"]) -> bool:
        if scope not in cls.__scopes:
            raise ValueError("scope must be one of {\"single\", \"bulk\"}")
        mapper = cls._mappers_bulk if scope == "bulk" else cls._mappers_single
        return from_ in mapper and to in mapper[from_]

    @classmethod
    def clear(cls, *, scope: Literal["single", "bulk"] | None = None) -> None:
        """
        Clears registered mappings.

        :param scope: Optional; one of {"single", "bulk"}. If None, clears all mappings.
        """
        if scope is not None:
            if scope not in cls.__scopes:
                raise ValueError('scope must be one of {"single", "bulk"}')

            if scope == "single":
                cls._mappers_single.clear()
            else:  # scope == "bulk"
                cls._mappers_bulk.clear()
            return

        cls._mappers_single.clear()
        cls._mappers_bulk.clear()

    @classmethod
    def list_mappers(cls, *, scope: Literal["single", "bulk"]) -> list[tuple[type, type]]:
        """
        Returns a list of all registered mapping pairs.

        :param scope: Optional; one of {"single", "bulk"}. If None, returns mappings from both scopes.
        :return: List of tuples (from_class, to_class).
        """
        if scope not in cls.__scopes:
            raise ValueError('scope must be one of {"single", "bulk"}')

        mapping = cls._mappers_single if scope == "single" else cls._mappers_bulk
        return [(f, t) for f, sub in mapping.items() for t in sub]

    @classmethod
    async def map(cls, from_: F, to: type[T], **func_kwargs: Any) -> T:
        """
        Asynchronously maps a SQLAlchemy ORM object to a Pydantic model instance.

        This method converts the provided `from_` object (an instance of a class
        inheriting from `DeclarativeBase`) into an instance of the `to` class
        (subclass of `BaseModel`). The conversion is performed either via a
        registered custom mapping function or, if none is available, through
        Pydantic's fallback mechanism (`model_validate` with `from_attributes=True`).

        :param from_: A SQLAlchemy ORM object to be mapped.
        :param to: The Pydantic model class to map the object to.
        :param func_kwargs: ``Optional``, Keyword arguments to pass to the registered custom mapping function.
        Only keys listed in `func_kwargs` during registration will be used.
        :return: A Pydantic model instance resulting from the mapping.
        :raises KeyError: If no custom mapping function is registered for `to` and fallback mapping is not possible.

        Notes
        -----
        - If no mapping function is registered, fallback mapping uses
        - `to.model_validate(from_, from_attributes=True)`. The `from_` object
          must not contain lazy-loaded attributes to avoid unexpected database
          queries or `DetachedInstanceError`.
        """
        func = cls._mappers_single.get(type(from_), {}).get(to)

        if func is _NoFunc:
            # fallback if func is intentionally not set
            return to.model_validate(from_, from_attributes=True)
        elif func is None:
            # fallback
            raise KeyError(
                f"No bulk mapping registered for {type(from_).__name__} -> {to.__name__}"
            )

        result = func(from_, **func_kwargs)

        if inspect.isawaitable(result):
            return await result
        return result

    @classmethod
    async def map_each(
            cls, from_items: Sequence[F], to: type[T], **func_kwargs: Any
    ) -> Sequence[T]:
        """
        Asynchronously maps a sequence of SQLAlchemy ORM objects to Pydantic model instances,
        applying the single-object mapping function to each item individually.

        This method iterates over the provided sequence of `from_items` (instances of a class
        inheriting from `DeclarativeBase`) and maps each object into an instance of the `to` class
        (subclass of `BaseModel`). The conversion for each object is performed either via a
        registered single-object mapping function or, if none is available, through Pydantic's
        fallback mechanism (`model_validate` with `from_attributes=True`).

        ⚠️ This method is not a bulk-mapping function: the mapping function is called separately
        for each object in the sequence. To register or use a true bulk mapping
        (`Sequence[from_] -> Sequence[to]`), use `register_bulk` and `map_bulk`.

        :param from_items: A sequence of SQLAlchemy ORM objects to be mapped one by one.
        :param to: The Pydantic model class to map the objects to.
        :param func_kwargs: Optional keyword arguments passed to the registered single-object mapping function.
        :returns A list of Pydantic model instances resulting from per-item mapping.
        :raises KeyError: If no single-object mapping function is registered for `to` and fallback mapping is not possible.

        Notes
        -----
        - Each object is mapped independently.
        - If no mapping function is registered, fallback mapping uses
          `to.model_validate(from_, from_attributes=True)`.
        - The `from_` objects must not contain lazy-loaded attributes to avoid unexpected database
          queries or `DetachedInstanceError`.
        """
        if not from_items:
            return []

        func = cls._mappers_single.get(type(from_items[0]), {}).get(to)

        if func is _NoFunc:
            # fallback if func is intentionally not set
            return [
                to.model_validate(item, from_attributes=True) for item in from_items
            ]
        elif func is None:
            # fallback
            raise KeyError(
                f"No bulk mapping registered for {type(from_items[0]).__name__} -> {to.__name__}"
            )

        first_res = func(from_items[0], **func_kwargs)

        if inspect.isawaitable(first_res):
            coros = [first_res]
            coros.extend([func(item, **func_kwargs) for item in from_items[1:]])
            return await asyncio.gather(*coros)
        else:
            res = [first_res]
            res.extend([func(item, **func_kwargs) for item in from_items[1:]])
            return res


    @classmethod
    async def map_bulk(cls, from_items: Sequence[F], to: type[T], **func_kwargs: Any
    ) -> Sequence[T]:
        """
        Asynchronously maps a sequence of SQLAlchemy ORM objects to Pydantic model instances
        using a registered bulk mapping function.

        This method passes the entire `from_items` sequence (instances of a class
        inheriting from `DeclarativeBase`) to a single registered bulk mapping function
        that converts it into a list of instances of the `to` class (subclass of `BaseModel`).

        ⚠️ This method performs a true bulk mapping: the mapping function is called **once**
        for the entire sequence. It is different from `map_each`, which maps objects individually.

        :param from_items: A sequence of SQLAlchemy ORM objects to be mapped in bulk.
        :param to: The Pydantic model class to map the objects to.
        :param func_kwargs: Optional keyword arguments passed to the registered bulk mapping function.
        :return: A sequence of Pydantic model instances resulting from the bulk mapping.
        :raises KeyError: If no bulk mapping function is registered for `to`.

        Notes
        -----
        - The mapping function should accept the entire sequence and return a list of model instances.
        - If no bulk function is registered, fallback mapping is performed per-item
          using `to.model_validate(from_, from_attributes=True)`.
        - Useful for optimized transformations when working with many objects at once.
        - The bulk function may be asynchronous or synchronous.
        """
        if not from_items:
            return []

        func = cls._mappers_bulk.get(type(from_items[0]), {}).get(to)

        if func is _NoFunc:
            # fallback if func is intentionally not set
            return [
                to.model_validate(item, from_attributes=True) for item in from_items
            ]
        elif func is None:
            # fallback
            raise KeyError(
                f"No bulk mapping registered for {type(from_items[0]).__name__} -> {to.__name__}"
            )

        res = func(from_items, **func_kwargs)

        if inspect.isawaitable(res):
            return await res

        return res
