import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
        self.CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")
        self.CARTESIA_VOICE_ID = os.getenv(
            "CARTESIA_VOICE_ID", "79a125e8-cd45-4c13-8a67-188112f4dd22"
        )
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

        self._validate_keys()

    def _validate_keys(self):
        missing = []
        if not self.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not self.DEEPGRAM_API_KEY:
            missing.append("DEEPGRAM_API_KEY")
        if not self.CARTESIA_API_KEY:
            missing.append("CARTESIA_API_KEY")

        if missing:
            raise ValueError(
                f"Missing required environment variables in .env: {', '.join(missing)}"
            )


config = Config()