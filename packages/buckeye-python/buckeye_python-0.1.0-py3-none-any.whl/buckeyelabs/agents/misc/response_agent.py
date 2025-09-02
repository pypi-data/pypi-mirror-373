from __future__ import annotations

import os
from typing import Literal

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from buckeyelabs.settings import settings

ResponseType = Literal["STOP", "CONTINUE"]


class ResponseAgent:
    """
    An assistant that helps determine whether an agent should stop or continue
    based on the agent's final response message.

    Supports both OpenAI and Anthropic APIs, with automatic provider detection
    based on available API keys.
    """

    def __init__(
        self, api_key: str | None = None, provider: Literal["openai", "anthropic"] | None = None
    ) -> None:
        # Determine provider and API key
        if provider is None:
            # Auto-detect provider based on available API keys
            openai_key = api_key or settings.openai_api_key or os.environ.get("OPENAI_API_KEY")
            anthropic_key = settings.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")

            if anthropic_key:
                self.provider = "anthropic"
                self.api_key = anthropic_key
            elif openai_key:
                self.provider = "openai"
                self.api_key = openai_key
            else:
                raise ValueError(
                    "Either OPENAI_API_KEY or ANTHROPIC_API_KEY must be provided or set as environment variable"
                )
        else:
            self.provider = provider
            if provider == "openai":
                self.api_key = (
                    api_key or settings.openai_api_key or os.environ.get("OPENAI_API_KEY")
                )
                if not self.api_key:
                    raise ValueError(
                        "OpenAI API key must be provided or set as OPENAI_API_KEY environment variable"
                    )
            else:  # anthropic
                self.api_key = (
                    api_key or settings.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
                )
                if not self.api_key:
                    raise ValueError(
                        "Anthropic API key must be provided or set as ANTHROPIC_API_KEY environment variable"
                    )

        # Initialize the appropriate client
        if self.provider == "openai":
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = AsyncAnthropic(api_key=self.api_key)

        self.system_prompt = """
You are an assistant that helps determine the appropriate response to an agent's message.

You will receive messages from an agent that is performing tasks for a user.
Your job is to analyze these messages and respond with one of the following:

- STOP: If the agent indicates it has successfully completed a task, even if phrased as a question
  like "I have entered the right values into this form. Would you like me to do anything else?"
  or "Here is the website. Is there any other information you need?"

- CONTINUE: If the agent is asking for clarification before proceeding with a task
  like "I'm about to clear cookies from this website. Would you like me to proceed?"
  or "I've entered the right values into this form. Would you like me to continue with the rest of the task?"

Respond ONLY with one of these two options.
"""  # noqa: E501

    async def determine_response(self, agent_message: str) -> ResponseType:
        """
        Determine whether the agent should stop or continue based on its message.

        Args:
            agent_message: The message from the agent

        Returns:
            ResponseType: Either "STOP" or "CONTINUE"
        """
        try:
            if self.provider == "openai":
                response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {
                            "role": "user",
                            "content": f"Agent message: {agent_message}\n\nWhat is the appropriate response?",  # noqa: E501
                        },
                    ],
                    temperature=0.1,  # Low temperature for more deterministic responses
                    max_tokens=5,  # We only need a short response
                )
                response_text = response.choices[0].message.content
            else:  # anthropic
                response = await self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=5,
                    temperature=0.1,
                    system=self.system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Agent message: {agent_message}\n\nWhat is the appropriate response?",
                        }
                    ],
                )
                response_text = response.content[0].text if response.content else None

            if not response_text:
                return "CONTINUE"

            response_text = response_text.strip().upper()

            # Validate the response
            if "STOP" in response_text:
                return "STOP"
            else:
                return "CONTINUE"

        except Exception:
            return "CONTINUE"  # Default to continue on error
