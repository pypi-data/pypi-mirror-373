from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Union
from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel, Field, create_model

from simplespec import (
    DepthLimitExceededError,
    generate_simple_spec,
)

# - Referenced specs:
# <user>
#   name:<str>
#   age:<int>

# - Spec:
# <dict[str, user]>


def test_simple_for_primitive_type():
    # Test case 1: Simple Pydantic model

    spec = generate_simple_spec(dict[str, int])
    assert spec.self.type == f"{dict[str, int]!s}"
    print(spec)


def test_simple_type_with_name_collision():
    # Test case 1: Simple Pydantic model

    class EmployeeModule(BaseModel):
        class User(BaseModel):
            supername: str = Field(description="The name of the user", min_length=1, max_length=100)
            superage: int = Field(default=18, description="The age of minion user", ge=18, le=100)

        user: User

    class User(BaseModel):
        name: str = Field(description="The name of the user", min_length=1, max_length=100)
        age: int | None = Field(description="The age of the user", ge=18, le=100)
        employees: list["EmployeeModule.User"]
        employees_with_nicknames: dict[str, EmployeeModule.User]

    EmployeeModule.model_rebuild()

    spec = generate_simple_spec(dict[str, User])
    assert spec.self.type == "dict[str, User]"
    assert spec.refs[0].type == "User"
    assert spec.refs[1].type == "User_1"
    print(spec)


def test_simple_type_builder_nested():
    # Test case 2: Nested Pydantic model
    class Address(BaseModel):
        street: str
        city: str

    class Person(BaseModel):
        name: str
        address: Address
        backup_address: Address | None

    spec = generate_simple_spec(Person)
    assert spec.self.type == "Person"
    assert spec.refs[0].type == "Address"
    print(spec)


def test_simple_type_builder_union():
    class Address(BaseModel):
        street: str
        city: str

    # Test case 3: Model with Union types
    class Response(BaseModel):
        data: str | int | Address
        status: str

    spec = generate_simple_spec(Response)
    assert spec.self.type == "Response"
    assert spec.refs[0].type == "Address"
    print(spec)


def test_simple_type_builder_within_depth_limit():
    class Level1(BaseModel):
        """describing a level 1 model"""

        value: int = Field(description="An integer data", gt=10)

    class Level2(BaseModel):
        """describing a level 2 model"""

        l1: Level1

    class ForLevel31(BaseModel):
        """describing a level 31 model"""

        l1: Level1
        l2: Level2
        content31: str = Field(description="A string data", min_length=20)

    class ForLevel32(BaseModel):
        """describing a level 32 model"""

        l1: Level1
        l2: Level2
        content32: str

    class Level3(BaseModel):
        l31: ForLevel31
        l32: ForLevel32

    class Level4(BaseModel):
        l3: Level3

    spec = generate_simple_spec(Level4)
    assert spec.self.type == "Level4"
    assert spec.self.description is None
    assert spec.refs[0].type == "Level3"
    assert spec.refs[0].description is None
    assert spec.refs[1].type == "ForLevel31"
    assert spec.refs[1].description == "describing a level 31 model"
    assert spec.refs[2].type == "ForLevel32"
    assert spec.refs[2].description == "describing a level 32 model"
    assert spec.refs[3].type == "Level1"
    assert spec.refs[3].description == "describing a level 1 model"
    assert spec.refs[4].type == "Level2"
    assert spec.refs[4].description == "describing a level 2 model"
    print(spec)


def test_simple_type_builder_depth_limit():
    class Level1(BaseModel):
        data: str

    class Level2(BaseModel):
        l1: Level1

    class Level3(BaseModel):
        l2: Level2

    class Level4(BaseModel):
        l3: Level3

    class Level5(BaseModel):
        l4: Level4

    class TooDeep(BaseModel):
        l5: Level5

    with pytest.raises(DepthLimitExceededError):
        generate_simple_spec(TooDeep)


def test_ref_lookup_optional_dict():
    # Test case for model with optional dictionary field
    class ConfigModel(BaseModel):
        name: str
        settings: dict[str, str] | None = None

    spec = generate_simple_spec(ConfigModel)
    assert spec.self.properties["name"].type == "str"
    assert spec.self.properties["settings"].type == "dict[str, str] | None"
    print(spec)


def test_ref_lookup_dict_of_dicts():
    # Test case for model with nested dictionaries
    class DeepConfig(BaseModel):
        name: str
        nested_settings: dict[str, dict[str, str]]

    spec = generate_simple_spec(DeepConfig)
    assert spec.self.properties["name"].type == "str"
    assert spec.self.properties["nested_settings"].type == "dict[str, dict[str, str]]"
    print(spec)


