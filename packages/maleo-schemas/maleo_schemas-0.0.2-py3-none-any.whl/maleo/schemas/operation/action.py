from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar


OperationActionT = TypeVar("OperationActionT", bound=Optional[BaseModel])


class OperationActionMixin(BaseModel, Generic[OperationActionT]):
    action: OperationActionT = Field(..., description="Action.")
