#sqlalchemy-pydantic-mapper

`sqlalchemy-pydantic-mapper` simplifies converting SQLAlchemy instances (subclasses of `sqlalchemy.orm.DeclarativeBase`) into Pydantic models (`pydantic.BaseModel`).

#### It supports:

* registering custom synchronous and asynchronous mappers;
* registration via decorator or by passing `func=` directly;
* automatic mapping via Pydantic if the model has `model_config = ConfigDict(from_attributes=True)`;
* `map(...)` — an async method returning the target Pydantic model instance (must `await` it);
* `map_each(...)` — an async method returning the sequence of target Pydantic model instances, calls target func for every ORM model (must `await` it);
* `map_bulk(...)` — an async method returning a list of mapped Pydantic model instances from a sequence of SQLAlchemy objects(must `await` it).

---
## Usage Examples (Full Code Snippets)

1. Simple registration via `func=` and checking `_mappers`:

```python
from sqlalchemy_pydantic_mapper import ObjectMapper


def mapper(db: UserDB) -> UserSchema:
    return UserSchema(id=db.id, name=db.name)


ObjectMapper.register(UserDB, UserSchema, func=mapper)
assert ObjectMapper._mappers_single[UserDB][UserSchema] is mapper
```

2. Registration via decorator:

```python
@ObjectMapper.register(UserDB, UserSchema)
def mapper2(db: UserDB) -> UserSchema:
    return UserSchema(id=db.id, name=db.name)
```

3. Async mapper (registration + usage):

```python
@ObjectMapper.register(UserDB, UserSchema)
async def async_mapper(db: UserDB) -> UserSchema:
    # e.g., async call or await something
    return UserSchema(id=db.id, name=db.name.upper())

import asyncio

async def main():
    user = UserDB()
    user.id = 1
    user.name = "alice"
    res = await ObjectMapper.map(user, UserSchema)
    print(res)  # UserSchema(id=1, name='ALICE')

asyncio.run(main())
```

4. Auto-mapping via Pydantic (`from_attributes=True`):

```python
class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
```

If no custom mapper is registered for the `from_class -> to_class` pair, `ObjectMapper.map(instance, UserSchema)` automatically calls:

```python
UserSchema.model_validate(instance, from_attributes=True)
```

5. Example in a test (synthetic):

```python
async def test_auto_mapping():
    stud = StudentDB()
    stud.id = 2
    stud.name = "Bob"

    result = await ObjectMapper.map(stud, UserSchema)
    assert result.id == 2
    assert result.name == "Bob"
```

6. Example for manual mapping (different names / logic):

```python
def stud_to_studschema(db: StudentDB) -> StudSchema:
    return StudSchema(id=db.id, name=db.name)

ObjectMapper.register(StudentDB, StudSchema, func=stud_to_studschema)
```
---


7. Mapping multiple objects with `map_many`

```python
users = [UserDB(id=1, name="Alice"), UserDB(id=2, name="Bob")]


# Synchronous mapper
def mapper(db: UserDB) -> UserSchema:
    return UserSchema(id=db.id, name=db.name)


ObjectMapper.register(UserDB, UserSchema, func=mapper)

import asyncio


async def main():
    results = await ObjectMapper.map_each(users, UserSchema)
    print(results)
    # [UserSchema(id=1, name='Alice'), UserSchema(id=2, name='Bob')]


asyncio.run(main())
```

---

8. Passing additional arguments to a mapper function

```python
def mapper_with_prefix(db: UserDB, prefix: str) -> UserSchema:
    return UserSchema(id=db.id, name=f"{prefix}{db.name}")

# Register mapper with a closure to pass extra arguments
ObjectMapper.register(UserDB, UserSchema, func=lambda db: mapper_with_prefix(db, prefix="Mr. "))

user = UserDB(id=1, name="Alice")
import asyncio

async def main():
    result = await ObjectMapper.map(user, UserSchema)
    print(result)  # UserSchema(id=1, name='Mr. Alice')

asyncio.run(main())
```

---

9. Re-registering a mapper (overwriting)

```python
# Original mapper
ObjectMapper.register(UserDB, UserSchema, func=lambda db: UserSchema(id=db.id, name=db.name))

# Re-register with a new logic
ObjectMapper.register(UserDB, UserSchema, 
                      func=lambda db: UserSchema(id=db.id, name=db.name.upper()),
                      override_existing=True)

user = UserDB(id=2, name="Bob")

import asyncio
async def main():
    result = await ObjectMapper.map(user, UserSchema)
    print(result)  # UserSchema(id=2, name='BOB')

asyncio.run(main())
```

---

10. Async mapper with `map_each`

```python
async def async_mapper(db: UserDB) -> UserSchema:
    import asyncio
    await asyncio.sleep(0.01)
    return UserSchema(id=db.id, name=db.name.upper())


ObjectMapper.register(UserDB, UserSchema, func=async_mapper)

users = [UserDB(id=1, name="Alice"), UserDB(id=2, name="Bob")]


async def main():
    results = await ObjectMapper.map_each(users, UserSchema)
    print(results)
    # [UserSchema(id=1, name='ALICE'), UserSchema(id=2, name='BOB')]


asyncio.run(main())
```

11. Async mapper with `map_bulk` - True bulk operation under all the sequence at once

```python
async def async_mapper(dbs: Sequence[UserDB]) -> Sequence[UserSchema]:
    import asyncio
    await asyncio.sleep(0.01)
    return [UserSchema(id=db.id, name=db.name.upper()) for db in dbs]


ObjectMapper.register_bulk(UserDB, UserSchema, func=async_mapper)

users = [UserDB(id=1, name="Alice"), UserDB(id=2, name="Bob")]


async def main():
    results = await ObjectMapper.map_bulk(users, UserSchema)
    print(results)
    # [UserSchema(id=1, name='ALICE'), UserSchema(id=2, name='BOB')]


asyncio.run(main())
```


## Errors and Behavior on Incorrect Usage

* `TypeError` if `from_` does not inherit `DeclarativeBase`:

```python
class NotABase: pass
ObjectMapper.register(NotABase, UserSchema)  # -> TypeError
```

* `TypeError` if `to_` does not inherit `BaseModel`:

```python
class NotABaseModel: pass
ObjectMapper.register(UserDB, NotABaseModel)  # -> TypeError
```

* `ValueError` if `func` is missing and `to_` does not have `model_config = ConfigDict(from_attributes=True)`:

```python
class BadSchema(BaseModel):
    id: int
    name: str

ObjectMapper.register(UserDB, BadSchema)  # -> ValueError
```
---
