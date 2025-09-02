import inspect
from importlib import import_module
from typing import get_origin, get_args, Any

import pytest
from pydantic import BaseModel, RootModel


@pytest.fixture(scope="session")
def models_module():
    # Import once; fails fast if unresolved imports / syntax errors
    return import_module("mixam_public_api.models")


def iter_pydantic_models(mod):
    for name, obj in inspect.getmembers(mod):
        # Only classes defined in this module (skip imported bases)
        if inspect.isclass(obj) and obj.__module__ == mod.__name__:
            if issubclass(obj, BaseModel) or issubclass(obj, RootModel):
                yield name, obj


def test_models_module_imports(models_module):
    # Smoke test: just importing the models shouldn't raise.
    assert models_module is not None


def test_all_models_generate_json_schema(models_module):
    # This catches unresolved forward refs, bad field types, etc.
    failures = []
    for name, cls in iter_pydantic_models(models_module):
        try:
            _ = cls.model_json_schema()
        except Exception as e:  # pragma: no cover - we want to see exact failures
            failures.append((name, repr(e)))
    if failures:
        msgs = "\n".join(f"- {n}: {err}" for n, err in failures)
        pytest.fail(f"Some models couldn't produce JSON Schema:\n{msgs}")


def _has_required_fields(cls: type[BaseModel]) -> bool:
    # Pydantic v2: field.is_required() tells us if value is required
    for f in cls.model_fields.values():
        if f.is_required():
            return True
    return False


def _example_value_for(annotation: Any):
    """Very small sampler for common primitives; used when a RootModel[T] has T required."""
    origin = get_origin(annotation)
    args = get_args(annotation)
    t = annotation if origin is None else origin
    if t in (str,):
        return "x"
    if t in (int,):
        return 0
    if t in (float,):
        return 0.0
    if t in (bool,):
        return False
    if t in (list, tuple, set):
        return []
    if t in (dict,):
        return {}
    # Fallback: None (many unions/optionals will accept it)
    return None


def test_can_construct_optionally_typed_models(models_module):
    """
    For models with no required fields, ensure we can instantiate and round-trip.
    For RootModel[T], try a minimal value of T.
    """
    failures = []
    for name, cls in iter_pydantic_models(models_module):
        try:
            if issubclass(cls, RootModel):
                # RootModel needs an inner value; try minimal based on inner type
                inner_ann = cls.__pydantic_generic_metadata__.get("args")
                # When not generic, Pydantic stores the annotation on __root_type__ in v2:
                inner_ann = getattr(cls, "__root_type__", None) or inner_ann
                value = _example_value_for(inner_ann)
                m = cls(value)
            else:
                if _has_required_fields(cls):
                    # Skip strictly required models; we only smoke-test that schema existed above
                    continue
                m = cls()  # all-optional
            # Make sure we can serialize/deserialize
            m = cls.model_validate(m.model_dump())  # coerce defaults to proper types
            dumped = m.model_dump_json()
            cls.model_validate_json(dumped)
        except Exception as e:
            failures.append((name, repr(e)))
    if failures:
        msgs = "\n".join(f"- {n}: {err}" for n, err in failures)
        pytest.fail(f"Some optional models couldn't be instantiated/round-tripped:\n{msgs}")
