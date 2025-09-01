"""Entity Linker Client - A Python client for the Entity Linker service."""

from ._version import __version__, __version_info__
from .linker_client import EntityLinker
from .models import (
    EntityLinkingConfig, 
    AndCondition, 
    OrCondition, 
    FieldCondition, 
    MatchCondition, 
    MatchType, 
    DictFieldMapping
)
from .config import default_config

__author__ = "Godel Backend Team"
__email__ = "support@godel-ai.com"

__all__ = [
    "EntityLinker", 
    "EntityLinkingConfig", 
    "AndCondition", 
    "OrCondition", 
    "FieldCondition", 
    "MatchCondition", 
    "MatchType", 
    "DictFieldMapping",
    "default_config"
]
