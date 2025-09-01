from typing import List, Dict, Any
from enum import Enum
import uuid
from .models import DictFieldMapping, MatchType

def _convert_dict_mappings_to_dict(mappings: List['DictFieldMapping']) -> List[Dict]:
    """Convert DictFieldMapping objects to dictionaries."""
    if mappings is None:
        return None

    result = []
    for mapping in mappings:
        if hasattr(mapping, 'dict_key') and hasattr(mapping, 'match_condition'):
            mapping_dict = {
                'dict_key': mapping.dict_key,
                'match_condition': convert_config_to_dict(mapping.match_condition)
            }
            if hasattr(mapping, 'target_field') and mapping.target_field is not None:
                mapping_dict['target_field'] = mapping.target_field
            result.append(mapping_dict)
        else:
            # Handle case where mapping is already a dictionary
            result.append(mapping)

    return result

def convert_config_to_dict(obj: Any) -> Any:
    """Recursively convert configuration objects to JSON-serializable dictionaries."""
    if obj is None:
        return None

    if isinstance(obj, Enum):
        return obj.value

    if isinstance(obj, uuid.UUID):
        return str(obj)

    if isinstance(obj, list):
        return [convert_config_to_dict(item) for item in obj]

    if hasattr(obj, 'filter_linked_entities_results') and hasattr(obj, 'quick_creation_config') and hasattr(obj, 'quick_linking_config') and hasattr(obj, 'llm_linking_config'):
        return {
            'filter_linked_entities_results': convert_config_to_dict(obj.filter_linked_entities_config),
            'quick_creation_config': convert_config_to_dict(obj.quick_creation_config),
            'quick_linking_config': convert_config_to_dict(obj.quick_linking_config),
            'llm_linking_config': convert_config_to_dict(obj.llm_linking_config),
            'llm_top_k': obj.llm_top_k
        }

    if hasattr(obj, 'conditions') and type(obj).__name__ == 'AndCondition':
        return {
            'type': 'AND',
            'conditions': convert_config_to_dict(obj.conditions)
        }

    if hasattr(obj, 'conditions') and type(obj).__name__ == 'OrCondition':
        return {
            'type': 'OR',
            'conditions': convert_config_to_dict(obj.conditions)
        }

    # Handle DictFieldMapping class using the dedicated function
    if hasattr(obj, 'dict_key') and hasattr(obj, 'match_condition'):
        return _convert_dict_mappings_to_dict([obj])[0]

    if hasattr(obj, 'field') and hasattr(obj, 'condition'):
        field_dict = {
            'type': 'FIELD',
            'field': obj.field,
            'condition': convert_config_to_dict(obj.condition)
        }
        if hasattr(obj, 'source_field') and obj.source_field is not None:
            field_dict['source_field'] = obj.source_field
        # Handle dict_mappings using the dedicated function
        if hasattr(obj, 'dict_mappings') and obj.dict_mappings is not None:
            field_dict['dict_mappings'] = _convert_dict_mappings_to_dict(
                obj.dict_mappings)
        return field_dict

    if hasattr(obj, 'match_type') and isinstance(obj.match_type, MatchType):
        match_dict = {
            'match_type': convert_config_to_dict(obj.match_type)
        }
        if hasattr(obj, 'threshold') and obj.threshold is not None:
            match_dict['threshold'] = obj.threshold
        if hasattr(obj, 'weight') and obj.weight is not None:
            match_dict['weight'] = obj.weight
        return match_dict

    if isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, dict):
        return {k: convert_config_to_dict(v) for k, v in obj.items()}

    if hasattr(obj, '__dict__'):
        return {k: convert_config_to_dict(v) for k, v in obj.__dict__.items()
                if not k.startswith('_')}

    return str(obj)
