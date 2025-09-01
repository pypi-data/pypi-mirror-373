from typing import List, Optional, Union
from enum import Enum
from dataclasses import dataclass


class MatchType(Enum):
    """Enum for different types of matching conditions"""
    STRICT_MATCH = "m"
    STRICT_MATCH_LIST = "ml"
    LEXICAL_SIMILARITY = "ls"
    LEXICAL_SIMILARITY_LIST = "lsl"
    SEMANTIC_SIMILARITY = "ss"
    SEMANTIC_SIMILARITY_LIST = "ssl"
    DICT_MATCH = "dm"  # New match type for dictionary matching


@dataclass
class MatchCondition:
    """Class representing a match condition for a field"""
    match_type: MatchType
    threshold: Optional[float] = None  # Required for similarity conditions
    # Weight for lexical similarity and semantic similarity
    weight: Optional[float] = None

    def __post_init__(self):
        # Validate that threshold is provided for similarity conditions
        similarity_types = [
            MatchType.LEXICAL_SIMILARITY,
            MatchType.LEXICAL_SIMILARITY_LIST,
            MatchType.SEMANTIC_SIMILARITY,
            MatchType.SEMANTIC_SIMILARITY_LIST
        ]

        if self.match_type in similarity_types and self.threshold is None:
            raise ValueError(
                f"Threshold must be provided for {self.match_type.value}")

        if self.match_type not in similarity_types and self.threshold is not None and self.match_type != MatchType.DICT_MATCH:
            raise ValueError(
                f"Threshold should not be provided for {self.match_type.value}")


@dataclass
class DictFieldMapping:
    """Class representing a mapping for a dictionary field to target field"""
    dict_key: str  # The key in the dictionary
    match_condition: MatchCondition  # Match condition for this key
    # Target field to match against, if None, match against same key in target dict
    target_field: Optional[str] = None


@dataclass
class FieldCondition:
    """Class representing a condition for a single field"""
    field: str  # The field to check
    condition: MatchCondition
    source_field: Optional[str] = None  # The field to check against
    dict_mappings: Optional[List[DictFieldMapping]
                            ] = None  # For dictionary fields


@dataclass
class AndCondition:
    """Class representing AND condition between field conditions"""
    conditions: List[Union["AndCondition", "OrCondition", FieldCondition]]


@dataclass
class OrCondition:
    """Class representing OR condition between field conditions"""
    conditions: List[Union[AndCondition, "OrCondition", FieldCondition]]


@dataclass
class EntityLinkingConfig:
    """Configuration for entity linking"""
    quick_creation_config: Union[AndCondition, OrCondition, FieldCondition]
    quick_linking_config: Union[AndCondition, OrCondition, FieldCondition]
    llm_linking_config: Optional[Union[AndCondition, OrCondition, FieldCondition]] = None
    llm_top_k: int = 5