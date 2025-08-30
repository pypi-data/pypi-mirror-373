from cachetools import cached
import inspect
from typing import List, Dict

from pydantic import BaseModel


@cached(cache={})
def get_fields_in_schema(cls: BaseModel) -> List[str]:
    fields = list(cls.__fields__.keys()) + _get_class_properties(cls)
    fields = _remove_protected_fields(fields)
    return fields


def _remove_protected_fields(fields):
    fields = [field for field in fields if not field.startswith('_')]
    fields = [field for field in fields if field != "model_fields_set"]
    fields = [field for field in fields if field != "model_extra"]
    return fields


def _get_class_properties(cls):
    properties = [
        member_name for member_name, member_object in inspect.getmembers(cls)
        if inspect.isdatadescriptor(member_object)
    ]
    return properties


class UnionParser:
    '''
    It took quite sometime to find this approach, the parser can be used across all pydantic versions.
    Synopsys:    parse a dict into a union of pydantic models and auto pick the model that can fit.
    Usage:       UnionParser[ModelA|ModelB].parse(<dict>)
    Description: There is no built-in method to parse a dict into a union of pydantic models. I figure 
    out it is the easiest to parse it into a container class that has a property of this union type.
    pydantic already supported this type of container class parsing. I searched all over internet and
    this approach is not mentioned anywhere. Either upgrading to pydantic_v2 or use a __root__ field
    was recommended in other places.
    Conceivably, this method can be used to parse any type into a pydantic model, but parse_obj_as
    from pydantic probably should be used for all cases that pydantic can natievly support parsing.
    '''
    def __class_getitem__(cls, union_type):
        class _UnionContainer(BaseModel):
            value: union_type

            @classmethod
            def parse(cls, value: Dict):
                return _UnionContainer(value=value).value

        return _UnionContainer
