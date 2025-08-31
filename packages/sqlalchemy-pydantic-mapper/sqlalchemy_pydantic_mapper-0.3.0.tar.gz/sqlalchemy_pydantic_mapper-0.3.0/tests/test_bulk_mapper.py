import pytest

from src.sqlalchemy_pydantic_mapper import ObjectMapper
from src.sqlalchemy_pydantic_mapper.ObjectMapper import _NoFunc
from tests.helpers import UserDB, UserSchema, StudSchema, StudentDB, BadDB, BadSchema


def test_register_direct(object_mapper: ObjectMapper):
    def mapper(dbs: list[UserDB]) -> list[UserSchema]:
        return [UserSchema(id=db.id, name=db.name) for db in dbs]

    object_mapper.register_bulk(UserDB, UserSchema, func=mapper)
    assert object_mapper._mappers_bulk[UserDB][UserSchema] is mapper


def test_register_decorator(object_mapper: ObjectMapper):
    @object_mapper.register_bulk(UserDB, UserSchema)
    def mapper2(dbs: list[UserDB]) -> list[UserSchema]:
        return [UserSchema(id=db.id, name=db.name) for db in dbs]

    assert object_mapper._mappers_bulk[UserDB][UserSchema] is mapper2


async def test_auto_mapping(object_mapper: ObjectMapper):
    object_mapper.register_bulk(StudentDB, UserSchema)
    stud = StudentDB()
    stud.id = 2
    stud.name = "Bob"

    result = await object_mapper.map_bulk([stud], UserSchema)
    assert result[0].id == 2
    assert result[0].name == "Bob"


async def test_manual_mapping(object_mapper: ObjectMapper):
    def stud_to_user(dbs: list[StudentDB]) -> list[StudSchema]:
        return [StudSchema(id=db.id, name=db.name.upper()) for db in dbs]
    object_mapper.register_bulk(StudentDB, StudSchema, func=stud_to_user)
    print(object_mapper._mappers_bulk)
    stud = StudentDB()
    stud.id = 2
    stud.name = "Bob"

    result = await ObjectMapper.map_bulk([stud], StudSchema)
    assert result[0].id == 2
    assert result[0].name == "BOB"

async def test_manual_mapping_async(object_mapper: ObjectMapper):
    async def stud_to_user(dbs: list[StudentDB]) -> list[StudSchema]:
        return [StudSchema(id=db.id, name=db.name.upper()) for db in dbs]
    object_mapper.register_bulk(StudentDB, StudSchema, func=stud_to_user)
    print(object_mapper._mappers_bulk)
    stud = StudentDB()
    stud.id = 2
    stud.name = "Bob"

    result = await ObjectMapper.map_bulk([stud], StudSchema)
    assert result[0].id == 2
    assert result[0].name == "BOB"

async def test_map_bulk_no_func(object_mapper: ObjectMapper):
    ObjectMapper.clear()
    ObjectMapper.register_bulk(UserDB, UserSchema)
    users = [UserDB(id=1, name="Alice"), UserDB(id=2, name="Bob")]
    results = await ObjectMapper.map_bulk(users, UserSchema)
    assert len(results) == 2
    assert results[0].name == "Alice"
    assert results[1].name == "Bob"


async def test_map_bulk_with_func_kwargs(object_mapper: ObjectMapper):
    async def mapper_with_session(users_: list[UserDB], session: str) -> list[UserSchema]:
        return [UserSchema(id=user.id, name=f"{user.name}-{session}") for user in users_]

    object_mapper.register_bulk(UserDB, UserSchema, func=mapper_with_session)

    users = [UserDB(id=1, name="Alice"), UserDB(id=2, name="Bob")]
    results = await object_mapper.map_bulk(users, UserSchema, session="X")
    assert results[0].name == "Alice-X"
    assert results[1].name == "Bob-X"


async def test_map_bulk_empty_sequence(object_mapper: ObjectMapper):
    object_mapper.register_bulk(UserDB, UserSchema)
    results = await ObjectMapper.map_bulk([], UserSchema)
    assert results == []


async def test_unregister(object_mapper: ObjectMapper):
    object_mapper.register_bulk(UserDB, UserSchema)
    assert UserSchema in object_mapper._mappers_bulk[UserDB]
    object_mapper.unregister(UserDB, UserSchema)
    assert object_mapper._mappers_bulk.get(UserDB) is None

