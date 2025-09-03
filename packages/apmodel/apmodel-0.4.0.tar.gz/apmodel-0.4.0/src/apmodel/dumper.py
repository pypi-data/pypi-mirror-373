import json
from dataclasses import fields
from typing import Any, Dict

from .types import ActivityPubModel, Undefined
from .context import LDContext

def _serialize_model_to_json(model: ActivityPubModel) -> Dict[str, Any]:
    # Start with this object's context. Create a new instance to avoid modifying model._context.
    try:
        aggregated_context = model._context + LDContext()
    except AttributeError:
        aggregated_context = None

    data = {}
    # Manually iterate over the fields of this dataclass instance.
    # fields() correctly includes fields from parent and child classes.
    for f in fields(model):
        value = getattr(model, f.name)

        # Skip private fields and undefined values.
        if f.name.startswith('_') or isinstance(value, Undefined):
            continue

        # Recursively serialize nested ActivityPubModels.
        if isinstance(value, ActivityPubModel):
            # Aggregate context from the child model.
            child_json = value.to_json()
            if aggregated_context:
                if hasattr(value, '_context') and value._context:
                    aggregated_context = aggregated_context + value._context
                # Serialize the child, which will produce a dict.
                # The child's context is not needed since we aggregated it.
                child_json.pop("@context", None)
            data[f.name] = child_json
        elif isinstance(value, list):
            processed_list = []
            for item in value:
                if isinstance(item, ActivityPubModel):
                    child_json = item.to_json()
                    if aggregated_context:
                        if hasattr(item, '_context') and item._context:
                            aggregated_context = aggregated_context + item._context
                        child_json.pop("@context", None)
                    processed_list.append(child_json)
                else:
                    processed_list.append(item)
            data[f.name] = processed_list
        else:
            data[f.name] = value

    # Add the final, fully merged context and any extra properties.
    if aggregated_context:
        data["@context"] = aggregated_context.full_context
    if model._extra: # pyright: ignore[reportAttributeAccessIssue]
        data.update(model._extra) # pyright: ignore[reportAttributeAccessIssue]
        
    return data

def dump(model: ActivityPubModel, **kwargs) -> str:
    return json.dumps(model.to_json(), **kwargs)