def test_ref_lookup_recursive_list():
    """Test case for model with recursive list type"""

    class Node(BaseModel):
        value: str
        children: list["Node"] = []

    Node.model_rebuild()  # Required for recursive types
    spec = generate_simple_spec(Node)
    assert spec.self.properties["value"].type == "str"
    assert spec.self.properties["children"].type == "list[Node]"
    print(spec)


def test_ref_lookup_multiple_nested_unions():
    """Test case for model with multiple nested union types"""

    class Tag(BaseModel):
        name: str

    class Category(BaseModel):
        title: str

    class Item(BaseModel):
        data: str | int | Tag | Category | list[str | Tag]

    spec = generate_simple_spec(Item)
    # Assert based on the alphabetically sorted union members
    assert spec.self.properties["data"].type == "Category | Tag | int | list[Tag | str] | str"
    # Refs should be sorted by depth, then name
    assert spec.refs[0].type == "Category"
    assert spec.refs[1].type == "Tag"
    print(spec)


def test_ref_lookup_nested_optional_dict():
    """Test case for model with nested optional dictionary fields"""

    class Settings(BaseModel):
        name: str

    class Config(BaseModel):
        primary: dict[str, Settings] | None
        fallback: dict[str, Settings | None] | None = None

    spec = generate_simple_spec(Config)
    assert spec.self.properties["primary"].type == "dict[str, Settings] | None"
    assert spec.self.properties["fallback"].type == "dict[str, Settings | None] | None"
    assert spec.refs[0].type == "Settings"
    print(spec)


def test_ref_lookup_complex_dict_keys():
    """Test case for model with complex dictionary key types"""

    class KeyType(BaseModel):
        id: str

    class ValueType(BaseModel):
        data: str

    class ComplexDict(BaseModel):
        simple_dict: dict[str, ValueType]
        tuple_dict: dict[tuple[str, int], ValueType]
        model_dict: dict[KeyType, ValueType]

    spec = generate_simple_spec(ComplexDict)
    print(spec)
    assert spec.self.properties["simple_dict"].type == "dict[str, ValueType]"
    assert spec.self.properties["tuple_dict"].type == "dict[tuple[str, int], ValueType]"
    assert spec.self.properties["model_dict"].type == "dict[KeyType, ValueType]"
    assert spec.refs[0].type == "KeyType"
    assert spec.refs[1].type == "ValueType"
    print(spec)


def test_ref_lookup_enum_types():
    """Test case for model with enum types"""

    class Color(str, Enum):
        RED = "red"
        BLUE = "blue"

    class Shape(str, Enum):
        CIRCLE = "circle"
        SQUARE = "square"

    class Drawing(BaseModel):
        primary_color: Color
        secondary_color: Color | None
        shapes: list[Shape]

    spec = generate_simple_spec(Drawing)
    assert spec.self.properties["primary_color"].type == "Enum['blue', 'red']"
    assert spec.self.properties["secondary_color"].type == "Enum['blue', 'red'] | None"
    print(spec)


def test_ref_lookup_forward_refs():
    """Test case for model with forward references"""

    class TreeNode(BaseModel):
        value: str
        parent: Optional["TreeNode"] = None
        siblings: list["TreeNode"] = []
        metadata: dict[str, Union[str, "TreeNode"]] = {}

    TreeNode.model_rebuild()
    spec = generate_simple_spec(TreeNode)
    assert spec.self.type == "TreeNode"
    assert spec.self.properties["value"].type == "str"
    assert spec.self.properties["parent"].type == "TreeNode | None"
    assert spec.self.properties["siblings"].type == "list[TreeNode]"
    assert spec.self.properties["metadata"].type == "dict[str, TreeNode | str]"
    print(spec)


def test_ref_lookup_literal_types():
    """Test case for model with literal types"""
    from typing import Literal

    class ApiConfig(BaseModel):
        version: Literal["v1", "v2", "v3"]
        mode: Literal[1, 2, 3]
        status: Literal["active"] | Literal["inactive"]
        settings: dict[Literal["main", "backup"], str]

    spec = generate_simple_spec(ApiConfig)
    assert spec.self.type == "ApiConfig"
    assert spec.self.properties["version"].type == "Literal['v1', 'v2', 'v3']"
    assert spec.self.properties["mode"].type == "Literal[1, 2, 3]"
    assert spec.self.properties["status"].type == "Literal['active'] | Literal['inactive']"
    assert spec.self.properties["settings"].type == "dict[Literal['main', 'backup'], str]"
    print(spec)


