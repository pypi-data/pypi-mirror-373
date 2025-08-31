from ollama import chat

from terminal_buddy.utils.config import config
from terminal_buddy.utils.prompts import BASIC_COMMAND_PROMPT_TEMPLATE


def get_terminal_command(user_query, mmr_prompt_template):
    messages = [
        {
            "role":"system",
            "content": BASIC_COMMAND_PROMPT_TEMPLATE
        },
        {
            "role": "user",
            "content": mmr_prompt_template.format(user_query=user_query)
        }
    ]

    return chat(config.OLLAMA_MODEL_NAME, messages=messages,think=False, options={"temperature":0.0}).message.content