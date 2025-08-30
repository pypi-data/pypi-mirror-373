from typing import Optional

from pydantic import BaseModel


class CreateAnonymousGreetingV0(BaseModel):
    greeting_anonymous_sender_name: Optional[str] = None
    greeting_text: Optional[str] = None