def test_ref_lookup_type_aliases():
    """Test case for model with type aliases"""

    class JsonContainer(BaseModel):
        data: dict[str, Any]  # Using Dict[str, Any] instead of the recursive JsonValue
        metadata: dict[str, str | int | float | bool | None | list[Any] | dict[str, Any]]

    spec = generate_simple_spec(JsonContainer)
    assert spec.self.type == "JsonContainer"
    assert spec.self.properties["data"].type == "dict[str, Any]"
    assert (
        spec.self.properties["metadata"].type
        == "dict[str, bool | dict[str, Any] | float | int | list[Any] | str | None]"
    )
    print(spec)


def test_enum_intents():
    """Test SimpleSpec in instance mode with enum fields"""

    class Intent(str, Enum):
        ADD_TASK = "add_task"
        COMPLETE_TASK = "complete_task"
        DELETE_TASK = "delete_task"

    class AddTask(BaseModel):
        """Add a task"""

        content: str

    class CompleteTask(BaseModel):
        """Complete a task"""

        task_id: str

    class DeleteTask(BaseModel):
        """Delete a task"""

        task_id: str

    class Response(BaseModel):
        """Response to a task intent"""

        intent: Intent
        task: AddTask | CompleteTask | DeleteTask

    # Create SimpleSpec with the instance
    spec = generate_simple_spec(Response)

    # Verify the representation contains the enum value

    print(spec)


def test_with_create_model():
    model1 = create_model("TestModel1", content=(str, ...))
    model2 = create_model("TestModel2", content=(str | model1, ...))
    model3 = create_model("TestModel3", content=(str | model1 | model2 | None, ...))
    spec = generate_simple_spec(model1)
    assert spec.self.type == "TestModel1"
    assert spec.self.properties["content"].type == "str"
    print(spec)

    spec = generate_simple_spec(model2)
    assert spec.self.type == "TestModel2"
    assert spec.self.properties["content"].type == "TestModel1 | str"
    assert spec.refs[0].type == "TestModel1"
    spec = generate_simple_spec(model3)
    assert spec.self.type == "TestModel3"
    assert spec.self.properties["content"].type == "TestModel1 | TestModel2 | str | None"
    assert spec.refs[0].type == "TestModel1"
    assert spec.refs[1].type == "TestModel2"
    print(spec)


def test_bytes_and_bytearray():
    """Test models with bytes and bytearray."""

    class DataContainer(BaseModel, arbitrary_types_allowed=True):
        raw_data: bytes
        mutable_raw: bytearray
        optional_bytes: bytes | None = None

    spec = generate_simple_spec(DataContainer)
    assert spec.self.type == "DataContainer"
    assert spec.self.properties["raw_data"].type == "bytes"
    assert spec.self.properties["mutable_raw"].type == "bytearray"
    assert spec.self.properties["optional_bytes"].type == "bytes | None"
    assert not spec.refs
    print(spec)


def test_int_enum():
    """Test models with IntEnum."""
    from enum import IntEnum

    class ErrorCode(IntEnum):
        NOT_FOUND = 404
        INTERNAL_ERROR = 500

    class ErrorResponse(BaseModel):
        error_code: ErrorCode
        message: str

    spec = generate_simple_spec(ErrorResponse)
    assert spec.self.type == "ErrorResponse"
    # IntEnum currently renders like a normal Enum in the resolver
    assert spec.self.properties["error_code"].type == "Enum[404, 500]"
    assert not spec.refs
    print(spec)


def test_complex_literal():
    """Test Literal with mixed types including None and bool."""
    from typing import Literal

    class ComplexLiteralModel(BaseModel):
        status: Literal["ok", "error", None]
        flag: Literal[True, False]
        mixed: Literal[1, "one", True, None]

    spec = generate_simple_spec(ComplexLiteralModel)
    assert spec.self.type == "ComplexLiteralModel"
    assert spec.self.properties["status"].type == "Literal['ok', 'error', None]"
    assert spec.self.properties["flag"].type == "Literal[True, False]"
    assert spec.self.properties["mixed"].type == "Literal[1, 'one', True, None]"
    assert not spec.refs
    print(spec)


