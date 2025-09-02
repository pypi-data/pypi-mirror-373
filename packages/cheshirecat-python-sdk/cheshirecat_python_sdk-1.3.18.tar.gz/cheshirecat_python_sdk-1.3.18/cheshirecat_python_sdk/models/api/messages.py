from pydantic import Field

from cheshirecat_python_sdk.models.dtos import MessageBase, Why


class MessageOutput(MessageBase):
    why: Why | None = Field(default_factory=Why)  # Assuming Why has a no-args constructor
    type: str | None = "chat"  # Default argument
    error: bool | None = False  # Default argument
    content: str = Field(init=False)  # Field without a default value

    def __init__(self, **data):
        super().__init__(**data)
        self.content = self.text
