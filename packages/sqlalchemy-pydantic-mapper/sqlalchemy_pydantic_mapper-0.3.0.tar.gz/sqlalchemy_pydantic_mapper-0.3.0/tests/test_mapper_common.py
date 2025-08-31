import pytest

from src.sqlalchemy_pydantic_mapper import ObjectMapper
from tests.helpers import UserDB, UserSchema


def test_create_instance_from_mapper(object_mapper: ObjectMapper):
    with pytest.raises(TypeError):
        object_mapper()

def test_invalid_unregister_scope(object_mapper: ObjectMapper):
    with pytest.raises(ValueError):
        object_mapper.unregister(UserDB, UserSchema, scope='bad')

def test_invalid_is_registered_scope(object_mapper: ObjectMapper):
    with pytest.raises(ValueError):
        object_mapper.is_registered(UserDB, UserSchema, scope='bad')

def test_invalid_clear_scope(object_mapper: ObjectMapper):
    with pytest.raises(ValueError):
        object_mapper.clear(scope='bad')

def test_invalid_list_mappers_scope(object_mapper: ObjectMapper):
    with pytest.raises(ValueError):
        object_mapper.list_mappers(scope='bad')