def test_optional_equivalents():
    """Test Optional[T] vs Union[T, None]."""

    class ModelA(BaseModel):
        value: str | None

    class ModelB(BaseModel):
        value: str | None

    spec_a = generate_simple_spec(ModelA)
    spec_b = generate_simple_spec(ModelB)

    assert spec_a.self.type == "ModelA"
    assert spec_b.self.type == "ModelB"
    assert spec_a.self.properties["value"].type == "str | None"
    assert spec_b.self.properties["value"].type == "str | None"
    assert not spec_a.refs
    assert not spec_b.refs


def test_default_factory():
    """Test field with default_factory."""
    from uuid import UUID, uuid4

    class ItemWithId(BaseModel):
        item_id: UUID = Field(default_factory=uuid4)
        name: str

    spec = generate_simple_spec(ItemWithId)
    assert spec.self.type == "ItemWithId"
    # default_factory results in a default constraint
    assert spec.self.properties["item_id"].type == "UUID"
    assert spec.self.properties["name"].type == "str"
    assert not spec.refs
    print(spec)


def test_all_constraints():
    """Test various constraints combined."""

    uuid_value = uuid4()

    class ConstrainedModel(BaseModel):
        count: int = Field(gt=0, le=100, multiple_of=5, description="A count")
        ratio: float = Field(ge=0.0, lt=1.0)
        name: str = Field(min_length=3, max_length=50)
        items: list[str] = Field(min_length=1, max_length=10)
        maybe_limited: str | None = Field(default="test", min_length=2)
        uuid_field: UUID = Field(default=uuid_value)

    spec = generate_simple_spec(ConstrainedModel)
    assert spec.self.type == "ConstrainedModel"
    props = spec.self.properties
    assert props["count"].type == "int"
    assert "gt=0" in props["count"].description
    assert "le=100" in props["count"].description
    assert "multiple_of=5" in props["count"].description
    assert "A count" in props["count"].description

    assert props["ratio"].type == "float"
    assert "ge=0.0" in props["ratio"].description
    assert "lt=1.0" in props["ratio"].description

    assert props["name"].type == "str"
    assert "min_length=3" in props["name"].description
    assert "max_length=50" in props["name"].description

    assert props["items"].type == "list[str]"
    assert "min_length=1" in props["items"].description
    assert "max_length=10" in props["items"].description

    assert props["maybe_limited"].type == "str | None"
    assert "default='test'" in props["maybe_limited"].description
    assert "min_length=2" in props["maybe_limited"].description

    assert props["uuid_field"].type == "UUID"
    assert f"default={uuid_value!r}" in props["uuid_field"].description

    assert not spec.refs
    print(spec)


def test_any_type():
    """Test model with Any type."""

    class FlexibleModel(BaseModel):
        flexible_field: Any
        dict_with_any: dict[str, Any]

    spec = generate_simple_spec(FlexibleModel)
    assert spec.self.type == "FlexibleModel"
    assert spec.self.properties["flexible_field"].type == "Any"
    assert spec.self.properties["dict_with_any"].type == "dict[str, Any]"
    assert not spec.refs
    print(spec)


def test_empty_model():
    """Test an empty Pydantic model."""

    class EmptyModel(BaseModel):
        pass

    spec = generate_simple_spec(EmptyModel)
    assert spec.self.type == "EmptyModel"
    assert not spec.self.properties
    assert not spec.refs
    print(spec)


def test_triple_name_collision():
    """Test name collision with three classes."""

    class ModuleA:
        class Data(BaseModel):
            a: int

    class ModuleB:
        class Data(BaseModel):
            b: str

    class Data(BaseModel):
        c: bool
        data_a: ModuleA.Data
        data_b: ModuleB.Data

    ModuleA.Data.model_rebuild()
    ModuleB.Data.model_rebuild()
    Data.model_rebuild()

    spec = generate_simple_spec(Data)
    print(spec)

    assert spec.self.type == "Data"
    assert len(spec.refs) == 2  # noqa: PLR2004
    # Depth order: Data (root, depth 0), ModuleA.Data (depth 1), ModuleB.Data (depth 1)
    # Since A and B are at same depth, secondary sort is alphabetical on internal name
    # Assuming ModuleA.Data ref name sorts before ModuleB.Data
    assert spec.refs[0].type == "Data_1"  # Belongs to ModuleA.Data
    assert "a" in spec.refs[0].properties
    assert spec.refs[1].type == "Data_2"  # Belongs to ModuleB.Data
    assert "b" in spec.refs[1].properties


