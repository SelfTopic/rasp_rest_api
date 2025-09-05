from dotenv import load_dotenv
import os

load_dotenv()

class Config:

    secret_key = os.environ.get("SECRET_KEY")

    def __init__(self) -> None:
        if not self.secret_key:
            raise ValueError("Secret key is not found in env file")
        
config = Config()

__all__ = ["config"]