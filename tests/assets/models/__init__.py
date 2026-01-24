"""Test Pydantic models for sphinxcontrib-pydantic tests."""

from tests.assets.models.basic import (
    DocumentedModel,
    EmptyModel,
    ModelWithDocstrings,
    SimpleModel,
)
from tests.assets.models.computed import ComputedFieldModel, ComputedWithDescription
from tests.assets.models.fields import (
    FieldWithAlias,
    FieldWithConstraints,
    FieldWithDefaults,
    FieldWithMetadata,
)
from tests.assets.models.forward_refs import (
    NodeA,
    NodeB,
    SelfReferencing,
    StringAnnotationModel,
    TreeNode,
)
from tests.assets.models.generics import (
    BoundedGeneric,
    ConcreteContainer,
    ConcreteWithValidator,
    GenericContainer,
    GenericMapping,
    GenericWithValidator,
)
from tests.assets.models.inheritance import (
    BaseModelWithValidator,
    BaseWithModelValidator,
    ChildModelOverrideValidator,
    ChildModelSimple,
    ChildModelWithOwnValidator,
    ChildWithInheritedModelValidator,
    GrandchildModel,
)
from tests.assets.models.nested import Address, Company, Person, RecursiveModel
from tests.assets.models.sqlmodel_models import (
    Hero,
    HeroCreate,
    HeroRead,
    HeroReadWithTeam,
    HeroUpdate,
    Team,
)
from tests.assets.models.validators import (
    BeforeValidator,
    ModelValidatorAfter,
    ModelValidatorBefore,
    MultiFieldValidator,
    SingleFieldValidator,
)