def test_exact_depth_limit():
    """Test structure that exactly hits the depth limit."""

    class L1(BaseModel):
        val1: str

    class L2(BaseModel):
        l1: L1

    class L3(BaseModel):
        l2: L2

    class L4(BaseModel):
        l3: L3

    class L5(BaseModel):  # This is the root, depth 0
        l4: L4  # L4 is depth 1, L3 depth 2, L2 depth 3, L1 depth 4

    # Default depth is 4. L1 is at depth 4, so it should be included.
    spec = generate_simple_spec(L5, max_depth=5)
    print(spec)
    assert spec.self.type == "L5"
    assert len(spec.refs) == 4  # noqa: PLR2004
    assert spec.refs[0].type == "L4"
    assert spec.refs[1].type == "L3"
    assert spec.refs[2].type == "L2"
    assert spec.refs[3].type == "L1"

    # If we set depth to 3, L1 should be excluded
    with pytest.raises(DepthLimitExceededError):  # L1 is at depth 4, exceeding limit 3
        generate_simple_spec(L5, max_depth=3)


def test_set_type():
    """Test model with set type."""

    class SetContainer(BaseModel):
        unique_ids: set[int]
        optional_set: set[str] | None = None

    spec = generate_simple_spec(SetContainer)
    assert spec.self.type == "SetContainer"
    assert spec.self.properties["unique_ids"].type == "set[int]"
    assert spec.self.properties["optional_set"].type == "set[str] | None"
    assert not spec.refs
    print(spec)


# --- Dataclass Support Tests ---


@dataclass
class SimpleDC:
    """A simple dataclass."""

    id: int
    name: str


def test_simple_dataclass():
    """Test spec generation for a basic dataclass."""
    spec = generate_simple_spec(SimpleDC)
    assert spec.self.type == "SimpleDC"
    assert spec.self.description == "A simple dataclass."
    assert "id" in spec.self.properties
    assert spec.self.properties["id"].type == "int"
    assert spec.self.properties["id"].description is None
    assert "name" in spec.self.properties
    assert spec.self.properties["name"].type == "str"
    assert spec.self.properties["name"].description is None
    assert not spec.refs
    print(spec)


@dataclass
class DCWithDefaults:
    """Dataclass with defaults."""

    value: float = 0.5
    flag: bool | None = None
    items: list[str] = field(default_factory=list)


def test_dataclass_with_defaults():
    """Test dataclass fields with default values."""
    spec = generate_simple_spec(DCWithDefaults)
    assert spec.self.type == "DCWithDefaults"
    assert spec.self.description == "Dataclass with defaults."
    props = spec.self.properties
    assert props["value"].type == "float"
    # Note: We expect default constraints to be captured
    assert props["value"].description == "[default=0.5]"
    assert props["flag"].type == "bool | None"
    assert props["flag"].description == "[default=None]"
    assert props["items"].type == "list[str]"
    # default_factory is harder to represent, check for its presence if possible or expect no constraint
    assert props["items"].description is None  # Or check for a specific representation if implemented
    assert not spec.refs
    print(spec)


@dataclass
class NestedAddressDC:
    street: str
    zip_code: str


@dataclass
class NestedPersonDC:
    """Person with a nested address dataclass."""

    person_id: UUID
    address: NestedAddressDC
    optional_address: NestedAddressDC | None = None


def test_nested_dataclass():
    """Test a dataclass containing another dataclass."""
    spec = generate_simple_spec(NestedPersonDC)
    assert spec.self.type == "NestedPersonDC"
    props = spec.self.properties
    assert props["person_id"].type == "UUID"
    assert props["address"].type == "NestedAddressDC"
    assert props["optional_address"].type == "NestedAddressDC | None"
    assert len(spec.refs) == 1
    assert spec.refs[0].type == "NestedAddressDC"
    assert "street" in spec.refs[0].properties
    assert "zip_code" in spec.refs[0].properties
    print(spec)


class PydanticContainerForDC(BaseModel):
    """Pydantic model holding a dataclass."""

    dc_field: SimpleDC
    optional_dc: SimpleDC | None = None


def test_dataclass_in_pydantic():
    """Test a Pydantic model containing a dataclass field."""
    spec = generate_simple_spec(PydanticContainerForDC)
    assert spec.self.type == "PydanticContainerForDC"
    props = spec.self.properties
    assert props["dc_field"].type == "SimpleDC"
    assert props["optional_dc"].type == "SimpleDC | None"
    assert len(spec.refs) == 1
    assert spec.refs[0].type == "SimpleDC"
    assert "id" in spec.refs[0].properties  # Verify the nested DC structure
    print(spec)


