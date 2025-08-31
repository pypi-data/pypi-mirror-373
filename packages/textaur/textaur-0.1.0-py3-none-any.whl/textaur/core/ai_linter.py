"""AI Linter class for linting text using OpenAI

Uses OpenAI to lint text. Can be initialized with an API key or will look for
one in the environment.
"""

from dotenv import load_dotenv
import openai
import os
import asyncio
from typing import Optional

# OPEN AI VARIABLES
OPENAI_API_KEY_NAME="OPENAI_API_KEY"
LINTING_MODEL="gpt-5-mini"

class AILinter:
    """AI Linter class for linting text using OpenAI"""
    def __init__(self, api_key: Optional[str]=None):
        """Initialize the AI Linter with an optional API key"""
        if not openai.api_key:
            if api_key:
                key = api_key
            else:
                load_dotenv()
                key = os.getenv(OPENAI_API_KEY_NAME)
            if not key:
                raise ValueError(f"No api key provided. No value found in env for key \"{OPENAI_API_KEY_NAME}\"")
            openai.api_key = key


    def remove_backticks(self, text: str) -> str:
        """
        Removes leading and trailing triple backticks from the text. If the text
        doesn't start or end with triple backticks, it returns the text as is.

        :param text
        Text to remove backticks from.
        """
        # in case of extra new lines or spacing
        stripped = text.strip()
        start = 3 if stripped.startswith("```") else 0
        end = -3 if stripped.endswith("```") else len(stripped)

        # add double new line at the end to ensure that linted chunks that get
        # concatenated together have blank lines between them
        return f"{stripped[start:end]}\n\n"


    def get_message(self, role: str, prompt: str) -> dict:
        """
        Returns a message dictionary for the OpenAI chat completion API.

        :param role
        Role of the message ("system" or "user").

        :param prompt
        Content of the message.
        """
        if role != "system" and role != "user":
            raise ValueError("role must be either 'system' or 'user'")
        return {
            "role": role,
            "content": prompt,
        }


    async def make_request(self, model: str, messages: list) -> str:
        """
        Makes a request to the OpenAI chat completion API.

        :param model
        Model to use for the request.

        :param messages
        List of messages to send to the API.
        """
        client = openai.AsyncOpenAI()
        completion = await client.chat.completions.create(
            model=model,
            messages=messages
        )
        obj = completion.choices[0]
        res = obj.message.content
        return self.remove_backticks(res)


    async def lint_text(self, text: str, linting_prompt: str) -> str:
        """
        Lints the given text using the OpenAI chat completion API.

        :param text
        Text to lint.

        :param linting_prompt
        Prompt to use for linting (ie, the system message).
        """
        return await self.make_request(
            LINTING_MODEL,
            [
                self.get_message("system", linting_prompt),
                self.get_message("user", f"Please clean up the following text: \n\n{text}"),
            ]
        )

    async def batch_lint_texts(
        self,
        texts: list[str],
        linting_prompt: str,
    ) -> list[str]:
        """
        Lints the given texts in parallel using the OpenAI chat completion API.

        :param texts
        List of texts to lint.

        :param linting_prompt
        Prompt to use for linting (ie, the system message).
        """
        res = [self.lint_text(text, linting_prompt) for text in texts]
        return await asyncio.gather(*res)