async def test_unregister_scope(object_mapper: ObjectMapper):
    object_mapper.register_bulk(UserDB, UserSchema)
    assert UserSchema in object_mapper._mappers_bulk[UserDB]
    object_mapper.unregister(UserDB, UserSchema, scope='bulk')
    assert object_mapper._mappers_bulk.get(UserDB) is None

async def test_unregister_scope_no_match(object_mapper: ObjectMapper):
    object_mapper.register_bulk(UserDB, UserSchema)
    assert UserSchema in object_mapper._mappers_bulk[UserDB]
    with pytest.raises(KeyError):
        object_mapper.unregister(StudentDB, UserSchema, scope='bulk')


async def test_unregister_bad_to_class(object_mapper: ObjectMapper):
    object_mapper.register_bulk(UserDB, UserSchema)

    assert UserSchema in object_mapper._mappers_bulk[UserDB]
    with pytest.raises(KeyError):
        object_mapper.unregister(UserDB, BadSchema)


async def test_unregister_bad_from_class(object_mapper: ObjectMapper):
    object_mapper.register_bulk(UserDB, UserSchema, override_existing=True)

    assert UserSchema in object_mapper._mappers_bulk[UserDB]
    with pytest.raises(KeyError):
        object_mapper.unregister(BadDB, UserSchema)


async def test_unregister_not_removes_from_class_when_empty(object_mapper: ObjectMapper):
    object_mapper.register_bulk(UserDB, UserSchema)
    object_mapper.register_bulk(UserDB, StudSchema)
    assert UserDB in object_mapper._mappers_bulk
    assert UserSchema in object_mapper._mappers_bulk[UserDB]

    object_mapper.unregister(UserDB, UserSchema)

    assert UserDB in object_mapper._mappers_bulk

async def test_clear(object_mapper: ObjectMapper):
    object_mapper.register_bulk(
        UserDB,
        UserSchema,
        func=lambda x: [UserSchema(id=1, name="1")]
    )
    assert UserDB in object_mapper._mappers_bulk
    assert UserSchema in object_mapper._mappers_bulk[UserDB]
    object_mapper.clear(scope='bulk')
    assert object_mapper._mappers_bulk == {}


async def test_missing_from_attributes(object_mapper: ObjectMapper):
    with pytest.raises(ValueError):
        object_mapper.register_bulk(UserDB, BadSchema)


async def test_already_registered(object_mapper: ObjectMapper):
    object_mapper.register_bulk(
        UserDB,
        UserSchema,
        func=lambda x: [UserSchema(id=1, name="1")],
    )
    with pytest.raises(KeyError):
        object_mapper.register_bulk(UserDB, UserSchema)

async def test_map_bulk_unregistered(object_mapper: ObjectMapper):
    user = UserDB(id=1, name="user")
    with pytest.raises(KeyError):
        await object_mapper.map_bulk([user], UserSchema)


async def test_list_mappers_empty(object_mapper: ObjectMapper):
    object_mapper._mappers_bulk = {}
    result = object_mapper.list_mappers(scope='bulk')
    assert result == []

async def test_is_registered(object_mapper: ObjectMapper):
    assert object_mapper.is_registered(UserDB, UserSchema, scope='single') is False
    object_mapper.register(UserDB, UserSchema)
    assert object_mapper.is_registered(UserDB, UserSchema, scope='single') is True

async def test_list_mappers_with_data(object_mapper: ObjectMapper):
    class FromA: ...

    class FromB: ...

    class ToX: ...

    class ToY: ...

    object_mapper._mappers_bulk = {
        FromA: {ToX: _NoFunc},
        FromB: {ToY: _NoFunc},
    }

    assert sorted(
        object_mapper.list_mappers(scope='bulk'), key=lambda x: (x[0].__name__, x[1].__name__)
    ) == sorted(
        [(FromA, ToX), (FromB, ToY)], key=lambda x: (x[0].__name__, x[1].__name__)
    )


def test_wrong_types(object_mapper: ObjectMapper):
    class NotABase:
        pass

    with pytest.raises(TypeError):
        object_mapper.register_bulk(NotABase, UserSchema)

    with pytest.raises(TypeError):
        object_mapper.register_bulk(UserDB, NotABase)