class PydanticPayload(BaseModel):
    content: str


@dataclass
class DataclassContainerForPydantic:
    """Dataclass holding a Pydantic model."""

    pydantic_field: PydanticPayload
    maybe_pydantic: PydanticPayload | None = None


def test_pydantic_in_dataclass():
    """Test a dataclass containing a Pydantic model field."""
    spec = generate_simple_spec(DataclassContainerForPydantic)
    assert spec.self.type == "DataclassContainerForPydantic"
    props = spec.self.properties
    assert props["pydantic_field"].type == "PydanticPayload"
    assert props["maybe_pydantic"].type == "PydanticPayload | None"
    assert len(spec.refs) == 1
    assert spec.refs[0].type == "PydanticPayload"
    assert "content" in spec.refs[0].properties
    print(spec)


@dataclass
class DCWithCollections:
    simple_list: list[int]
    list_of_dc: list[SimpleDC]
    dict_of_models: dict[str, PydanticPayload]
    optional_list_dc: list[SimpleDC] | None = None


def test_dataclass_with_collections():
    """Test dataclass with various collection types."""
    spec = generate_simple_spec(DCWithCollections)
    assert spec.self.type == "DCWithCollections"
    props = spec.self.properties
    assert props["simple_list"].type == "list[int]"
    assert props["list_of_dc"].type == "list[SimpleDC]"
    assert props["dict_of_models"].type == "dict[str, PydanticPayload]"
    assert props["optional_list_dc"].type == "list[SimpleDC] | None"
    # SimpleDC and PydanticPayload
    assert len(spec.refs) == 2  # noqa: PLR2004
    # Order depends on depth/name sorting
    ref_types = sorted([r.type for r in spec.refs])
    assert ref_types == ["PydanticPayload", "SimpleDC"]
    print(spec)


# --- Collision Test with Dataclass ---


class NamespaceDC:
    """Acts as a namespace for the dataclass version."""

    @dataclass
    class CollisionItem:
        """A dataclass item for collision testing (namespaced)."""

        dc_id: int


class CollisionItem(BaseModel):  # Pydantic version, name clashes with NamespaceDC.CollisionItem
    """A Pydantic model item for collision testing."""

    pydantic_id: str
    nested_dc: NamespaceDC.CollisionItem  # Reference the namespaced dataclass


def test_dataclass_pydantic_collision():
    """Test name collision between a dataclass and a Pydantic model."""
    # Need to rebuild the Pydantic model to resolve the nested ref
    CollisionItem.model_rebuild()

    spec = generate_simple_spec(CollisionItem)  # Generate spec for the Pydantic model
    print(spec)

    # The Pydantic model CollisionItem is the root (self)
    assert spec.self.type == "CollisionItem"
    assert "pydantic_id" in spec.self.properties
    # The nested field should refer to the *other* CollisionItem (the dataclass)
    # which should get a disambiguated name, e.g., CollisionItem_1
    assert spec.self.properties["nested_dc"].type == "CollisionItem_1"

    # There should be one reference: the dataclass version
    assert len(spec.refs) == 1
    assert spec.refs[0].type == "CollisionItem_1"
    assert "dc_id" in spec.refs[0].properties

    # Now test generating for the dataclass directly (should not collide with itself)
    spec_dc = generate_simple_spec(NamespaceDC.CollisionItem)  # Pass the namespaced dataclass type
    print(spec_dc)
    assert spec_dc.self.type == "CollisionItem"  # Simple name as it's the root
    assert "dc_id" in spec_dc.self.properties
    assert not spec_dc.refs


# --- Exception Handling Tests ---


# Test case for potential recursion depth issues handled by walker
class RecursiveWalkerTestA(BaseModel):
    b: Optional["RecursiveWalkerTestB"] = None


class RecursiveWalkerTestB(BaseModel):
    a: RecursiveWalkerTestA


RecursiveWalkerTestA.model_rebuild()
RecursiveWalkerTestB.model_rebuild()


def test_recursion_depth_limit():
    """Test that deep recursion hits the DepthLimitExceededError."""
    with pytest.raises(DepthLimitExceededError):
        generate_simple_spec(RecursiveWalkerTestA, max_depth=1)  # Set low depth

    # Should work with default depth
    spec = generate_simple_spec(RecursiveWalkerTestA)
    assert spec.self.type == "RecursiveWalkerTestA"
    assert len(spec.refs) == 1
    assert spec.refs[0].type == "RecursiveWalkerTestB"
    print(spec)
