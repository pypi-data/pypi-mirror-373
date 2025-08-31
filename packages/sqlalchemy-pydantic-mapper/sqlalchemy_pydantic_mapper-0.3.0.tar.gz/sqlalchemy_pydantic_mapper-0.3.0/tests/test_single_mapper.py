import pytest

from src.sqlalchemy_pydantic_mapper import ObjectMapper
from src.sqlalchemy_pydantic_mapper.ObjectMapper import _NoFunc
from tests.helpers import UserDB, UserSchema, StudentDB, StudSchema, BadDB, BadSchema

def test_register_direct(object_mapper: ObjectMapper):
    def mapper(db: UserDB) -> UserSchema:
        return UserSchema(id=db.id, name=db.name)

    object_mapper.register(UserDB, UserSchema, func=mapper, override_existing=True)
    assert object_mapper._mappers_single[UserDB][UserSchema] is mapper


def test_register_decorator(object_mapper: ObjectMapper):
    @object_mapper.register(UserDB, UserSchema)
    def mapper2(db: UserDB) -> UserSchema:
        return UserSchema(id=db.id, name=db.name)

    assert object_mapper._mappers_single[UserDB][UserSchema] is mapper2


async def test_auto_mapping(object_mapper: ObjectMapper):
    object_mapper.register(StudentDB, UserSchema)
    stud = StudentDB()
    stud.id = 2
    stud.name = "Bob"

    result = await object_mapper.map(stud, UserSchema)
    assert result.id == 2
    assert result.name == "Bob"


async def test_manual_mapping(object_mapper: ObjectMapper):
    def stud_to_user(db: UserDB) -> StudSchema:
        return StudSchema(id=db.id, name=db.name.upper())

    stud = StudentDB()
    stud.id = 2
    stud.name = "Bob"
    ObjectMapper.register(
        StudentDB, StudSchema, func=stud_to_user
    )
    result = await object_mapper.map(stud, StudSchema)
    assert result.id == 2
    assert result.name == "BOB"

async def test_manual_mapping_async(object_mapper: ObjectMapper):
    async def stud_to_user(db: UserDB) -> StudSchema:
        return StudSchema(id=db.id, name=db.name.upper())

    stud = StudentDB()
    stud.id = 2
    stud.name = "Bob"
    ObjectMapper.register(
        StudentDB, StudSchema, func=stud_to_user
    )
    result = await object_mapper.map(stud, StudSchema)
    assert result.id == 2
    assert result.name == "BOB"

async def test_map_each_fallback(object_mapper: ObjectMapper):
    object_mapper.register(UserDB, UserSchema)
    users = [UserDB(id=1, name="Alice"), UserDB(id=2, name="Bob")]
    results = await ObjectMapper.map_each(users, UserSchema)
    assert len(results) == 2
    assert results[0].name == "Alice"
    assert results[1].name == "Bob"


async def test_map_each_func(object_mapper: ObjectMapper):
    def mapper(db: UserDB) -> UserSchema:
        return UserSchema(id=db.id, name=db.name.upper())


    object_mapper.register(UserDB, UserSchema, func=mapper)

    users = [UserDB(id=1, name="Alice"), UserDB(id=2, name="Bob")]
    results = await object_mapper.map_each(users, UserSchema)
    assert len(results) == 2
    assert results[0].name == "ALICE"
    assert results[1].name == "BOB"


async def test_map_each_with_async_mapper(object_mapper: ObjectMapper):
    async def mapper(db: UserDB) -> UserSchema:
        return UserSchema(id=db.id, name=db.name.upper())

    object_mapper.register(UserDB, UserSchema, func=mapper)

    users = [UserDB(id=1, name="alice"), UserDB(id=2, name="bob")]
    results = await object_mapper.map_each(users, UserSchema)
    assert len(results) == 2
    assert results[0].name == "ALICE"
    assert results[1].name == "BOB"


async def test_map_with_func_kwargs(object_mapper: ObjectMapper):
    async def mapper_with_session(user: UserDB, session: str) -> UserSchema:
        return UserSchema(id=user.id, name=f"{user.name}-{session}")

    object_mapper.register(UserDB, UserSchema, func=mapper_with_session)

    users = [UserDB(id=1, name="Alice"), UserDB(id=2, name="Bob")]
    results = await object_mapper.map_each(users, UserSchema, session="X")
    assert results[0].name == "Alice-X"
    assert results[1].name == "Bob-X"


async def test_map_empty_sequence(object_mapper: ObjectMapper):
    object_mapper.register(UserDB, UserSchema)
    results = await object_mapper.map_each([], UserSchema)
    assert results == []


