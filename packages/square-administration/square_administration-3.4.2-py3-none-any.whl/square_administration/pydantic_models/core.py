from typing import Optional, List

from pydantic import BaseModel, Field
from square_database_structure.square.greeting.tables import Greeting


class GetAllGreetingsV0(BaseModel):
    order_by: List[str] = Field(
        default_factory=lambda: [f"-{Greeting.greeting_datetime.name}"]
    )
    limit: Optional[int] = None
    offset: int = 0
