from enum import Enum
from typing import Literal, NewType, Self

from pydantic import BaseModel, model_validator

from enpi_api.l1 import openapi_client
from enpi_api.l2.types.clone import CloneId
from enpi_api.l2.types.collection import CollectionId
from enpi_api.l2.types.sequence import SequenceId
from enpi_api.l2.types.tag import TagId, TagValue
from enpi_api.l2.util.from_raw_model import FromRawModel

FilterId = NewType("FilterId", str)
"""The unique identifier of a filter."""


class OperatorType(str, Enum):
    """Type of an operator that is used in filter conditions."""

    AND = "and"
    OR = "or"


class Operator(BaseModel):
    """Operator used in filter conditions."""

    type: Literal["operator"] = "operator"
    """Internal type used by filters to determine what part of `Condition` this object is."""
    operator: OperatorType
    """Type of the operator."""
    conditions: list["NestedCondition"]
    """A list of conditions."""


class MatchIdTarget(str, Enum):
    """Target level of an ID match."""

    COLLECTION = "collection"
    CLONE = "clone"
    SEQUENCE = "sequence"


class MatchId(BaseModel):
    """Filters results down to the ones that
    have ID matching the one provided (single)."""

    type: Literal["match_id"] = "match_id"
    """Internal type used by filters to determine what part of `Condition` this object is."""
    target: MatchIdTarget
    """Target level of an ID match."""
    id: CollectionId | CloneId | SequenceId
    """Target ID value."""


class MatchIds(BaseModel):
    """Filters results down to the ones that
    have IDs matching the ones provided (many)."""

    type: Literal["match_ids"] = "match_ids"
    """Internal type used by filters to determine what part of `Condition` this object is."""
    target: MatchIdTarget
    """Target level of an ID match."""
    ids: list[CollectionId] | list[CloneId] | list[SequenceId]
    """Target ID values."""


class MatchTagRuleType(str, Enum):
    """Rule type for the `MatchTagRule` object."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    GREATER_THAN = "greater_than"
    SMALLER_THAN = "smaller_than"
    IS_BLANK = "is_blank"
    IS_NOT_BLANK = "is_not_blank"


class MatchTagRule(BaseModel):
    """Determines the tag value used for filtering down results via `MatchTag`."""

    type: MatchTagRuleType
    """Rule type for the `MatchTagRule` object."""
    value: TagValue | None
    """Tag value used for matching."""

    @model_validator(mode="after")
    def ensure_value_if_needed(self) -> Self:
        """@private"""
        if self.type not in {MatchTagRuleType.IS_BLANK, MatchTagRuleType.IS_NOT_BLANK}:
            if self.value is None:
                raise ValueError(f"Value must be provided for rule {self.type}")
        return self


class MatchTag(BaseModel):
    """Filters results down to the ones that
    have a given tag value matching the one provided."""

    type: Literal["match_tag"] = "match_tag"
    """Internal type used by filters to determine what part of `Condition` this object is."""
    tag_id: TagId
    """Target tag ID of a tag match."""
    rule: MatchTagRule
    """Determines the tag value used for filtering down results via `MatchTag`."""


class MatchCloneOperatorType(str, Enum):
    """Operator used in `MatchClone` filter conditions."""

    ANY_SEQUENCE = "any_sequence"
    EVERY_SEQUENCE = "every_sequence"


class MatchClone(BaseModel):
    """Filters results down to the ones that match the criteria applied
    to sequenes of a clone. In other words, it matches clones that have
    `all` or their sequences within meeting the filter criteria or have
    `any` of them meeting it (at least one), depending on the operator.

    Example:
        A match object that gets all clones that contain a heavy sequence (i.e. have at least
        one sequence with a `Heavy` chain tag value present):

    ```python
        match = MatchClone(
            operator=MatchCloneOperatorType.ANY_SEQUENCE,
            conditions=[
                MatchTag(
                    tag_id=SequenceTags.Chain,
                    rule=MatchTagRule(
                        type=MatchTagRuleType.EQUALS,
                        value="heavy",
                    ),
                )
            ],
        ),
    ```
    """

    type: Literal["match_clone"] = "match_clone"
    """Internal type used by filters to determine what part of `Condition` this object is."""
    operator: MatchCloneOperatorType
    """Operator used in `MatchClone` filter conditions."""
    conditions: list["Condition"]
    """The conditions that the either "any sequence" or "every sequence" must match. The conditions in this list are
    combined with an implicit "and" operator."""


Condition = MatchId | MatchIds | MatchTag | Operator
"""The condition of a filter.

The condition for a filter can contain either a singular condition, or an operator that combines multiple conditions.
These conditions can be nested as well.

An example filter that filters data from a specific collection, and only includes Heavy sequences:

