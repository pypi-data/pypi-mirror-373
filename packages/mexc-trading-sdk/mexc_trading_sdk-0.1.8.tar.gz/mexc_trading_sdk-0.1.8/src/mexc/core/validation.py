from typing_extensions import TypeVar, Generic, Any
from dataclasses import dataclass, field
from mexc.core.exc import ValidationError

T = TypeVar('T')

class validator(Generic[T]):

  def __init__(self, Type: type[T]):
    from pydantic import TypeAdapter
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

@dataclass
class ValidationMixin:
  default_validate: bool = field(default=True, kw_only=True)

  def validate(self, validate: bool | None) -> bool:
    return self.default_validate if validate is None else validate