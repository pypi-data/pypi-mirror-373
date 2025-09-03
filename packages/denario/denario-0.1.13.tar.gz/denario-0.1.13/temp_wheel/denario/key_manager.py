import os
from pydantic import BaseModel
from dotenv import load_dotenv

class KeyManager(BaseModel):
    ANTHROPIC: str = ""
    GEMINI: str = ""
    OPENAI: str = ""
    PERPLEXITY: str = ""

    def get_keys_from_env(self) -> None:

        load_dotenv()

        self.ANTHROPIC      = os.getenv("ANTHROPIC_API_KEY")
        # self.GEMINI         = os.getenv("GEMINI_API_KEY")
        self.GEMINI         = os.getenv("GOOGLE_API_KEY")
        self.PERPLEXITY     = os.getenv("PERPLEXITY_API_KEY")
        self.OPENAI         = os.getenv("OPENAI_API_KEY")

    def __getitem__(self, key: str) -> str:
        return getattr(self, key)

    def __setitem__(self, key: str, value: str) -> None:
        setattr(self, key, value)
