import io
from typing import Any, Mapping
import deepmerge
from pydantic import BaseModel
from ruamel.yaml import CommentedMap, CommentedSeq, YAML


def merge_yaml(*args: dict) -> dict:
    if len(args) < 2:
        raise ValueError("At least two dictionaries are required for merging")

    for arg in args:
        if not isinstance(arg, dict):
            raise ValueError("All arguments must be dictionaries")

    base = args[0]
    for a in args[1:]:
        base = deepmerge.always_merger.merge(base, a)

    return base


def merge_yaml_strings(*args: str) -> dict:
    if len(args) < 2:
        raise ValueError("At least two dictionaries are required for merging")

    dicts = []
    yaml = YAML(typ='safe')
    for arg in args:
        try:
            data = yaml.load(arg)
            if not isinstance(data, dict):
                raise ValueError("All YAML strings must represent dictionaries")
            dicts.append(data)
        except Exception as e:
            raise ValueError(f"Error parsing YAML string: {e}")

    return merge_yaml(*dicts)


def merge_yaml_strings_return_str(*args: str) -> str:
    merged_dict = merge_yaml_strings(*args)
    yaml_serializer = YAML()
    yaml_serializer.default_flow_style = False
    yaml_serializer.preserve_quotes = True
    yaml_serializer.width = 4096

    stream = io.StringIO()
    yaml_serializer.dump(merged_dict, stream)
    return stream.getvalue()


def values_to_yaml(values_object: BaseModel,
                   top_level_comment: str,
                   yaml_serializer: YAML,
                   exclude_none=True,
                   exclude_defaults: bool = False,
                   exclude_unset: bool = False,
                   include: Mapping[str, Any] | set[str] | None = None,
                   exclude: Mapping[str, Any] | set[str] | None = None) -> str:
    def _to_commented_map(obj):
        if isinstance(obj, dict):
            cm = CommentedMap()
            for k, v in obj.items():
                cm[k] = _to_commented_map(v)
            return cm
        if isinstance(obj, list):
            cs = CommentedSeq()
            for v in obj:
                cs.append(_to_commented_map(v))
            return cs

        return obj

    def _add_field_comments(model: BaseModel, node: Any, count: int = 0) -> None:
        if not isinstance(node, CommentedMap):
            return

        fields = model.__class__.model_fields

        for name, field in fields.items():
            key = field.alias or name  # respect field alias
            if key in node and field.description:
                if '\n' in field.description or count == 0:
                    node.yaml_set_comment_before_after_key(key=key, before=field.description, indent=count * 2)
                else:
                    node.yaml_add_eol_comment(field.description, key=key)

            value = getattr(model, name, None)
            child_node = node.get(key)

            # Nested BaseModel
            if isinstance(value, BaseModel) and isinstance(child_node, CommentedMap):
                _add_field_comments(value, child_node, count + 1)

    """Export configuration to YAML string with optional comments"""
    data_dict = values_object.model_dump(
        by_alias=True,
        exclude_none=exclude_none,
        exclude_defaults=exclude_defaults,
        exclude_unset=exclude_unset,
        include=include,
        exclude=exclude)

    # Create comments
    data = _to_commented_map(data_dict)
    _add_field_comments(values_object, data)

    if top_level_comment != "":
        data.yaml_set_start_comment(top_level_comment)

    yaml_serializer.default_flow_style = False
    yaml_serializer.preserve_quotes = True
    yaml_serializer.width = 4096

    stream = io.StringIO()
    yaml_serializer.dump(data, stream)
    return stream.getvalue()
