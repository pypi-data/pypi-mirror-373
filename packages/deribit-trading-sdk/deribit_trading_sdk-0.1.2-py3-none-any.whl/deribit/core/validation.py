from typing_extensions import TypeVar, Generic, Any, is_typeddict
from dataclasses import dataclass, field, is_dataclass
from .exc import ValidationError

T = TypeVar('T')

class validator(Generic[T]):

  def __init__(self, Type: type[T]):
    from pydantic import TypeAdapter, ConfigDict
    is_record = is_dataclass(Type) or is_typeddict(Type)
    if is_record and not hasattr(Type, '__pydantic_config__'):
      setattr(Type, '__pydantic_config__', ConfigDict(extra='allow'))
    self.adapter = TypeAdapter(Type)
    
  def json(self, data: str | bytes | bytearray) -> T:
    from pydantic import ValidationError as PydanticValidationError
    try:
      return self.adapter.validate_json(data)
    except PydanticValidationError as e:
      raise ValidationError from e

  def python(self, data: Any) -> T:
    from pydantic import ValidationError as PydanticValidationError
    try:
      return self.adapter.validate_python(data)
    except PydanticValidationError as e:
      raise ValidationError from e
    
  def __call__(self, data) -> T:
    if isinstance(data, str | bytes | bytearray):
      return self.json(data)
    else:
      return self.python(data)