```python
condition = Operator(
    operator=OperatorType.AND,
    conditions=[
        MatchId(
            target=MatchIdTarget.COLLECTION,
            id=CollectionId(1234)
        ),
        MatchTag(
            tag_id=SequenceTags.Chain,
            rule=MatchTagRule(
                type=MatchTagRuleType.EQUALS,
                value="Heavy"
            )
        )
    ]
)
```
"""

NestedCondition = Condition | MatchClone
"""A single entry present in `conditions` within `Operator` object."""


class Filter(FromRawModel[openapi_client.GetFilterSuccessResponse]):
    """A single filter object."""

    id: FilterId
    """The unique identifier of a filter."""
    version: int
    """Version of a filter."""
    name: str
    """Name of a filter."""
    shared: bool
    """Determines if a filter is visible to other users in the organization."""
    condition: Condition
    """Condition(s) applied by the filter."""

    @classmethod
    def _build(cls, raw: openapi_client.GetFilterSuccessResponse) -> "Filter":
        class ValidationHelper(BaseModel):
            condition: Condition

        return cls(
            id=FilterId(raw.id),
            version=int(raw.version),
            name=raw.name,
            shared=raw.shared or False,
            condition=ValidationHelper.model_validate(dict(condition=raw.condition.to_dict() if raw.condition is not None else None)).condition,
        )


class Template(BaseModel):
    """A template for a value in a templated filter."""

    type: Literal["template"] = "template"
    """Internal type used by filters to recognize the template."""
    key: str | None = None
    """The key of the column in the template file, if it differs from the default chosen key.

    In case of a `Template` being used in a `MatchTag` condition, the default key is the display name of the tag. For
    example, for the tag `SequenceTags.Cdr3AminoAcids`, the default key would be `CDR3 Amino Acids`. The display names
    for tags are documented.

    In case of a `Template` being used in a `MatchId` condition, the default key is the target of the match, in lowercase,
    suffixed with `_id`. For example, for a `MatchId` with target `collection`, the default key would be `collection_id`.
    """


class TemplatedMatchId(BaseModel):
    """Filters results down to the ones that
    have ID matching the ones provided in the template."""

    type: Literal["match_id"] = "match_id"
    """Internal type used by filters to determine what part of `TemplatedCondition` this object is."""
    target: MatchIdTarget
    """Target level of an ID match."""
    id: Template = Template()
    """A template for a value in the templated filter. If left empty, the key used for value
        matching from within template will be picked internally later on (see `Template`
        and `TemplatedCondition` for more info)."""


class MatchTagRuleEquals(BaseModel):
    """Determines the tag value used for filtering down results via `TemplatedMatchTag`."""

    type: Literal[MatchTagRuleType.EQUALS] = MatchTagRuleType.EQUALS
    """Rule type for the `MatchTagRule` object. Templated match tag rules can only be of type `equals`."""
    value: Template = Template()
    """A template for a value in the templated filter. If left empty, the key used for value
        matching from within template will be picked internally later on (see `Template`
        and `TemplatedCondition` for more info)."""


class TemplatedMatchTag(BaseModel):
    """Filters results down to the ones that
    have tag values matching the ones provided in the template."""

    type: Literal["match_tag"] = "match_tag"
    """Internal type used by filters to determine what part of `TemplatedCondition` this object is."""
    tag_id: TagId
    """Target tag ID of a templated tag match."""
    rule: MatchTagRuleEquals = MatchTagRuleEquals()
    """Templated match tag rules can only be of type equals, if the key does not need to be specified, a default can be used"""


class TemplatedAndOperator(BaseModel):
    """Operator used to define multiple conditions for templated
    filter that are linked with `AND` operators."""

    type: Literal["operator"] = "operator"
    """Internal type used by filters to determine what part of `TemplatedCondition` this object is."""
    operator: Literal[OperatorType.AND] = OperatorType.AND
    """Operator value, has to be `Operator.AND`."""
    conditions: list["NestedTemplatedCondition"]
    """A list of templated conditions."""


NestedTemplatedCondition = MatchId | TemplatedMatchId | MatchIds | TemplatedMatchTag
"""Nested conditions for the templated filter.

Templated filter does not allow another operator at the nested level, only conditions.
"""

TemplatedCondition = TemplatedAndOperator | NestedTemplatedCondition
"""The condition of a templated filter.

This filter can exclusively be used with the templated metadata importer.

The templated filter differs from the standard filter in that it allows templating of the values in matches. This allows
the filter to be used in conjunction with a CSV or DataFrame that contains the values to be matched on, as well as
one or more columns containing values to be added to the annotation target for those matches.

The templated filter has at most one level of nesting, only allows the `and` operator at the root level, and does not
allow any other matching rule than `equals` for tags.

Example of a templated filter where the collection name is templated:

```python
condition = TemplatedAndOperator(
    conditions=[
        TemplatedMatchTag(
            tag_id=CollectionTags.Name,
            # By omitting the template key, it uses the column with the header `Name` in the template file
        ),
    ]
)
```
This condition could then work with such an example template:
```
    Name, ExampleValue
    Collection 1, 123
    Collection 2, 456
    ...
```
which would apply metadata based on the `Name` column match. For example, all collections with `Collection 1`
name could (depending on the rest of filter and import configuration) have `123` value applied as
their `ExampleValue` tag. For more information on this functionality see templated metadata types
enpi_api.l2.types.import_metadata_templated and the metadata import api enpi_api.l2.client.api.collection_api.CollectionApi.add_metadata.
"""


class TemplatedFilter(FromRawModel[openapi_client.GetTemplatedFilterSuccessResponse]):
    """A single templated filter object."""

    id: FilterId
    """The unique identifier of a filter."""
    version: int
    """Version of a filter."""
    name: str
    """Name of a filter."""
    shared: bool
    """Determines if a filter is visible to other users in the organization."""
    condition: TemplatedCondition
    """Condition(s) applied by the templated filter."""

    @classmethod
    def _build(cls, raw: openapi_client.GetTemplatedFilterSuccessResponse) -> "TemplatedFilter":
        class ValidationHelper(BaseModel):
            condition: TemplatedCondition

        return cls(
            id=FilterId(raw.id),
            version=int(raw.version),
            name=raw.name,
            shared=raw.shared or False,
            condition=ValidationHelper.model_validate(dict(condition=raw.condition.to_dict() if raw.condition is not None else None)).condition,
        )