async def test_unregister(object_mapper: ObjectMapper):
    object_mapper.register(UserDB, UserSchema)
    assert UserSchema in object_mapper._mappers_single[UserDB]
    object_mapper.unregister(UserDB, UserSchema)
    assert object_mapper._mappers_single.get(UserDB) is None

async def test_unregister_scope(object_mapper: ObjectMapper):
    object_mapper.register(UserDB, UserSchema)
    assert UserSchema in object_mapper._mappers_single[UserDB]
    object_mapper.unregister(UserDB, UserSchema, scope='single')
    assert object_mapper._mappers_single.get(UserDB) is None

async def test_unregister_scope_no_match(object_mapper: ObjectMapper):
    object_mapper.register(UserDB, UserSchema)
    assert UserSchema in object_mapper._mappers_single[UserDB]
    with pytest.raises(KeyError):
        object_mapper.unregister(StudentDB, UserSchema, scope='single')

async def test_unregister_bad_to_class(object_mapper: ObjectMapper):
    object_mapper.register(UserDB, UserSchema)

    assert UserSchema in object_mapper._mappers_single[UserDB]

    with pytest.raises(KeyError):
        object_mapper.unregister(UserDB, BadSchema)


async def test_unregister_bad_from_class(object_mapper: ObjectMapper):
    object_mapper.register(UserDB, UserSchema, override_existing=True)

    assert UserSchema in object_mapper._mappers_single[UserDB]

    with pytest.raises(KeyError):
        object_mapper.unregister(BadDB, UserSchema)


async def test_unregister_not_removes_from_class_when_empty(object_mapper: ObjectMapper):
    object_mapper.register(UserDB, UserSchema)
    object_mapper.register(UserDB, StudSchema)

    assert UserDB in object_mapper._mappers_single
    assert UserSchema in object_mapper._mappers_single[UserDB]

    object_mapper.unregister(UserDB, UserSchema)

    assert UserDB in object_mapper._mappers_single


async def test_clear(object_mapper: ObjectMapper):
    object_mapper.clear()

    object_mapper.register(
        UserDB,
        UserSchema,
        func=lambda x: UserSchema(id=1, name="1")
    )

    assert UserDB in object_mapper._mappers_single
    assert UserSchema in object_mapper._mappers_single[UserDB]

    object_mapper.clear(scope='single')

    assert object_mapper._mappers_single == {}


async def test_bad_from_attribute(object_mapper: ObjectMapper):
    with pytest.raises(ValueError):
        object_mapper.register(UserDB, BadSchema)


async def test_already_registered(object_mapper: ObjectMapper):
    object_mapper.register(
        UserDB,
        UserSchema,
        func=lambda x: UserSchema(id=1, name="1"),
    )
    with pytest.raises(KeyError):
        object_mapper.register(UserDB, UserSchema)


async def test_map_unregistered(object_mapper: ObjectMapper):
    user = UserDB(id=1, name="user")
    with pytest.raises(KeyError):
        await object_mapper.map(user, UserSchema)

async def test_map_each_unregistered(object_mapper: ObjectMapper):
    user = UserDB(id=1, name="user")
    with pytest.raises(KeyError):
        await object_mapper.map_each([user], UserSchema)

async def test_list_mapper_empty(object_mapper: ObjectMapper):
    object_mapper._mappers_single = {}
    result = object_mapper.list_mappers(scope='single')
    assert result == []


async def test_list_mapper_with_data(object_mapper: ObjectMapper):
    class FromA: ...

    class FromB: ...

    class ToX: ...

    class ToY: ...

    object_mapper._mappers_single = {
        FromA: {ToX: _NoFunc},
        FromB: {ToY: _NoFunc},
    }

    assert sorted(
        object_mapper.list_mappers(scope='single'), key=lambda x: (x[0].__name__, x[1].__name__)
    ) == sorted(
        [(FromA, ToX), (FromB, ToY)], key=lambda x: (x[0].__name__, x[1].__name__)
    )

async def test_is_registered(object_mapper: ObjectMapper):
    assert object_mapper.is_registered(UserDB, UserSchema, scope='bulk') is False
    object_mapper.register_bulk(UserDB, UserSchema)
    assert object_mapper.is_registered(UserDB, UserSchema, scope='bulk') is True

async def test_wrong_types(object_mapper: ObjectMapper):
    class NotABase:
        pass

    with pytest.raises(TypeError):
        object_mapper.register(NotABase, UserSchema)

    with pytest.raises(TypeError):
        object_mapper.register(UserDB, NotABase)