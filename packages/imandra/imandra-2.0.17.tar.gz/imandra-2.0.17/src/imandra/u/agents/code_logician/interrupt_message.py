import uuid

from pydantic import BaseModel, Field


class InterruptMessage(BaseModel):
    agent: str = Field(description="Name of the agent")
    output: str = Field(
        description="Current output of the agent, providing context for feedback"
    )
    prompt: str = Field(description="Prompt used to ask for feedback")
    id: str = Field(default_factory=lambda _: str(uuid.uuid4()))
