import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ.get(
    "OPENAI_API_KEY"
)

OPENAI_MODEL = os.environ.get(
    "OPENAI_MODEL",
    "gpt-4o-mini",
)


if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY environment variable "
        "is not set"
    )